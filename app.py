import asyncio
import os
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

TOKEN = os.getenv("BOT_TOKEN", "8977128124:AAFtlQj5f08BR94kd2_WCNwX0FXMq8Fo0h4")
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  await message.answer(
      "Привет! Я твой бот-помощник для учебы. 📚\nИспользуй кнопки ниже для"
      " быстрого доступа:"
  )


WEBHOOK_URL = f"https://kpt-portal.onrender.com/webhook/{TOKEN}"


@asynccontextmanager
async def lifespan(app: FastAPI):
  # Устанавливаем вебхук при старте
  await bot.set_webhook(WEBHOOK_URL)
  print(f"Webhook set to: {WEBHOOK_URL}")
  yield
  # Удаляем вебхук при выключении
  await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
  return templates.TemplateResponse(request, "index.html")


@app.post(f"/webhook/{TOKEN}")
async def telegram_webhook(request: Request):
  try:
    json_data = await request.json()
    update = types.Update.model_validate(json_data, context={"bot": bot})

    # Запускаем обработку апдейта в фоновой задаче,
    # чтобы Telegram сразу получил ответ 200 OK и не ждал завершения всей логики бота
    asyncio.create_task(dp.feed_update(bot, update))

    return {"status": "ok"}
  except Exception as e:
    import traceback

    traceback.print_exc()
    return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
  import uvicorn

  port = int(os.getenv("PORT", 10000))
  uvicorn.run("app:app", host="0.0.0.0", port=port)
