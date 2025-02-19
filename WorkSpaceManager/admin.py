from django.contrib import admin
from .models import *


admin.site.register(WorkSpace)
admin.site.register(IndustrialActivity)
admin.site.register(WorkspaceMember)


admin.site.register(MemberPermission)
admin.site.register(ViewName)

admin.site.register(MethodPermission)
# Register your models here.



