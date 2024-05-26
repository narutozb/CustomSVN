# maya/

from django.db import models
from svn.models import FileChange


class MayaFile(models.Model):
    changed_file = models.OneToOneField(FileChange, on_delete=models.CASCADE, related_name='maya_file')
    description = models.TextField()

    def __str__(self):
        return f"MayaFile for {self.changed_file.file_path}"