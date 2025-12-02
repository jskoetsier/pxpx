import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pxmx.settings")

app = Celery("pxmx")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# Periodic task schedule
app.conf.beat_schedule = {
    "sync-all-clusters-every-5-minutes": {
        "task": "proxmox_manager.tasks.sync_all_clusters",
        "schedule": 300.0,  # 5 minutes in seconds
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
