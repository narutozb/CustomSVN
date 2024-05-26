from django.contrib import admin

# Register your models here.
from .models import MayaFile, TransformNode, ShapeNode


@admin.register(MayaFile)
class MayaFileAdmin(admin.ModelAdmin):
    list_display = ['changed_file', 'file_attribute', 'scene_info']


@admin.register(TransformNode)
class TransformNodeAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'transform_property', 'scene']


@admin.register(ShapeNode)
class ShapeNodeAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'shape_property', 'scene']
