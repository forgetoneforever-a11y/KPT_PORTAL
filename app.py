import os
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

# Инициализация бота и диспетчера
TOKEN = os.getenv("BOT_TOKEN", "8977128124:AAFtlQj5f08BR94kd2_WCNwX0FXMq8Fo0h4")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ДОБАВЛЯЕМ ОБРАБОТЧИК КОМАНДЫ /START ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я твой бот-помощник для учебы. 📚\nИспользуй кнопки ниже для быстрого доступа:"
    )

# Указываем ваш публичный URL на Render
WEBHOOK_URL = f"https://kpt-portal.onrender.com/webhook/{TOKEN}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Автоматически регистрируем вебхук в Telegram при запуске сервера
    await bot.set_webhook(WEBHOOK_URL)
    yield
    # Очищаем вебхук при выключении
    await bot.delete_webhook()

# Создаем приложение FastAPI с поддержкой lifespan
app = FastAPI(lifespan=lifespan)

# Подключаем папку templates для рендеринга HTML-страниц
templates = Jinja2Templates(directory="templates")


# Главная страница (отдает index.html)
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


# Вебхук для Telegram бота
@app.post(f"/webhook/{TOKEN}")
async def telegram_webhook(request: Request):
  try:
    # Получаем JSON-данные от Telegram асинхронно
    json_data = await request.json()

    # Превращаем в объект апдейта aiogram и передаем в диспетчер
    update = types.Update.model_validate(json_data, context={"bot": bot})
    await dp.feed_update(bot, update)

    return {"status": "ok"}
  except Exception as e:
    print(f"Error handling webhook: {e}")
    return JSONResponse(status_code=500, content={"error": str(e)})


# Код для запуска локально (на Render запуск пойдет через Uvicorn)
if __name__ == "__main__":
  import uvicorn

  port = int(os.getenv("PORT", 10000))
  uvicorn.run("app:app", host="0.0.0.0", port=port)
