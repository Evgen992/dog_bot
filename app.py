import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# --- Настройки ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена!")

logging.basicConfig(level=logging.INFO)

# --- Flask приложение для "живучести" ---
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "✅ Бот Doge_foge_bot работает"

@flask_app.route('/health')
def health():
    return "OK", 200

# --- Функция для запуска бота (в отдельном потоке)---
def run_bot():
    # Создаём приложение бота
    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчики команд
    async def start(update: Update, context):
        await update.message.reply_text("Привет! Я работаю на Render 24/7 🚀")

    async def echo(update: Update, context):
        user_text = update.message.text
        await update.message.reply_text(f"Ты написал: {user_text}")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота (polling)
    print("🤖 Бот запущен и слушает сообщения...")
    app.run_polling()

# --- Точка входа ---
if __name__ == '__main__':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Запускаем Flask сервер (в главном потоке)
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port)