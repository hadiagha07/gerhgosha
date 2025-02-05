from django.apps import AppConfig
from django.core.management import call_command


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        import threading
        from .apscheduler import start_scheduler
        threading.Thread(target=start_scheduler).start()