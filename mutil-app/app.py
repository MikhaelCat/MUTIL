# mutil-app/app.py
# mutil-app/app.py
import os
import requests
import random
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_migrate import Migrate
from models import db, Task, Submission # Убедитесь, что Task и Submission импортированы
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError # Для обработки ошибок уникальности при добавлении задания

load_dotenv()

# --- Предварительно заданные задания-заглушки ---
DUMMY_TASKS = [
    "Напиши письмо своему холодильнику.",
    "Сфотографируй свою тень в стиле нуар.",
    "Придумай национальный гимн для своей кошки.",
    "Нарисуй карту вымышленного острова, сделанного из завтрака.",
    "Сочини заклинание для вызова пиццы.",
]

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mutil.db') # Дефолт для разработки
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey') # Добавьте секретный ключ для безопасности сессий

    db.init_app(app)
    migrate = Migrate(app, db)

    # URL нашего API сервиса (FastAPI)
    # Используем имя сервиса 'api' из Docker Compose
    API_SERVICE_URL = os.getenv('API_SERVICE_URL', "http://api:8000") 

    @app.route('/')
    def index():
        """Главная страница приложения."""
        return render_template('index.html')

    @app.route('/gallery')
    def gallery():
        """Страница галереи ответов."""
        # Получаем все ответы, отсортированные по голосам
        submissions = Submission.query.order_by(Submission.votes.desc()).all()
        # Для каждого ответа подтягиваем текст задания
        gallery_data = []
        for submission in submissions:
            gallery_data.append({
                'id': submission.id,
                'task_text': submission.task.text, # Доступ к тексту задания через relation
                'content': submission.content,
                'votes': submission.votes,
                'created_at': submission.created_at.isoformat()
                # 'image_url': '...' # Если есть поддержка изображений, добавить сюда
            })
        return render_template('gallery.html', submissions=gallery_data)

    @app.route('/api/get-task', methods=['GET'])
    def get_task():
        """API-эндпоинт для получения случайного задания."""
        task_text = None
        try:
            # Пытаемся получить задание от LLM через наш FastAPI сервис
            response = requests.get(f"{API_SERVICE_URL}/generate-task", timeout=5) # Добавлен таймаут
            if response.status_code == 200:
                task_text = response.json().get("task")
                if not task_text: # Если API вернул пустой 'task'
                    raise ValueError("LLM API returned empty task text.")
                print(f"Задание получено от LLM API: {task_text}")
            else:
                print(f"LLM API вернул статус: {response.status_code}. Ответ: {response.text}")
                raise Exception(f"LLM API service error: Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"Ошибка подключения к LLM API по адресу {API_SERVICE_URL}. Возможно, сервис недоступен.")
            task_text = random.choice(DUMMY_TASKS)
        except requests.exceptions.Timeout:
            print(f"Таймаут при ожидании ответа от LLM API {API_SERVICE_URL}.")
            task_text = random.choice(DUMMY_TASKS)
        except Exception as e:
            print(f"Не удалось получить задание от LLM API, используем заглушку. Ошибка: {e}")
            task_text = random.choice(DUMMY_TASKS)
        
        # Сохраняем задание в БД, если оно новое
        # Используем first_or_404() или просто first()
        task = Task.query.filter_by(text=task_text).first()
        if not task:
            try:
                task = Task(text=task_text)
                db.session.add(task)
                db.session.commit()
                print(f"Новое задание сохранено в БД: {task.text}")
            except IntegrityError:
                # Если конкурирующий запрос уже добавил это задание
                db.session.rollback()
                task = Task.query.filter_by(text=task_text).first()
                print(f"Задание '{task_text}' уже существует в БД.")
            except Exception as e:
                db.session.rollback()
                print(f"Ошибка при сохранении нового задания в БД: {e}")
                # В случае ошибки сохранения, все равно возвращаем задание
                # В идеале, здесь можно взять другое задание из заглушек
                task = Task(text=task_text, id='temporary_id') # Для jsonify, если БД упала

        return jsonify({'id': task.id, 'text': task.text})

    @app.route('/api/submit', methods=['POST'])
    def submit():
        """API-эндпоинт для отправки ответа пользователя."""
        # Ожидаем JSON-данные, как отправляет фронтенд на JavaScript
        data = request.get_json() 
        task_id = data.get('task_id')
        content = data.get('content')

        if not task_id or not content:
            print("Ошибка: Отсутствуют task_id или content в запросе /api/submit")
            return jsonify({"error": "Missing task_id or content"}), 400
        
        # Проверяем, существует ли такое задание
        task = Task.query.get(task_id)
        if not task:
            print(f"Ошибка: Задание с ID {task_id} не найдено.")
            return jsonify({"error": "Task not found"}), 404

        try:
            new_submission = Submission(task_id=task_id, content=content) # Исправлено: task_id и content
            db.session.add(new_submission)
            db.session.commit()
            print(f"Новый ответ для задания {task_id} сохранен: {content[:50]}...")
            return jsonify({"message": "Submission successful", "submission_id": new_submission.id}), 201
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при сохранении ответа: {e}")
            return jsonify({"error": "Failed to save submission"}), 500

    @app.route('/api/submission/<int:submission_id>/vote', methods=['POST'])
    def vote(submission_id):
        """API-эндпоинт для голосования за ответ."""
        submission = Submission.query.get(submission_id) # Используем .get()
        if not submission:
            print(f"Ошибка: Ответ с ID {submission_id} не найден.")
            return jsonify({"error": "Submission not found"}), 404

        try:
            submission.votes += 1
            db.session.commit()
            print(f"Голос за ответ {submission_id} учтен. Новое количество голосов: {submission.votes}")
            return jsonify({'votes': submission.votes, 'message': 'Vote recorded successfully'})
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при голосовании за ответ {submission_id}: {e}")
            return jsonify({"error": "Failed to record vote"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    # С Flask-Migrate важно, чтобы контекст приложения был активен для команд Alembic.
    # В production вы будете использовать gunicorn или другой WSGI-сервер.
    # Для разработки `flask run` или `app.run()` подойдут.
    with app.app_context():
        db.create_all() # Создаем таблицы, если их нет. Это только для dev!
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True для разработки

    # mutil-app/app.py (только измененный @app.route('/api/submit'))
# ... (остальной код импортов и def create_app() остается прежним)

    @app.route('/api/submit', methods=['POST'])
    def submit():
        """API-эндпоинт для отправки ответа пользователя."""
        # Ожидаем form-data, как отправляет Telegram-бот (httpx.post(url, data=...))
        data = request.form
        task_id = data.get('task_id')
        content = data.get('content')
        author_info = data.get('author_info', 'Unknown User') # Добавлено для примера

        if not task_id or not content:
            print("Ошибка: Отсутствуют task_id или content в запросе /api/submit")
            return jsonify({"error": "Missing task_id or content"}), 400
        
        # Проверяем, существует ли такое задание
        task = Task.query.get(task_id) # Task.query.get() работает с Primary Key
        if not task:
            print(f"Ошибка: Задание с ID {task_id} не найдено.")
            return jsonify({"error": "Task not found"}), 404

        try:
            # Если у вас есть поле для автора в Submission, используйте его
            # Если нет, можно добавить. Пока просто сохраняем content
            new_submission = Submission(
                task_id=task_id, 
                content=content,
                # author_info=author_info # Если добавить это поле в модель Submission
            )
            db.session.add(new_submission)
            db.session.commit()
            print(f"Новый ответ для задания {task_id} сохранен: {content[:50]}... От {author_info}")
            # Возвращаем JSON-ответ, чтобы Telegram-бот мог его обработать
            return jsonify({"message": "Submission successful", "submission_id": new_submission.id}), 201
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при сохранении ответа: {e}")
            return jsonify({"error": "Failed to save submission"}), 500
