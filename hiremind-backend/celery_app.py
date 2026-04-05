import sys
from pathlib import Path

from celery import Celery


ROOT_DIR = Path(__file__).resolve().parent
# Celery CLI can temporarily inject and later remove CWD from sys.path when loading
# the app. Always insert one explicit ROOT_DIR entry so it remains importable.
sys.path.insert(0, str(ROOT_DIR))

celery_app = Celery(
    "hiremind_backend",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["tasks.ai_tasks"],
)

celery_app.conf.task_routes = {
    "tasks.ai_tasks.*": {"queue": "ai_queue"}
}