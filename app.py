import os
import logging
from flask import Flask, request, Response
import requests

# Загружаем переменные окружения
TOKEN = os.environ.get("BOT_TOKEN")
FOLDER_ID = os.environ.get("FOLDER_ID")
YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY")

if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")
if not FOLDER_ID:
    raise ValueError("FOLDER_ID not set!")
if not YANDEX_API_KEY:
    raise ValueError("YANDEX_API_KEY not set!")

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        logging.error(f"Send error: {e}")

def ask_yandex_gpt(user_message):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 2000
        },
        "messages": [{"role": "user", "text": user_message}]
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
            if 'photo' in update['message']:
                photo = update['message']['photo'][-1]
                file_size = photo.get('file_size', 0)
                handle_photo(chat_id, photo['file_id'], file_size)
                return
            text = update['message'].get('text', '')
            if text == '/start':
                send_message(chat_id, "Привет! Я Пёсий бот с ИИ 🐕\nЗадай мне любой вопрос!")
            elif text == '/help':
                handle_help(chat_id)
            else:
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)