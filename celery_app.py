from celery import Celery
from config import settings
REDIS_URL = f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0'
celery_instance = Celery('shop_tasks', broker=REDIS_URL, backend=REDIS_URL,include=['tasks'])
celery_instance.conf.update(task_track_started=True)