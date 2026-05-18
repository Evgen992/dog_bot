import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- 1. Настройки ---
# Загружаем токен бота из переменных окружения Render
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена!")

# Включаем логирование, чтобы видеть, что происходит
logging.basicConfig(level=logging.INFO)

# Создаем приложение Flask - это будет "веб-маячок" для Render
flask_app = Flask(__name__)

# --- 2. Логика бота (она знакомая)---
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот, который работает 24/7 на облачном сервере!")

async def echo(update: Update, context):
    user_text = update.message.text
    await update.message.reply_text(f"Ты сказал: {user_text}")

# --- 3. Функция запуска бота (в отдельном потоке)---
def run_bot():
    """Запускает polling-версию бота в фоновом режиме"""
    # Создаем "приложение" для бота
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запускаем бота (polling будет работать в этом же потоке)
    application.run_polling()

# --- 4. "Здоровье" веб-сервера (нужно для Render)---
@flask_app.route('/')
def index():
    return "Telegram бот запущен и работает!"

@flask_app.route('/health')
def health():
    return "OK", 200

# --- 5. Точка входа ---
if __name__ == '__main__':
    # Запускаем бота в отдельном потоке, чтобы Flask не блокировался
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем веб-сервер Flask
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port)