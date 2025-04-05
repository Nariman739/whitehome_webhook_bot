
import telebot
import openai
import flask
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)
openai.api_key = OPENAI_API_KEY
app = flask.Flask(__name__)
chat_history = {}

PROMPT_SYSTEM = "Ты — AI-консультант White Home в Астане. Тебя зовут Бауыржан. Помогаешь клиенту рассчитать стоимость потолков. Вежливо общайся, веди к расчёту и замеру. Уведомляй владельца при получении номера или адреса."

@bot.message_handler(commands=['start'])
def greet(message):
    bot.send_message(message.chat.id, "Привет! Я Бауыржан из White Home. Сколько квадратов потолок?")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    user_id = message.chat.id
    user_text = message.text

    if user_id not in chat_history:
        chat_history[user_id] = [{"role": "system", "content": PROMPT_SYSTEM}]
    chat_history[user_id].append({"role": "user", "content": user_text})

    if any(x in user_text.lower() for x in ['номер', 'телефон', 'адрес', 'астана', 'улица', 'дом', '+7']):
        bot.send_message(OWNER_ID, f"📬 Новый контакт от @{message.from_user.username or 'неизвестно'}:\n\n{user_text}")

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=chat_history[user_id]
        )
        reply = response.choices[0].message.content
        bot.send_message(user_id, reply)
        chat_history[user_id].append({"role": "assistant", "content": reply})
    except Exception as e:
        bot.send_message(user_id, f"Ошибка: {e}")

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(flask.request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Не поддерживается', 403

@app.route('/', methods=['GET'])
def index():
    return "White Home Bot is running!"
