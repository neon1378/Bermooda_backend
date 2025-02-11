# myproject/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CrmManager.settings')

app = Celery('CrmManager')
app.conf.enable_utc = False
app.conf.timezone = 'Asia/Tehran'

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['WalletManager','core'])


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
