import asyncio
import logging

from aiogram.types import BotCommand

from logic.bot import bot, dp
from logic.db.init_db import init_db


async def main():
    await init_db()  # Проверяем/создаём БД перед запуском бота
    await bot.set_my_commands([BotCommand(command="start", description="Запуск бота")])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
