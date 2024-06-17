from django.contrib import admin

from .models import FBXFile, Take, ModelSkeleton, TakeModelSkeleton


@admin.register(FBXFile)
class FBXFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'fps', 'file_change', 'client_version',)


@admin.register(Take)
class TakeAdmin(admin.ModelAdmin):
    list_display = ('id', 'fbx_file', 'name', 'start_frame', 'end_frame',)


@admin.register(ModelSkeleton)
class ModelSkeletonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent',)


@admin.register(TakeModelSkeleton)
class ModelSkeletonKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'take', 'model_skeleton', 'ws_location', 'ws_rotation', 'ws_scale', 'frame',)
