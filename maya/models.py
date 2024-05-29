from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from svn.models import FileChange


class SceneInfo(models.Model):
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


class NodeAttribute(models.Model):
    scene = models.ForeignKey(SceneInfo, on_delete=models.CASCADE, related_name='node_attributes')
    node_name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    def clean(self):
        if self.parent and self.parent == self:
            raise ValidationError("A node cannot be its own parent.")

    class Meta:
        abstract = True


class TransformNode(NodeAttribute):
    transform_property = models.CharField(max_length=255)
    translate_x = models.FloatField(default=0.0)
    translate_y = models.FloatField(default=0.0)
    translate_z = models.FloatField(default=0.0)
    rotate_x = models.FloatField(default=0.0)
    rotate_y = models.FloatField(default=0.0)
    rotate_z = models.FloatField(default=0.0)
    scale_x = models.FloatField(default=1.0)
    scale_y = models.FloatField(default=1.0)
    scale_z = models.FloatField(default=1.0)
    scene = models.ForeignKey(SceneInfo, on_delete=models.CASCADE, related_name='transform_nodes')


class ShapeNode(NodeAttribute):
    shape_property = models.CharField(max_length=255)
    scene = models.ForeignKey(SceneInfo, on_delete=models.CASCADE, related_name='shape_nodes')


class MayaFile(models.Model):
    changed_file = models.OneToOneField(FileChange, on_delete=models.CASCADE, related_name='maya_file')
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    local_path = models.CharField(max_length=255)
    scene_info = models.OneToOneField(SceneInfo, on_delete=models.CASCADE, related_name='maya_file', blank=True,
                                      null=True)
    transform_nodes = models.ManyToManyField(TransformNode, related_name='maya_files')
    shape_nodes = models.ManyToManyField(ShapeNode, related_name='maya_files')

    def __str__(self):
        return f"MayaFile for {self.changed_file.file_path}"


@receiver(post_delete, sender=MayaFile)
def delete_related_scene_info(sender, instance, **kwargs):
    if instance.scene_info:
        instance.scene_info.delete()
