from aiogram import Router


def get_buttons_router() -> Router:
    from logic.bot.buttons import (back, change_task_deadline,
                                   change_task_text, delete_deadlines,
                                   delete_only_task, new_deadline,
                                   show_deadlines, tick_task)

    router = Router()
    router.include_router(new_deadline.router)
    router.include_router(back.router)
    router.include_router(delete_deadlines.router)
    router.include_router(show_deadlines.router)
    router.include_router(tick_task.router)
    router.include_router(delete_only_task.router)
    router.include_router(change_task_text.router)
    router.include_router(change_task_deadline.router)

    return router
