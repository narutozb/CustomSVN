from django.contrib import admin

# Register your models here.

from .models import Fbx, FbxDetail,  NodeAttribute


@admin.register(Fbx)
class FbxAdmin(admin.ModelAdmin):
    list_display = ('changed_file', 'opened_successfully', 'local_path')
    list_filter = ('opened_successfully',)


@admin.register(FbxDetail)
class FbxDetailAdmin(admin.ModelAdmin):
    list_display = ('fbx',)




