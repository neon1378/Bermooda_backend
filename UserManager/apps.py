from django.apps import AppConfig

from apscheduler.schedulers.background import BackgroundScheduler

class SuperusermangerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'UserManager'
