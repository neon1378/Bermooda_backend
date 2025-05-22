from django.contrib import admin
from .models import *


admin.site.register(Image)
admin.site.register(Core)
admin.site.register(City)
admin.site.register(State)
admin.site.register(MainFile)
admin.site.register(Reminder)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ( 'is_deleted', 'deleted_at',"name","id")
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