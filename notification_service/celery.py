import os

from celery import Celery
from tasks.tasks import schedule_periodic_tasks


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notification_service.settings")
app = Celery("notification_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.on_after_finalize.connect
def on_after_configure(sender, **kwargs):
    app.loader.import_default_modules()
    schedule_periodic_tasks(sender, **kwargs)
