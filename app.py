import os
import asyncio
from flask import Flask, render_template, request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN", "8977128124:AAFtlQj5f08BR94kd2_WCNwX0FXMq8Fo0h4")
WEB_APP_URL = os.getenv("RENDER_EXTERNAL_URL", "https://kpt-portal.onrender.com")

# Инициализация Flask и Dispatcher
app = Flask(__name__)
dp = Dispatcher()

# Настройка клавиатур
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🌐 Открыть сайт колледжа")
    builder.button(text="📅 Расписание на сегодня")
    builder.button(text="ℹ️ Помощь")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Сайт организатора", url=WEB_APP_URL)
    builder.button(text="🔔 Включить уведомления", callback_data="enable_notifications")
    builder.adjust(1)
    return builder.as_markup()

# Хендлеры бота
@dp.message(Command("start"))
async def start_command(message: types.Message):
    greeting = "Привет! Я твой бот-помощник для учебы. 📚"
    await message.answer(
        f"{greeting}\nИспользуй кнопки ниже для быстрого доступа:",
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda msg: msg.text == "🌐 Открыть сайт колледжа")
async def open_site_btn(message: types.Message):
    await message.answer(
        "Нажми на кнопку ниже, чтобы открыть портал:",
        reply_markup=get_inline_keyboard()
    )

@dp.message(lambda msg: msg.text == "📅 Расписание на сегодня")
async def schedule_btn(message: types.Message):
    await message.answer("📅 Твое расписание на сегодня:\n1. Технология машиностроения\n2. Инженерная графика\n3. Базы данных")

@dp.message(lambda msg: msg.text == "ℹ️ Помощь")
async def help_btn(message: types.Message):
    await message.answer("Я помогаю следить за учебой, присылаю уведомления и открываю доступ к сайту.")

@dp.callback_query(lambda query: query.data == "enable_notifications")
async def process_callback(callback: types.CallbackQuery):
    await callback.answer("Уведомления успешно включены! ✅", show_alert=True)
    await callback.message.edit_text("✅ Уведомления активированы для этого чата.")

@dp.message()
async def echo_message(message: types.Message):
    await message.answer(f"Я тебя услышал! Напиши /start, чтобы обновить меню.")


# --- Роуты Flask для сайта, вебхука и API заметок ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def telegram_webhook():
    """Создает изолированный контекст бота и сессии на каждый запрос от Telegram"""
    async def process_update():
        async with Bot(token=TOKEN) as local_bot:
            update = types.Update.model_validate(
                request.get_json(force=True), context={"bot": local_bot}
            )
            await dp.feed_update(local_bot, update)

    asyncio.run(process_update())
    return "OK", 200

@app.route("/api/send-note", methods=["POST"])
def send_note_to_telegram():
    """Принимает заметки/напоминания с сайта и пересылает их в Telegram"""
    data = request.get_json(force=True)
    chat_id = data.get("chat_id")
    note_text = data.get("text")
    
    if not chat_id or not note_text:
        return {"error": "Missing chat_id or text"}, 400

    async def send_msg():
        async with Bot(token=TOKEN) as local_bot:
            await local_bot.send_message(
                chat_id=chat_id, 
                text=f"🔔 **Напоминание / Заметка:**\n\n{note_text}"
            )

    try:
        asyncio.run(send_msg())
        return {"status": "success"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    # При старте автоматически регистрируем Webhook в Telegram
    import requests
    webhook_url = f"{WEB_APP_URL}/webhook/{TOKEN}"
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
    
    # Запускаем Flask-сервер
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
