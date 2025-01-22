from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import logging

logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Update broker transport options with Kafka-specific settings
app.conf.update(
    broker_transport_options={
        'transport': '.kafka_transport.KafkaTransport',
        'kafka_heartbeat_interval_ms': 3000,
        'kafka_session_timeout_ms': 30000,
        'kafka_max_poll_interval_ms': 300000,  # Optional
    }
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
