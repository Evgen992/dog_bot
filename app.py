import os
import json
import logging
from flask import Flask, request, Response
import requests

# --- Настройки ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена!")

# URL твоего бота на Render
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://dog-bot-8gvc.onrender.com')
WEBHOOK_URL = f"{RENDER_URL}/webhook"

logging.basicConfig(level=logging.INFO)

# --- Flask приложение ---
app = Flask(__name__)

# --- Функции для работы с Telegram API ---
def send_message(chat_id, text):
    """Отправляет сообщение пользователю"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Ошибка отправки: {e}")

# --- Основная логика бота ---
def handle_update(update):
    """Обрабатывает входящее обновление от Telegram"""
    try:
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            if text == '/start':
                send_message(chat_id, "Привет! Я бот, который работает на Render через Webhook 🚀")
            else:
                send_message(chat_id, f"Ты написал: {text}")
    except Exception as e:
        logging.error(f"Ошибка в handle_update: {e}")

# --- Эндпоинты для Render и Telegram ---
@app.route('/')
def index():
    return "✅ Бот Doge_foge_bot работает через Webhook!"

@app.route('/health')
def health():
    return "OK", 200

@app.route(f'/webhook', methods=['POST'])
def webhook():
    """Точка входа для сообщений от Telegram"""
    try:
        update = request.get_json()
        if update:
            handle_update(update)
        return Response("OK", status=200)
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return Response("Error", status=500)

# --- Точка входа ---
if __name__ == '__main__':
    # Устанавливаем вебхук для Telegram
    set_webhook_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
    try:
        response = requests.get(set_webhook_url, timeout=10)
        logging.info(f"Webhook установлен: {response.json()}")
    except Exception as e:
        logging.error(f"Ошибка установки вебхука: {e}")

    # Запускаем Flask сервер
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)