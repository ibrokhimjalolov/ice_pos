from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "pos_system.settings"
django.setup()
from django.apps import apps
from django.conf import settings
from celery.schedules import crontab

class CeleryConfig:
    CELERY_BROKER_URL = "redis://redis:6379"
    CELERY_RESULT_BACKEND = "redis://redis:6379"
    CELERY_TIMEZONE = "Asia/Tashkent"
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 120 * 60 * 100
    CELERY_TASK_SOFT_TIME_LIMIT = 120 * 60 * 100
    CELERY_WORKER_MAX_TASKS_PER_CHILD = 100


app = Celery("ice_pos")
app.config_from_object(settings, namespace="CELERY")
app.config_from_object(CeleryConfig, namespace="CELERY")
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

app.conf.beat_schedule = {
    "send_db_backup_to_telegramusers_task": {
        "task": "send_db_backup_to_telegramusers_task",
        # every day at 2 pm
        "schedule": crontab(hour=2, minute=0),
    }
}
