from aiogram import Router


def get_routers() -> Router:
    from logic.bot.buttons import get_buttons_router
    from logic.bot.commands import get_commands_router

    router = Router()
    router.include_router(get_commands_router())
    router.include_router(get_buttons_router())

    return router
