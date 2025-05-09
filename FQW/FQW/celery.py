from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Укажите настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FQW.settings')

# Создайте экземпляр Celery
app = Celery('FQW')

# Используйте Django-настройки
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживайте задачи в файлах tasks.py
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)