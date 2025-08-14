from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.task_service import generate_random_task, generate_task_with_ai
from app.services.response_service import get_responses_for_task, get_response
from app.services.vote_service import create_vote
from app.models.models import Task, Response, Vote

bp = Blueprint('main', __name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@bp.route('/')
def index():
    """Главная страница."""
    return render_template('index.html', title='MUTIL - Генератор заданий')

@bp.route('/api/tasks/generate', methods=['POST'])
def api_generate_task():
    """API эндпоинт для генерации задания."""
    db = next(get_db())
    try:
        # Получаем prompt из запроса 
        data = request.get_json() or {}
        prompt = data.get('prompt')
        
        # Генерируем задание
        if prompt:
            task_text = generate_task_with_ai(prompt)
        else:
            task_text = generate_random_task()
        
        # Создаем задание в БД
        task = Task(text=task_text)
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return jsonify({
            'id': task.id,
            'text': task.text
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@bp.route('/api/tasks/<int:task_id>')
def api_get_task(task_id):
    """API эндпоинт для получения задания."""
    db = next(get_db())
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            return jsonify({
                'id': task.id,
                'text': task.text
            })
        else:
            return jsonify({'error': 'Task not found'}), 404
    finally:
        db.close()

@bp.route('/api/responses', methods=['POST'])
def api_create_response():
    """API эндпоинт для создания ответа."""
    db = next(get_db())
    try:
        data = request.get_json() or {}
        task_id = data.get('task_id')
        text = data.get('text')
        
        if not task_id:
            return jsonify({'error': 'task_id is required'}), 400
            
        # Создаем ответ в БД
        response = Response(text=text, task_id=task_id)
        db.add(response)
        db.commit()
        db.refresh(response)
        
        return jsonify({
            'id': response.id,
            'text': response.text,
            'task_id': response.task_id
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@bp.route('/api/responses/task/<int:task_id>')
def api_get_responses_for_task(task_id):
    """API эндпоинт для получения ответов для задания."""
    db = next(get_db())
    try:
        responses = get_responses_for_task(db, task_id)
        return jsonify([{
            'id': r.id,
            'text': r.text,
            'task_id': r.task_id
        } for r in responses])
    finally:
        db.close()

@bp.route('/api/votes', methods=['POST'])
def api_create_vote():
    """API эндпоинт для голосования."""
    db = next(get_db())
    try:
        data = request.get_json() or {}
        response_id = data.get('response_id')
        value = data.get('value', 1)  
        
        if not response_id:
            return jsonify({'error': 'response_id is required'}), 400
            
        # Создаем голос в БД 
        vote = Vote(response_id=response_id, value=value, user_id=1)
        db.add(vote)
        db.commit()
        db.refresh(vote)
        
        # Обновляем рейтинг ответа
        from app.services.vote_service import update_response_score_cache
        update_response_score_cache(response_id, db)
        
        return jsonify({
            'id': vote.id,
            'response_id': vote.response_id,
            'value': vote.value
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()