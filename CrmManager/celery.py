import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CrmManager.settings')

app = Celery('CrmManager')
app.conf.enable_utc = False
app.conf.timezone = 'Asia/Tehran'
app.conf.broker_connection_retry_on_startup = True
# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['WalletManager', 'core'])

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))