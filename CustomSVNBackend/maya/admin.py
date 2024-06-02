from django.contrib import admin

# Register your models here.
from .models import MayaFile, TransformNode, ShapeNode, SceneInfo


@admin.register(MayaFile)
class MayaFileAdmin(admin.ModelAdmin):
    list_display = ['changed_file', 'scene_info', ]


@admin.register(TransformNode)
class TransformNodeAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'transform_property', 'scene']


@admin.register(ShapeNode)
class ShapeNodeAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'shape_property', 'scene']


@admin.register(SceneInfo)
class SceneInfoAdmin(admin.ModelAdmin):
    list_display = ['transforms', 'groups', 'empty_groups', 'meshes', 'verts', 'edges', 'faces', 'tris', 'uvs', 'ngons',
                    'materials', 'textures', 'cameras', 'joints', 'lights', 'blend_shapes', 'morph_targets',
                    'nurbs_curves', 'root_nodes', 'up_axis', 'linear', 'angular', 'current_time', 'anim_start_time',
                    'anim_end_time', 'play_back_start_time', 'play_back_end_time', 'frame_rate']
