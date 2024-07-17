from .models import FBXFile, Take, ModelSkeleton, TakeModelSkeleton
from rest_framework import serializers
from packaging import version
from django.db import models


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
        fields = ['fps', 'file_change', 'client_version', ]

    def update(self, instance: FBXFile, validated_data):
        current_version = version.parse(instance.client_version)
        new_version = version.parse(validated_data.get('client_version', '0,0,0'))
        if new_version > current_version:
            for k, v in validated_data.items():
                setattr(instance, k, v)
        instance.save()
        return instance


class ReceiveTakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Take
        fields = ['fbx_file', 'name', 'start_frame', 'end_frame', ]

    def update(self, instance: Take, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class ReceiveModelSkeleton(serializers.ModelSerializer):
    class Meta:
        model = ModelSkeleton
        fields = ['name', 'fbx_file']
