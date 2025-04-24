from celery import Celery

from app.logger import logger
from app.sqlite_cache import init_db, mark_done
from app.tasks import classify_text_sync

init_db()

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",  # или что у тебя используется
    backend="redis://redis:6379/1",  # вот это критично!
)


@celery_app.task(name="classify_text")
def classify_text_task(text: str):
    level = classify_text_sync(text)["label"]
    mark_done(text, level)
    return level
