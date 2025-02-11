from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Label)
admin.site.register(Category)
admin.site.register(ActionData)
admin.site.register(Report)
admin.site.register(CustomerUser)
admin.site.register(GroupCrm)
admin.site.register(CrmDepartment)

