from django.contrib import admin
from .models import Repository, Commit, FileChange, Branch


class FileChangeInline(admin.TabularInline):
    model = FileChange
    extra = 0


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'repository')
    search_fields = ('name', 'repository__name')


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url', 'created_at')
    search_fields = ('name', 'url')


@admin.register(Commit)
class CommitAdmin(admin.ModelAdmin):
    list_display = ('id', 'repository', 'revision', 'branch', 'author', 'message', 'date')
    search_fields = ('repository__name', 'revision', 'author')
    list_filter = ('repository', 'author', 'date', 'branch',)
    inlines = [FileChangeInline]


@admin.register(FileChange)
class FileChangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'commit', 'path', 'action')
    search_fields = ('commit__revision', 'path')
    list_filter = ('action',)
