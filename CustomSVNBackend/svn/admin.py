from django.contrib import admin
from .models import Repository, Commit, FileChange


class FileChangeInline(admin.TabularInline):
    model = FileChange
    extra = 0




@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'url', 'created_at')
    search_fields = ('name', 'url')


@admin.register(Commit)
class CommitAdmin(admin.ModelAdmin):
    list_display = ('id','repository', 'revision', 'author', 'message', 'date')
    search_fields = ('repository__name', 'revision', 'author')
    list_filter = ('repository', 'author', 'date')
    inlines = [FileChangeInline]


# @admin.register(FileChange)
# class FileChangeAdmin(admin.ModelAdmin):
#     list_display = ('id','commit', 'file_path', 'change_type')
#     search_fields = ('commit__revision', 'file_path')
#     list_filter = ('change_type',)
