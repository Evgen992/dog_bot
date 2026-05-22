import os
import json
import logging
from flask import Flask, request, Response
import requests
import requests

# Функция для общения с YandexGPT
def ask_yandex_gpt(user_message):
    # Бери эти значения из переменных окружения!
    folder_id = os.environ.get("FOLDER_ID")
    api_key = os.environ.get("YANDEX_API_KEY")
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 2000
        },
        "messages": [
            {
                "role": "user",
                "text": user_message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if 'result' in result:
            return result['result']['alternatives'][0]['message']['text']
        else:
            logging.error(f"YandexGPT error: {result}")
            return "Извини, что-то пошло не так..."
    except Exception as e:
        logging.error(f"YandexGPT exception: {e}")
        return "Ошибка подключения к нейросети 😢"

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

RENDER_URL = "https://dog-bot-8gvc.onrender.com"
WEBHOOK_URL = f"{RENDER_URL}/webhook"

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        logging.error(f"Send error: {e}")

def handle_photo(chat_id, file_id, file_size):
    send_message(chat_id, f"📸 Фото получено!\nРазмер: {file_size} байт")

def handle_help(chat_id):
    help_text = (
        "📋 Команды:\n"
        "/start — приветствие\n"
        "/help — эта справка\n\n"
        "📷 Отправь фото — я отвечу!"
    )
    send_message(chat_id, help_text)

def handle_update(update):
    try:
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            
            # Обработка фото (оставляем как есть)
            if 'photo' in update['message']:
                photo = update['message']['photo'][-1]
                file_id = photo['file_id']
                file_size = photo.get('file_size', 0)
                handle_photo(chat_id, file_id, file_size)
                return
            
            # Обработка текста
            text = update['message'].get('text', '')
            
            if text == '/start':
                send_message(chat_id, "Привет! Я Пёсий бот с ИИ 🐕\nЗадай мне любой вопрос!")
            elif text == '/help':
                handle_help(chat_id)
            else:
                # Если не команда — отвечаем через YandexGPT
                ai_response = ask_yandex_gpt(text)
                send_message(chat_id, ai_response)
                
    except Exception as e:
        logging.error(f"Update error: {e}")

@app.route('/')
def index():
    return "Бот работает", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if update:
            handle_update(update)
        return Response("OK", status=200)
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return Response("Error", status=500)

if __name__ == '__main__':
    # Установка вебхука
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
    try:
        resp = requests.get(url, timeout=10)
        logging.info(f"Webhook set: {resp.json()}")
    except Exception as e:
        logging.error(f"Webhook error: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)