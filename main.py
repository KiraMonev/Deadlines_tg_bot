import asyncio
import logging

from aiogram import Bot, Dispatcher

from logic.bot import get_routers
from logic.config import BOT_API_TOKEN


async def main():
    bot = Bot(token=BOT_API_TOKEN)
    dp = Dispatcher()
    dp.include_router(get_routers())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
