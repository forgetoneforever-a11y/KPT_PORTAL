import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN", "8977128124:AAFtlQj5f08BR94kd2_WCNwX0FXMq8Fo0h4")

# Получаем URL сайта из переменных окружения на Render (или подставляем шаблон)
WEB_APP_URL = os.getenv("RENDER_EXTERNAL_URL", "https://college-organizer-bot.onrender.com")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    """Создает постоянные кнопки под клавиатурой чата"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🌐 Открыть сайт колледжа")
    builder.button(text="📅 Расписание на сегодня")
    builder.button(text="ℹ️ Помощь")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_inline_keyboard():
    """Создает Inline-кнопки прямо под сообщением"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Сайт организатора", url=WEB_APP_URL)
    builder.button(text="🔔 Включить уведомления", callback_data="enable_notifications")
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Убрали проверку ADMIN_ID, теперь приветствие универсальное для всех
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
