import os

from celery import Celery

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app = Celery('bot_tasks', broker=REDIS_URL)
app.conf.broker_connection_retry_on_startup = True
app.conf.worker_pool = 'solo'
app.conf.worker_concurrency = 1

import logic.queue.tasks

app.conf.beat_schedule = {
    'check-reminders-every-minute': {
        'task': 'logic.queue.tasks.check_reminders',
        'schedule': 60.0,  # Выполнять каждые 60 секунд
    },
    'prolonging-tasks-every-minute': {
        'task': 'logic.queue.tasks.prolonging_tasks',
        'schedule': 60.0,
    }
}
