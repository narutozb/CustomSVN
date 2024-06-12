from django.contrib import admin

from .models import Task, Project, Comment, Status, Priority


# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'priority', 'assigned_to', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['project', 'status', 'priority', 'assigned_to']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'created_at']
    search_fields = ['content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'desc']
    search_fields = ['name', 'desc']
    ordering = ['name']


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    search_fields = ['name', 'value']
    ordering = ['value']