import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Настройки
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена!")

logging.basicConfig(level=logging.INFO)

# Flask для "живости" сервера
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "✅ Бот работает"

@flask_app.route('/health')
def health():
    return "OK", 200

# === Обработчики команд ===
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я работаю на Render 24/7")

async def echo(update: Update, context):
    user_text = update.message.text
    await update.message.reply_text(f"Ты сказал: {user_text}")

# === Точка входа ===
if __name__ == '__main__':
    # Создаём приложение бота
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота в polling-режиме (в фоне)
    app.run_polling()

    # Flask сервер для Render (обязательно)
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port)