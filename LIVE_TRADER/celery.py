from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LIVE_TRADER.settings')

app = Celery('LIVE_TRADER')
app.conf.broker_transport_options = {
    'priority_steps': [0, 1],
}
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.result_expires = 60 * 60 * 24
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

