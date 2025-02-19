from django.contrib import admin
from .models import *


@admin.register(WorkSpace)
class WorkSpaceAdmin(admin.ModelAdmin):
    list_display = ( 'is_deleted', 'deleted_at')
    list_filter = ('is_deleted',)
    actions = ['restore_selected']

    def get_queryset(self, request):
        # Use the custom manager's queryset
        return self.model.all_objects.get_queryset()

    @admin.action(description='Restore selected items')
    def restore_selected(self, request, queryset):
        # Restore soft-deleted items
        queryset.update(is_deleted=False, deleted_at=None)
        self.message_user(request, f'{queryset.count()} items restored successfully.')
admin.site.register(IndustrialActivity)
admin.site.register(WorkspaceMember)


admin.site.register(MemberPermission)
admin.site.register(ViewName)

admin.site.register(MethodPermission)
# Register your models here.



