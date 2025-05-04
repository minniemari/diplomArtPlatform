from django.apps import AppConfig
from django.db.utils import OperationalError


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        # Подключение сигналов
        import main.signals
