from aiogram import Router


def get_routers() -> Router:
    from . import start_command

    router = Router()
    router.include_router(start_command.router)

    return router