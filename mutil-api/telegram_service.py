# mutil-api/telegram_service.py
import logging
import os
import httpx 
from telegram import Update 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
from telegram.constants import ParseMode 


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

API_SERVICE_URL = os.getenv("API_SERVICE_URL", "http://api:8000")
FLASK_WEB_APP_URL = os.getenv("FLASK_WEB_APP_URL", "http://web:5000")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start."""
    await update.message.reply_text(
        "Привет! Я бот для генерации безумных заданий. Используй /gettask, чтобы начать.",
        parse_mode=ParseMode.HTML
    )

# Обработчик команды /gettask
async def get_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /gettask и получает задание от FastAPI API."""
    await update.message.reply_text("Придумываю для тебя безумное задание...", parse_mode=ParseMode.HTML)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_SERVICE_URL}/generate-task", timeout=10)
            response.raise_for_status() # Вызывает исключение для HTTP ошибок (4xx, 5xx)
            
            task_data = response.json()
            task_id = task_data.get("id") # Получаем ID задания
            task_text = task_data.get("text")
            
            if task_text and task_id:
                # Сохраняем ID и текст задания в контекст пользователя для последующей обработки ответа
                context.user_data['last_task_id'] = task_id
                context.user_data['last_task_text'] = task_text
                await update.message.reply_text(
                    f"Твое задание:\n\n<b>{task_text}</b>\n\n"
                    "Присылай свой ответ (текст или фото) в этот чат!",
                    parse_mode=ParseMode.HTML
                )
                logger.info(f"Выдано задание ID {task_id} пользователю {update.message.from_user.id}")
            else:
                await update.message.reply_text("Не могу придумать задание. Попробуй позже.")
                logger.warning(f"API вернул некорректные данные: {task_data}")
    except httpx.RequestError as e:
        logger.error(f"Ошибка HTTP-запроса к API '{API_SERVICE_URL}': {e}")
        await update.message.reply_text("К сожалению, не удалось связаться с сервисом заданий. Пожалуйста, попробуй позже.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при получении задания: {e}")
        await update.message.reply_text("Ой, что-то пошло не так на сервере :(")

# Обработчик текстовых и фото ответов
async def handle_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые ответы и ответы с фото."""
    last_task_id = context.user_data.get('last_task_id')
    last_task_text = context.user_data.get('last_task_text')

    if not last_task_id or not last_task_text:
        await update.message.reply_text("Сначала получи задание с помощью команды /gettask")
        return

    submission_content = ""
    # Если это текстовое сообщение
    if update.message.text:
        submission_content = update.message.text
    # Если это фото
    elif update.message.photo:
        # Получаем самое большое фото (последнее в списке)
        photo_file_id = update.message.photo[-1].file_id
        # Здесь вы можете скачать фото, если это нужно для галереи
        # Например: file = await context.bot.get_file(photo_file_id)
        # await file.download_to_drive(f'submissions/{photo_file_id}.jpg')
        submission_content = f"[Фото] {update.message.caption or 'Без подписи'}"
        logger.info(f"Получено фото-ответ для задания {last_task_id} от пользователя {update.message.from_user.id}")
    else:
        await update.message.reply_text("Пожалуйста, присылай ответ в виде текста или фотографии.")
        return

    # Собираем данные для отправки во Flask-приложение
    submission_data = {
        'task_id': last_task_id, # Передаем ID полученного задания
        'content': submission_content,
        'author_info': f"Telegram User @{update.message.from_user.username or update.message.from_user.id}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Flask-эндпоинт /api/submit ожидает form-data (application/x-www-form-urlencoded)
            # httpx.post(url, data=...) автоматически отправит как form-data
            submit_response = await client.post(
                f"{FLASK_WEB_APP_URL}/api/submit", 
                data=submission_data, # Отправляем как form-data
                timeout=10
            )
            submit_response.raise_for_status() # Вызывает исключение для HTTP ошибок

            # Flask /api/submit теперь возвращает JSON с сообщением и id, а не редирект
            response_json = submit_response.json()
            if submit_response.status_code == 201: # Успешное создание ресурса
                await update.message.reply_text("Отлично, твой ответ принят и отправлен в галерею!")
                context.user_data.pop('last_task_id', None) # Очищаем задание после ответа
                context.user_data.pop('last_task_text', None)
                logger.info(f"Ответ для задания {last_task_id} успешно отправлен в Flask API.")
            else:
                await update.message.reply_text(f"Не удалось сохранить ответ. Статус: {submit_response.status_code}. Ошибка: {response_json.get('error', 'Неизвестно')}")
                logger.error(f"Ошибка сохранения ответа в Flask API. Статус: {submit_response.status_code}, Ответ: {response_json}")

    except httpx.RequestError as e:
        logger.error(f"Ошибка HTTP-запроса к Flask API '{FLASK_WEB_APP_URL}': {e}")
        await update.message.reply_text("Не удалось сохранить твой ответ. Произошла сетевая ошибка.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при отправке ответа: {e}")
        await update.message.reply_text("Не удалось сохранить твой ответ. Произошла непредвиденная ошибка.")

# Функция для создания экземпляра Application
def create_telegram_app(token: str) -> Application:
    """Создает и возвращает экземпляр Application для Telegram бота."""
    application = Application.builder().token(token).build()
    return application

# Функция для настройки обработчиков (экспортируется для main.py)
def configure_telegram_handlers(application: Application):
    """Конфигурирует и добавляет обработчики команд и сообщений."""
    application.add_handler(CommandHandler("start", start_command)) # Имя функции изменено
    application.add_handler(CommandHandler("gettask", get_task_command)) # Имя функции изменено
    # Обработчик для текстовых сообщений, которые не являются командами, и для фото
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle_submission)) 
    logger.info("Обработчики Telegram бота сконфигурированы.")


# --- Тестовый блок для отладки (не будет выполняться при импорте) ---
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv() # Загружаем .env для локального тестирования
    
    # Для локального запуска бота (вместо вебхука)
    async def main():
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("TELEGRAM_BOT_TOKEN не установлен в .env для локального тестирования.")
            return

        application = create_telegram_app(token)
        configure_telegram_handlers(application) # Конфигурируем обработчики

        print("Запуск Telegram бота в режиме polling (для локального тестирования)...")
        # В режиме polling бот постоянно опрашивает сервер Telegram
        await application.run_polling(poll_interval=3)

    import asyncio
    asyncio.run(main())