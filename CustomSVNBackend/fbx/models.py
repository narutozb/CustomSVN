from django.core.exceptions import ValidationError
from django.db import models

from svn.models import FileChange


# Create your models here.


class Fbx(models.Model):
    changed_file = models.OneToOneField(FileChange, on_delete=models.CASCADE, related_name='fbx_file')
    opened_successfully = models.BooleanField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    local_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'FBX'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'FBX for {self.changed_file.file_path}'


class NodeAttribute(models.Model):
    node_name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    def clean(self):
        if self.parent and self.parent == self:
            raise ValidationError("A node cannot be its own parent.")

    class Meta:
        abstract = True


class Node(NodeAttribute):
    fbx = models.ForeignKey(Fbx, on_delete=models.CASCADE, related_name='nodes')
