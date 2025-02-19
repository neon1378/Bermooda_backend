from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CategoryProject)
admin.site.register(TaskLabel)

admin.site.register(CheckList)
admin.site.register(Task)
admin.site.register(ProjectChat)
admin.site.register(Project)
admin.site.register(TaskReport)

