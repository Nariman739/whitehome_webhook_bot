import os
import telebot
import openai
from flask import Flask, request

# Переменные окружения (заданы на Render)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# История сообщений по юзеру
chat_history = {}

# Flask приложение
app = Flask(__name__)

# Системный prompt для ChatGPT
PROMPT_SYSTEM = """
Ты — AI-консультант по натяжным потолкам компании White Home в Астане. Твоё имя - Бауыржан.
Общайся уважительно, по-человечески, но без лишних фраз. Не пиши "как я могу помочь" — сразу по делу.
Задавай вопросы, чтобы посчитать цену потолков:
- Какая площадь?
- Какой тип потолка по периметру (вставка, галтель, теневой, парящий)?
- Есть ли шторы (для подшторников)?
- Нужен ли багет?
- Сколько светильников и люстр?
В конце предложи бесплатный замер и спроси, когда удобно.
"""

# Корневая страница для проверки
@app.route('/')
def index():
    return 'WhiteHome bot работает!'

# Webhook — ОБЯЗАН совпадать с тем, что ты указал в Telegram API
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return 'ok', 200

# Ответ на /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Салем! Я Бауыржан из White Home. Напишите, пожалуйста, сколько квадратов потолков? 😊"
    )

# Обработка всех остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.chat.id
    user_input = message.text.strip()

    if user_id not in chat_history:
        chat_history[user_id] = [{"role": "system", "content": PROMPT_SYSTEM}]
    chat_history[user_id].append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=chat_history[user_id]
        )
        reply = response.choices[0].message.content.strip()
        bot.send_message(user_id, reply)
        chat_history[user_id].append({"role": "assistant", "content": reply})

        # Уведомить админа, если в тексте есть цифры (например, номер телефона)
        if any(c.isdigit() for c in user_input) and len(user_input) >= 9:
            bot.send_message(ADMIN_ID, f"🆕 Клиент написал: {user_input}")

    except Exception as e:
        bot.send_message(user_id, "Произошла ошибка. Попробуйте ещё раз позже.")
        bot.send_message(ADMIN_ID, f"Ошибка у клиента {user_id}: {e}")

# Запуск (локально не нужен, на Render — игнорируется gunicorn-ом)
if __name__ == "__main__":
    app.run()
