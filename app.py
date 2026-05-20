import os
import json
import logging
from flask import Flask, request, Response
import requests

# --- Настройки ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена!")

# URL твоего бота на Render (замени, если другой)
RENDER_URL = "https://dog-bot-8gvc.onrender.com"
WEBHOOK_URL = f"{RENDER_URL}/webhook"

logging.basicConfig(level=logging.INFO)

# --- Flask ---
app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)

def handle_update(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        if text == '/start':
            send_message(chat_id, "Привет! Я Пёсий бот, напиши что нибудь и я отвечу эхом")
        else:
            send_message(chat_id, f"Ты написал: {text}")

@app.route('/')
def index():
    return "✅ Бот Doge_foge_bot работает"

@app.route('/health')
def health():
    return "OK", 200

@app.route(f'/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if update:
            handle_update(update)
        return Response("OK", status=200)
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return Response("Error", status=500)
@app.route('/set_webhook')
def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
    r = requests.get(url)
    return r.json()

if __name__ == '__main__':
    # Устанавливаем вебхук
    resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
    logging.info(f"Webhook установлен: {resp.json()}")

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)