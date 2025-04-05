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

app = Flask(__name__)

PROMPT_SYSTEM = """
PROMPT_SYSTEM = """
Ты — AI-консультант по натяжным потолкам компании White Home в Астане. Твоё имя — Бауыржан. Общайся уважительно, по-человечески, но без лишних фраз. Не пиши "как я могу помочь" — сразу по делу.

Ты помогаешь рассчитать стоимость установки потолков. Уточняй:
- площадь потолков в м²
- тип потолка по периметру: вставка, галтель, теневой, парящий
- есть ли окна и нужны ли подшторники (если не вставка — переспроси)
- количество комнат (если нужно рассчитать длину подшторников)
- сколько люстр и софитов
- если площадь маленькая (ванна, балкон), уточни про **минимальный заказ 50 000 ₸**

Расчёт делай по правилам:

— Потолок: 2000 ₸/м²  
— Периметр = площадь × 1.3  
— Профиль вставка: 1000 ₸/п.м.  
— Багет (если вставка или галтель): 500 ₸/п.м.  
— Алюминиевый подшторник: 8000 ₸/м  
— Установка люстры: 5000 ₸/шт  
— Установка софита: 2500 ₸/шт  
— Длина подшторника = кол-во комнат × 3 м (если не указана)

Если выбрана вставка, теневой или парящий — профиль = алюминий, багет не нужен.

Никогда не делай расчёт, пока не получишь минимум:
— площадь
— тип потолка
— подшторники да/нет (если не вставка)

В конце расчёта всегда пиши:
"Это предварительный расчёт. Для точной стоимости лучше заказать бесплатный замер — мастер приедет и всё точно скажет. Когда было бы удобно провести замер?"
"""

"""

@app.route('/')
def index():
    return 'WhiteHome bot работает!'

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
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

        if any(c.isdigit() for c in user_input) and len(user_input) >= 9:
            bot.send_message(ADMIN_ID, f"🆕 Клиент написал: {user_input}")

    except Exception as e:
        bot.send_message(user_id, "Произошла ошибка. Попробуйте ещё раз позже.")
        bot.send_message(ADMIN_ID, f"Ошибка у клиента {user_id}: {e}")

if __name__ == "__main__":
    app.run()
