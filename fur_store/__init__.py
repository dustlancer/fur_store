from __future__ import absolute_import, unicode_literals

# Загружаем Celery при запуске Django
from .celery import app as celery_app

__all__ = ('celery_app',)