import os
import time

from celery import Celery

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PROTOCOL = os.environ.get("REDIS_PROTOCOL", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
BROKEN_URL_DB_INDEX = "2"
RESULT_BACKEND_DB_INDEX = "3"


celery = Celery(__name__)
celery.conf.broker_url = f"{REDIS_PROTOCOL}://{REDIS_HOST}:{REDIS_PORT}/{BROKEN_URL_DB_INDEX}"
celery.conf.result_backend = f"{REDIS_PROTOCOL}://{REDIS_HOST}:{REDIS_PORT}/{RESULT_BACKEND_DB_INDEX}"


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 2)
    return True

# scheduled tasks using celery beat
celery.conf.beat_schedule = {
    'test-period-task': {
        'task': 'create_task',
        'schedule': 10.0,
        'kwargs': {'task_type': '1'}
    }
}