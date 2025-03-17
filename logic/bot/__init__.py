from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from logic.bot.buttons import get_buttons_router
from logic.bot.commands import get_commands_router
from logic.bot.config import BOT_API_TOKEN

bot = Bot(token=BOT_API_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(get_commands_router())
dp.include_router(get_buttons_router())
