from django.contrib import admin
from .models import MayaFile, SceneInfo, TransformNode, MorphTargetNode


class SceneInfoInline(admin.StackedInline):
    model = SceneInfo
    show_change_link = True
    extra = 0


class TransformNodeInline(admin.TabularInline):
    model = TransformNode
    show_change_link = True
    extra = 0
    raw_id_fields = ('parent',)


@admin.register(MayaFile)
class MayaFileAdmin(admin.ModelAdmin):
    list_display = ['changed_file', 'opened_successfully', 'description', 'local_path']
    list_filter = ['changed_file__commit__repository', ]
    inlines = [SceneInfoInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'changed_file__commit__repository',
            'scene_info'
        ).prefetch_related(
            'scene_info__transform_nodes'
        )


@admin.register(SceneInfo)
class SceneInfoAdmin(admin.ModelAdmin):
    inlines = [TransformNodeInline]
    list_display = ['maya_file', 'tris', 'joints', 'materials', 'textures', 'morph_targets', 'blend_shapes']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('maya_file').prefetch_related('transform_nodes')


@admin.register(TransformNode)
class TransformNodeAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'scene', 'parent', 'attr_name', 'translate_x', 'translate_y', 'translate_z',
                    'rotate_x', 'rotate_y', 'rotate_z', 'scale_x', 'scale_y', 'scale_z', 'visibility']
    list_filter = ['scene__maya_file__changed_file__commit__repository']
    raw_id_fields = ('parent', 'scene')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('scene__maya_file', 'parent')


@admin.register(MorphTargetNode)
class MorphTargetNodeAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'weight', 'scene', ]
