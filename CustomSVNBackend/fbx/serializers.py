from .models import FBXFile, Take, ModelSkeleton, TakeModelSkeleton
from rest_framework import serializers


class FBXFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FBXFile
        fields = '__all__'


class TakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Take
        fields = '__all__'


class ModelSkeletonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelSkeleton
        fields = '__all__'


class TakeModelSkeletonSerializer(serializers.ModelSerializer):
    class Meta:
        model = TakeModelSkeleton
        fields = '__all__'


class ReceiveFBXFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FBXFile
        fields = ['fps', 'file_change', 'client_version']


class ReceiveTakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Take
        fields = ['fbx_file', 'name', 'start_frame', 'end_frame']


class ReceiveModelSkeleton(serializers.ModelSerializer):
    class Meta:
        model = ModelSkeleton
        fields = ['name', 'fbx_file']

