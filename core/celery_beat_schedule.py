from celery.schedules import crontab

BEAT_SCHEDULE = {
    'check-ssl-certificates-daily': {
        'task': 'core.tasks.check_ssl_certificates',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight every day
        'args': (),
    },
    'send-ssl-expiry-notifications-daily': {
        'task': 'core.tasks.send_ssl_expiry_notifications',
        'schedule': crontab(hour=8, minute=0),  # Run at 8 AM every day
        'args': (),
    },
    'update-expired-certificates-hourly': {
        'task': 'core.tasks.update_expired_certificates',
        'schedule': crontab(minute=0),  # Run every hour
        'args': (),
    },
}