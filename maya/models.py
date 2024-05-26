from django.db import models
from svn.models import FileChange


class FileAttribute(models.Model):
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    local_path = models.CharField(max_length=255)


class SceneInfo(models.Model):
    transforms = models.IntegerField(default=0)
    groups = models.IntegerField(default=0)
    empty_groups = models.IntegerField(default=0)
    meshes = models.IntegerField(default=0)
    edges = models.IntegerField(default=0)
    up_axis = models.CharField(max_length=10, blank=True, null=True)
    linear = models.CharField(max_length=10, blank=True, null=True)
    current_time = models.FloatField(blank=True, null=True)
    anim_start_time = models.FloatField(blank=True, null=True)
    frame_rate = models.FloatField(blank=True, null=True)


class NodeAttribute(models.Model):
    scene = models.ForeignKey(SceneInfo, on_delete=models.CASCADE, related_name='node_attributes')
    node_name = models.CharField(max_length=255)

    class Meta:
        abstract = True


class TransformNode(NodeAttribute):
    transform_property = models.CharField(max_length=255)  # 示例属性
    scene = models.ForeignKey(SceneInfo, on_delete=models.CASCADE, related_name='transform_nodes')


class ShapeNode(NodeAttribute):
    shape_property = models.CharField(max_length=255)  # 示例属性
    scene = models.ForeignKey(SceneInfo, on_delete=models.CASCADE, related_name='shape_nodes')


class MayaFile(models.Model):
    changed_file = models.OneToOneField(FileChange, on_delete=models.CASCADE, related_name='maya_file')
    file_attribute = models.OneToOneField(FileAttribute, on_delete=models.CASCADE, related_name='maya_file')
    scene_info = models.OneToOneField(SceneInfo, on_delete=models.CASCADE, related_name='maya_file', blank=True,
                                      null=True)

    def __str__(self):
        return f"MayaFile for {self.changed_file.file_path}"
