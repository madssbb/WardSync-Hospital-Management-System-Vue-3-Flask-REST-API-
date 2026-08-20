from app import celery_app
from celery.schedules import crontab
from tasks import *

# Ensure celery beat schedule is configured
celery_app.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-reports': {
        'task': 'tasks.generate_monthly_reports',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
    },
}
celery_app.conf.timezone = 'UTC'
