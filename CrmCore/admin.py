from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.admin.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "action_time", "content_type", "object_repr", "action_flag")
    list_filter = ("action_flag", "content_type", "user")
# Register your models here.
admin.site.register(Label)
admin.site.register(Category)
admin.site.register(ActionData)
admin.site.register(Report)
admin.site.register(CustomerUser)
admin.site.register(GroupCrm)
admin.site.register(CrmDepartment)

admin.site.register(Campaign)
admin.site.register(CampaignField)
admin.site.register(CampaignForm)
admin.site.register(CampaignFormData)
# admin.site.register(IpAshol)

@admin.register(IpAshol)
class IpAsholAdmin(admin.ModelAdmin):
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