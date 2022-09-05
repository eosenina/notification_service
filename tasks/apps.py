from django.apps import AppConfig
from .tasks import schedule_periodic_tasks


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
