import os
from aiogram import Bot, Dispatcher, types
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

# Инициализация бота и диспетчера
TOKEN = os.getenv("BOT_TOKEN", "8977128124:AAFtlQj5f08BR94kd2_WCNwX0FXMq8Fo0h4")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем приложение FastAPI
app = FastAPI()

# Подключаем папку templates для рендеринга HTML-страниц
templates = Jinja2Templates(directory="templates")


# Главная страница (отдает index.html)
@app.get("/")
async def index(request: Request):
  return templates.TemplateResponse("index.html", {"request": request})


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
