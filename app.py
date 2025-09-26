import asyncio
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import router as handlers_router
from admin import router as admin_router, set_bot_instance
from database import init_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TG_ADMIN_IDS
import os
from dotenv import load_dotenv
import redis


load_dotenv()

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


init_db()


async def setup_admin_router():
    await set_bot_instance(bot)


dp.include_router(handlers_router)
dp.include_router(admin_router)

async def reset_limits():
    conn = sqlite3.connect("mail_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET limit_count = 5")
    conn.commit()
    conn.close()
    print("Лимиты сброшены!")

async def on_startup():
    await bot.send_message(chat_id=TG_ADMIN_IDS[0], text="Бот запущен и готов к работе!")

async def main():
    await setup_admin_router()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(reset_limits, 'interval', hours=24)  # Сбрасываем каждые 24 часа
    scheduler.start()

    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
