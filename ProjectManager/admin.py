from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(CategoryProject)
class CategoryProjectAdmin(admin.ModelAdmin):
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

@admin.register(TaskLabel)
class TaskLabelAdmin(admin.ModelAdmin):
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
@admin.register(CheckList)
class CheckListAdmin(admin.ModelAdmin):
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

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
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
@admin.register(ProjectChat)
class ProjectChatAdmin(admin.ModelAdmin):
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


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
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


@admin.register(TaskReport)
class TaskReportAdmin(admin.ModelAdmin):
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


@admin.register(ProjectMessage)
class CategoryProjectAdmin(admin.ModelAdmin):
    list_display = ( 'is_deleted', 'deleted_at',"id")
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