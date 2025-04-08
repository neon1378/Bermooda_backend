from django.db import models
from core.models import SoftDeleteModel,MainFile
# Create your models here.
class MeetingPlan(SoftDeleteModel):
    REMEMBER_TYPE = (
        ("hour", "HOUR"),
        ("minute", "MINUTE"),
        ("day", "day"),
    )
    title = models.CharField(max_length=50,null=True)
    files = models.ManyToManyField(MainFile)
    date_to_start = models.DateField(null=True)
    remember_type = models.CharField(choices=REMEMBER_TYPE,null=True)
    remember_time = models.IntegerField(default=0)
