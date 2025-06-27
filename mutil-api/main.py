# mutil-api/main.py
import os
import random
import asyncio
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from llm_service import generate_task_with_llm
from telegram_service import create_telegram_app, configure_telegram_handlers 
app = FastAPI(
    title="MUTIL API Service",
    description="API for generating absurd tasks and integrating with Telegram bot.",
    version="1.0.0"
)

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
webhook_url = os.getenv("WEBHOOK_URL")

# Инициализация Telegram Bot Application
telegram_app = None
if telegram_token:
    # Создаем экземпляр Application
    telegram_app = create_telegram_app(token=telegram_token)
    # Конфигурируем обработчики для бота 
    configure_telegram_handlers(telegram_app)
else:
    print("TELEGRAM_BOT_TOKEN не найден. Telegram-бот не будет настроен.")


DUMMY_TASKS = [
    "Напиши оду пылесосу.",
    "Изобрази звук фиолетового цвета.",
    "Возьми интервью у своего левого ботинка.",
    "Построй башню из кубиков сахара, которая выше твоего роста.",
    "Создай новое приветствие для инопланетных гостей."
]

@app.on_event("startup")
async def on_startup():
    """Действия при запуске FastAPI приложения."""
    if telegram_app and webhook_url:
        print(f"Попытка установить вебхук для Telegram на: {webhook_url}")
        try:
            success = await telegram_app.bot.set_webhook(url=webhook_url, drop_pending_updates=True)
            if success:
                print("Вебхук Telegram установлен успешно!")
            else:
                print("Не удалось установить вебхук Telegram! Проверьте WEBHOOK_URL и TELEGRAM_BOT_TOKEN.")
        except Exception as e:
            print(f"Ошибка при установке вебхука Telegram: {e}")
    else:
        print("Вебхук Telegram не будет установлен (TELEGRAM_BOT_TOKEN или WEBHOOK_URL отсутствует).")

@app.get("/generate-task")
async def get_generated_task():
    task = await generate_task_with_llm()
    if task:
        return {"task": task}
    else:
        print("LLM не сгенерировала задание. Возвращаем задание-заглушку.")
        return {"task": random.choice(DUMMY_TASKS)}

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if not telegram_app:
        print("Получен вебхук Telegram, но бот не настроен.")
        raise HTTPException(status_code=500, detail="Telegram Bot not configured")
    
    try:
        # Получаем тело запроса как JSON
        body = await request.json()
        # Создаем объект Update из полученного JSON
        update = Update.de_json(body, telegram_app.bot) 
        asyncio.create_task(telegram_app.process_update(update))
        
        return {"status": "ok"}
    except Exception as e:
        print(f"Ошибка обработки вебхука Telegram: {e}")
        return {"status": "error", "message": str(e)}, 200 

@app.get("/")
def read_root():
    """Корневой эндпоинт API."""
    return {"service": "MUTIL API is running", "version": app.version}

@app.on_event("shutdown")
async def on_shutdown():
    """Действия при завершении работы FastAPI приложения."""
    if telegram_app and webhook_url: 
        print("Удаление вебхука Telegram...")
        try:
            success = await telegram_app.bot.delete_webhook()
            if success:
                print("Вебхук Telegram успешно удален.")
            else:
                print("Не удалось удалить вебхук Telegram.")
        except Exception as e:
            print(f"Ошибка при удалении вебхука Telegram: {e}")