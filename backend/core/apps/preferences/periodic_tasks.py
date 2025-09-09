"""
Periodic Task Scheduling Configuration
Defines scheduled tasks for data processing pipeline
"""

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

app = Celery('gradvy_data_pipeline')

# Configure periodic tasks
app.conf.beat_schedule = {
    # Real-time data processing (every 30 seconds)
    'process-pending-events': {
        'task': 'apps.preferences.tasks.batch_process_events',
        'schedule': 30.0,  # Run every 30 seconds
        'options': {'queue': 'realtime'}
    },
    
    # User behavior analysis (every 15 minutes)
    'analyze-user-behaviors': {
        'task': 'apps.preferences.tasks.analyze_user_behavior',
        'schedule': timedelta(minutes=15),
        'options': {'queue': 'analytics'}
    },
    
    # Update user segments (every hour)
    'update-user-segments': {
        'task': 'apps.preferences.tasks.update_user_segments',
        'schedule': crontab(minute=0),  # Every hour at :00
        'options': {'queue': 'ml'}
    },
    
    # Generate daily reports (every day at 6 AM UTC)
    'daily-analytics-report': {
        'task': 'apps.preferences.tasks.generate_analytics_reports',
        'schedule': crontab(hour=6, minute=0),
        'options': {'queue': 'reports'}
    },
    
    # Cleanup old data (every day at 2 AM UTC)
    'cleanup-analytics-data': {
        'task': 'apps.preferences.tasks.cleanup_old_analytics_data',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'maintenance'}
    },
    
    # Performance monitoring (every 5 minutes)
    'monitor-system-performance': {
        'task': 'apps.preferences.tasks.monitor_system_performance',
        'schedule': timedelta(minutes=5),
        'options': {'queue': 'monitoring'}
    },
    
    # Update ML models (every 6 hours)
    'update-recommendation-models': {
        'task': 'apps.preferences.tasks.update_recommendation_models',
        'schedule': crontab(minute=0, hour='*/6'),
        'options': {'queue': 'ml'}
    },
    
    # Privacy compliance audit (daily at midnight)
    'privacy-compliance-audit': {
        'task': 'apps.preferences.tasks.privacy_compliance_audit',
        'schedule': crontab(hour=0, minute=0),
        'options': {'queue': 'compliance'}
    },
}

# Queue configuration
app.conf.task_routes = {
    # Real-time processing
    'apps.preferences.tasks.process_analytics_event': {'queue': 'realtime'},
    'apps.preferences.tasks.batch_process_events': {'queue': 'realtime'},
    'apps.preferences.tasks.update_realtime_metrics': {'queue': 'realtime'},
    
    # Analytics and ML
    'apps.preferences.tasks.analyze_user_behavior': {'queue': 'analytics'},
    'apps.preferences.tasks.update_user_segments': {'queue': 'ml'},
    'apps.preferences.tasks.update_recommendation_models': {'queue': 'ml'},
    
    # System maintenance
    'apps.preferences.tasks.cleanup_old_analytics_data': {'queue': 'maintenance'},
    'apps.preferences.tasks.monitor_system_performance': {'queue': 'monitoring'},
    
    # Compliance and reporting
    'apps.preferences.tasks.generate_analytics_reports': {'queue': 'reports'},
    'apps.preferences.tasks.privacy_compliance_audit': {'queue': 'compliance'},
}

# Worker configuration for different queues
app.conf.task_default_queue = 'default'
app.conf.task_create_missing_queues = True

# Priority and resource allocation
app.conf.task_queue_max_priority = 10
app.conf.worker_prefetch_multiplier = 1  # Important for real-time processing

# Task execution settings
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1
app.conf.task_reject_on_worker_lost = True

# Result backend settings
app.conf.result_expires = 3600  # Results expire after 1 hour
app.conf.result_persistent = True

# Error handling
app.conf.task_annotations = {
    'apps.preferences.tasks.process_analytics_event': {
        'rate_limit': '1000/m',  # Max 1000 per minute
        'time_limit': 60,        # 60 second time limit
        'soft_time_limit': 45,   # 45 second soft limit
    },
    'apps.preferences.tasks.analyze_user_behavior': {
        'rate_limit': '100/m',   # Max 100 per minute
        'time_limit': 300,       # 5 minute time limit
        'soft_time_limit': 240,  # 4 minute soft limit
    },
    'apps.preferences.tasks.update_recommendation_models': {
        'rate_limit': '10/h',    # Max 10 per hour
        'time_limit': 1800,      # 30 minute time limit
        'soft_time_limit': 1500, # 25 minute soft limit
    }
}

# Development vs Production settings
import os
if os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('production'):
    # Production settings
    app.conf.worker_concurrency = 4
    app.conf.worker_max_tasks_per_child = 1000
else:
    # Development settings
    app.conf.worker_concurrency = 2
    app.conf.worker_max_tasks_per_child = 100

# Monitoring and logging
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True