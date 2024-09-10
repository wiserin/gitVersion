import asyncio
from aiogram import Dispatcher
from app.handlers.main import main_router
from app.database.models import start_db
from bot import bot
from aiohttp import ClientConnectionError
from app.mailing import mailing



# Launching a bot, getting a token
async def main():
    start_db
    dp = Dispatcher()
    dp.include_router(main_router)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await asyncio.gather(mailing(), dp.start_polling(bot))
    except Exception as e:
        print(e)

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
