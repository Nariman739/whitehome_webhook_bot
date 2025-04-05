
# White Home Telegram Webhook Bot

📦 Как запустить на Render.com:

1. Перейди на https://render.com
2. Нажми "New → Web Service"
3. Подключи GitHub (можно залить ZIP в новый репозиторий)
4. Выстави настройки:
   - Environment: Python 3
   - Start Command: gunicorn bot_webhook:app
5. Добавь Environment Variables:
   - TELEGRAM_TOKEN = <твой токен>
   - OPENAI_API_KEY = <твой ключ>
   - ADMIN_ID = 499592803
6. После запуска скопируй URL вида `https://whitehome.onrender.com`
7. Установи Webhook:
   https://api.telegram.org/bot<твой_токен>/setWebhook?url=https://whitehome.onrender.com/<твой_токен>

🎉 Готово!
