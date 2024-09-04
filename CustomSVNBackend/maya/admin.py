from django.contrib import admin
from django.shortcuts import redirect

from svn.models import Repository
# Register your models here.
from .models import MayaFile, TransformNode, ShapeNode, SceneInfo


@admin.register(MayaFile)
class MayaFileAdmin(admin.ModelAdmin):
    list_display = ['changed_file', 'scene_info', 'opened_successfully', 'description', 'local_path']
    search_fields = ['changed_file__file_path', ]
    list_filter = ['changed_file__commit__repository', ]


@admin.register(TransformNode)
class TransformNodeAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'scene', ]


@admin.register(ShapeNode)
class ShapeNodeAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'scene']


@admin.register(SceneInfo)
class SceneInfoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'maya_file', 'display_revision',
        'transforms', 'groups', 'empty_groups', 'meshes', 'verts', 'edges', 'faces', 'tris', 'uvs', 'ngons',
        'materials', 'textures', 'cameras', 'joints', 'lights', 'blend_shapes', 'morph_targets',
        'nurbs_curves', 'root_nodes', 'up_axis', 'linear', 'angular', 'current_time', 'anim_start_time',
        'anim_end_time', 'play_back_start_time', 'play_back_end_time', 'frame_rate'
    ]
    search_fields = (
        'related_maya_file__changed_file__file_path',
    )
    list_filter = ['maya_file__changed_file__commit__repository__name', ]

    def display_revision(self, obj):
        return obj.related_maya_file.changed_file.commit.revision

    display_revision.short_description = 'Revision'
