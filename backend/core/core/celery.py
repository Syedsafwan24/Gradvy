import os
from celery import Celery
from datetime import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('gradvy_analytics_pipeline')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix in your settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Import periodic task configuration
try:
    from apps.preferences.periodic_tasks import *
    # Apply the beat schedule from periodic_tasks.py
    from apps.preferences import periodic_tasks
    if hasattr(periodic_tasks.app.conf, 'beat_schedule'):
        app.conf.beat_schedule = periodic_tasks.app.conf.beat_schedule
        app.conf.task_routes = periodic_tasks.app.conf.task_routes
        app.conf.task_annotations = periodic_tasks.app.conf.task_annotations
except ImportError:
    pass

# Auto-discover tasks in all installed apps.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f'Celery debug task request: {self.request!r}')

@app.task(bind=True)
def health_check(self):
    """Health check task for monitoring pipeline status"""
    from django.utils import timezone
    return {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'worker_id': self.request.hostname,
        'task_id': self.request.id
    }
