from django.contrib import admin
from .models import *
from django.contrib import admin
admin.site.register(CustomerBank)

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ( 'is_deleted', 'deleted_at',"title")
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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ( 'is_deleted', 'deleted_at',"title")
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

@admin.register(ActionData)
class ActionDataAdmin(admin.ModelAdmin):
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
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
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
@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ( 'is_deleted', 'deleted_at',"fullname_or_company_name")
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
@admin.register(GroupCrm)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ( 'is_deleted', 'deleted_at',"title")
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
@admin.register(CrmDepartment)
class CrmDepartmentAdmin(admin.ModelAdmin):
    list_display = ( 'is_deleted', 'deleted_at',"title")
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
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
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
@admin.register(CampaignField)
class CampaignFieldAdmin(admin.ModelAdmin):
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

@admin.register(CampaignForm)
class CampaignFormAdmin(admin.ModelAdmin):
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
@admin.register(CampaignFormData)
class CampaignFormDataAdmin(admin.ModelAdmin):
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


@admin.register(LabelStep)
class LabelStepAdmin(admin.ModelAdmin):
    list_display = ('is_deleted', 'deleted_at')
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


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ('is_deleted', 'deleted_at')
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

@admin.register(CustomerStep)
class CustomerStepAdmin(admin.ModelAdmin):
    list_display = ('is_deleted', 'deleted_at')
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



