from django.db import models

from svn.models import FileChange


# Create your models here.


class FBXFile(models.Model):
    file_change = models.OneToOneField(FileChange, on_delete=models.CASCADE, null=True, blank=True)
    fps = models.FloatField()

    def __str__(self):
        return f'FBX for {self.file_change.file_path}'


class Take(models.Model):
    fbx_file = models.ForeignKey(FBXFile, on_delete=models.CASCADE, related_name='takes')
    name = models.CharField(max_length=256, )
    start_frame = models.IntegerField()
    end_frame = models.IntegerField()
    model_skeleton_keys = models.ManyToManyField('ModelSkeleton', through='TakeModelSkeleton', related_name='takes')

    def __str__(self):
        return self.name


class Float3Field(models.Field):
    description = "A field to store 3D coordinates as three floats"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return [float(x) for x in value.split(',')]

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is None:
            return value
        return [float(x) for x in value.split(',')]

    def get_prep_value(self, value):
        return ','.join(map(str, value))

    def db_type(self, connection):
        return 'text'


class ModelSkeleton(models.Model):
    name = models.CharField(max_length=256)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)

    def __str__(self):
        return self.name


class TakeModelSkeleton(models.Model):
    take = models.ForeignKey(Take, on_delete=models.CASCADE, related_name='model_skeletons')
    model_skeleton = models.ForeignKey(ModelSkeleton, on_delete=models.CASCADE, related_name='keys')
    ws_location = Float3Field()
    ws_rotation = Float3Field()
    ws_scale = Float3Field()
    frame = models.FloatField()

    def __str__(self):
        return f'{self.take.name} - {self.model_skeleton.name} - {self.frame}'

    class Meta:
        unique_together = ('take', 'model_skeleton',)
