from aiogram import Router


def get_commands_router() -> Router:
    from logic.bot.commands import start_command

    router = Router()
    router.include_router(start_command.router)

    return router
