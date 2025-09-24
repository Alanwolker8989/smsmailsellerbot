import asyncio
import os
from aiogram import Bot, Dispatcher
from handlers import router
from dotenv import load_dotenv
from database import init_db

load_dotenv() 

bot = Bot(token=os.getenv("BOT_TOKEN")) 
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    init_db()
    asyncio.run(main())