import os
import asyncio
import threading
from flask import Flask, render_template
from bot import dp, bot

app = Flask(__name__)

@app.route("/")
def index():
    # Flask ищет index.html в папке templates/
    return render_template("index.html")

def run_telegram_bot():
    """Функция для запуска бота в асинхронном цикле"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dp.start_polling(bot))

if __name__ == "__main__":
    # Запускаем Telegram-бота в фоновом потоке, чтобы он не мешал сайту
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Получаем порт от Render (или ставим 5000 по умолчанию для локального теста)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)