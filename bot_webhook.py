import os
import telebot
import openai
from flask import Flask, request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

chat_history = {}

# Flask приложение
app = Flask(__name__)

PROMPT_SYSTEM = """
Ты — AI-консультант White Home в Астане. Твоё имя — Бауыржан...
(сюда вставим полный промпт — как у нас был ранее)
"""

@app.route('/')
def index():
    return 'WhiteHome bot работает!'

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Салем! Я Бауыржан из White Home. Напишите, пожалуйста, сколько квадратов потолков? 😊")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.chat.id
    user_input = message.text

    if user_id not in chat_history:
        chat_history[user_id] = [{"role": "system", "content": PROMPT_SYSTEM}]
    chat_history[user_id].append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=chat_history[user_id]
        )
        reply = response.choices[0].message.content
        bot.send_message(user_id, reply)
        chat_history[user_id].append({"role": "assistant", "content": reply})

        # Уведомление админу, если есть номер телефона
        if any(c.isdigit() for c in user_input) and len(user_input) >= 9:
            bot.send_message(ADMIN_ID, f"🆕 Клиент написал: {user_input}")

    except Exception as e:
        bot.send_message(user_id, "Произошла ошибка. Попробуйте ещё раз позже.")
        bot.send_message(ADMIN_ID, f"Ошибка у клиента {user_id}: {e}")

# Запускаем Flask через gunicorn
if __name__ == "__main__":
    app.run()
