from aiogram import Router


def get_buttons_router() -> Router:
    from logic.bot.buttons import (back, delete_deadlines, new_deadline,
                                   show_deadlines)

    router = Router()
    router.include_router(new_deadline.router)
    router.include_router(back.router)
    router.include_router(delete_deadlines.router)
    router.include_router(show_deadlines.router)

    return router
