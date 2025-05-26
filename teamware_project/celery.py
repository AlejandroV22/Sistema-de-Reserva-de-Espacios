import os
from celery import Celery

# Configurar la variable de entorno para que Celery encuentre Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teamware_project.settings')

app = Celery('teamware_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()