from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(AnonCustomer)
admin.site.register(Department)
admin.site.register(Room)
admin.site.register(RoomMessage)
admin.site.register(GroupRoom)



