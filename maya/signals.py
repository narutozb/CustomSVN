from django.db.models.signals import post_delete
from django.dispatch import receiver
from svn.models import FileChange
from .models import MayaFile


@receiver(post_delete, sender=FileChange)
def delete_related_maya_file(sender, instance, **kwargs):
    try:
        maya_file = instance.maya_file
        maya_file.delete()
    except MayaFile.DoesNotExist:
        pass
