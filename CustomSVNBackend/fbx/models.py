class FBXFile(models.Model):
    file_change = models.OneToOneField(FileChange, on_delete=models.CASCADE, null=True, blank=True)
    fps = models.FloatField(blank=True, null=True)

    client_version = models.CharField(default='0.0.0', max_length=64, null=True, blank=True)

    def __str__(self):
        return f'FBX for {self.file_change.file_path}'


class Take(models.Model):
    fbx_file = models.ForeignKey(FBXFile, on_delete=models.CASCADE, related_name='takes')
    name = models.CharField(max_length=256, )
    start_frame = models.FloatField()
    end_frame = models.FloatField()
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
    fbx_file = models.ForeignKey(FBXFile, on_delete=models.CASCADE, related_name='model_skeletons')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'fbx_file',)


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
=======
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


class FbxDetail(models.Model):
    fbx = models.OneToOneField(Fbx, on_delete=models.CASCADE, related_name='details')
    fps = models.FloatField()


class Character(models.Model):
    name = models.CharField(max_length=255)
    fbx_detail = models.ForeignKey(FbxDetail, on_delete=models.CASCADE, related_name='characters')


class FbxTake(models.Model):
    fbx_detail = models.ForeignKey(FbxDetail, on_delete=models.CASCADE, related_name='takes')
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'FBX Take {self.name}'


class FbxAnimLayer(models.Model):
    '''
    Take 001: BaseAnimation
    Take 001: AnimLayer1

    '''
    fbx_detail = models.ForeignKey(FbxTake, on_delete=models.CASCADE, related_name='layers')
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'FBX AnimLayer {self.name}'


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

