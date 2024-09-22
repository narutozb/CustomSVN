# maya/models.py
from types import NoneType

from django.db import models
from django.core.exceptions import ValidationError
from svn.models import FileChange


class MayaFile(models.Model):
    changed_file = models.OneToOneField(FileChange, on_delete=models.CASCADE, related_name='maya_file')
    opened_successfully = models.BooleanField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    local_path = models.CharField(max_length=255, null=True, blank=True)
    client_version = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"MayaFile for {self.changed_file.path}"


class SceneInfo(models.Model):
    maya_file = models.OneToOneField(MayaFile, on_delete=models.CASCADE, related_name='scene_info', blank=True,
                                     null=True)
    transforms = models.IntegerField(default=0)
    groups = models.IntegerField(default=0)
    empty_groups = models.IntegerField(default=0)
    meshes = models.IntegerField(default=0)
    verts = models.IntegerField(default=0)
    edges = models.IntegerField(default=0)
    faces = models.IntegerField(default=0)
    tris = models.IntegerField(default=0)
    uvs = models.IntegerField(default=0)
    ngons = models.IntegerField(default=0)
    materials = models.IntegerField(default=0)
    textures = models.IntegerField(default=0)
    cameras = models.IntegerField(default=0)
    joints = models.IntegerField(default=0)
    lights = models.IntegerField(default=0)
    blend_shapes = models.IntegerField(default=0)
    morph_targets = models.IntegerField(default=0)
    nurbs_curves = models.IntegerField(default=0)
    root_nodes = models.IntegerField(default=0)

    up_axis = models.CharField(max_length=2, blank=True, null=True)
    linear = models.CharField(max_length=10, blank=True, null=True)
    angular = models.CharField(max_length=10, blank=True, null=True)
    current_time = models.FloatField(default=0.0, blank=True, null=True)
    anim_start_time = models.FloatField(default=0.0, blank=True, null=True)
    anim_end_time = models.FloatField(default=0.0, blank=True, null=True)
    play_back_start_time = models.FloatField(default=0.0, blank=True, null=True)
    play_back_end_time = models.FloatField(default=0.0, blank=True, null=True)
    frame_rate = models.FloatField(default=0.0, blank=True, null=True)

    def __str__(self):
        return f'SceneInfo:{self.maya_file}'


class NodeAttribute(models.Model):
    scene = models.ForeignKey(SceneInfo, on_delete=models.CASCADE, related_name='node_attributes')
    node_name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    def clean(self):
        if self.parent and self.parent == self:
            raise ValidationError("A node cannot be its own parent.")

    def __str__(self):
        return f'{self.parent.node_name if self.parent else None}|{self.node_name}'

    class Meta:
        abstract = True


class TransformNode(NodeAttribute):
    translate_x = models.FloatField(default=0.0)
    translate_y = models.FloatField(default=0.0)
    translate_z = models.FloatField(default=0.0)
    rotate_x = models.FloatField(default=0.0)
    rotate_y = models.FloatField(default=0.0)
    rotate_z = models.FloatField(default=0.0)
    scale_x = models.FloatField(default=1.0)
    scale_y = models.FloatField(default=1.0)
    scale_z = models.FloatField(default=1.0)
    visibility = models.BooleanField(default=True)
    scene = models.ForeignKey(SceneInfo, on_delete=models.CASCADE, related_name='transform_nodes', null=True,
                              blank=True)


class ShapeNode(NodeAttribute):
    scene = models.ForeignKey(SceneInfo, on_delete=models.CASCADE, related_name='shape_nodes', null=True, blank=True)
