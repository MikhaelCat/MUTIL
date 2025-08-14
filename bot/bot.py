import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import httpx
import os

# Конфигурация
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        '🎨 Привет! Я бот MUTIL - генератор безумных творческих заданий!\n\n'
        'Используй /random, чтобы получить случайное задание.\n'
        'Используй /top, чтобы увидеть топ работ.\n'
        'Используй /help, чтобы получить справку.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        'Команды бота:\n'
        '/random - получить случайное задание\n'
        '/top - топ лучших работ\n'
        '/help - справка'
    )

async def get_random_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /random"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_URL}/api/tasks/generate")
            
        if response.status_code == 200:
            data = response.json()
            task_text = data['text']
            task_id = data['id']
            
            
            keyboard = [
                [InlineKeyboardButton("👍", callback_data=f"vote_up_{task_id}")],
                [InlineKeyboardButton("👎", callback_data=f"vote_down_{task_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f'🎨 Твое задание:\n\n{task_text}',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text('Не удалось получить задание. Попробуйте позже.')
    except Exception as e:
        logger.error(f"Ошибка при получении задания: {e}")
        await update.message.reply_text('Произошла ошибка. Попробуйте позже.')

async def get_top_responses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /top"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/gallery/top")  
            
        if response.status_code == 200:
            data = response.json()
            if data:
                message = "🏆 Топ работ:\n\n"
                for i, item in enumerate(data[:5], 1):  
                    message += f"{i}. {item['text']}\n\n"
                await update.message.reply_text(message)
            else:
                await update.message.reply_text('Пока нет работ в топе.')
        else:
            await update.message.reply_text('Не удалось получить топ работ. Попробуйте позже.')
    except Exception as e:
        logger.error(f"Ошибка при получении топа: {e}")
        await update.message.reply_text('Произошла ошибка. Попробуйте позже.')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    # Разбираем callback_data
    data_parts = query.data.split('_')
    if len(data_parts) >= 3:
        action = data_parts[0]  
        direction = data_parts[1]  
        task_id = data_parts[2]    
        vote_value = 1 if direction == 'up' else -1
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/api/votes",
                    json={
                        "response_id": int(task_id),  
                        "value": vote_value
                    }
                )
            
            if response.status_code == 200:
                await query.edit_message_text(
                    text=f"Спасибо за ваш голос! {'👍' if vote_value > 0 else '👎'}"
                )
            else:
                await query.edit_message_text(
                    text="Не удалось зарегистрировать голос. Попробуйте позже."
                )
        except Exception as e:
            logger.error(f"Ошибка при голосовании: {e}")
            await query.edit_message_text(
                text="Произошла ошибка при голосовании. Попробуйте позже."
            )

def main():
    """Основная функция запуска бота"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("random", get_random_task))
    app.add_handler(CommandHandler("top", get_top_responses))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()