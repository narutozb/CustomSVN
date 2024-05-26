from rest_framework import serializers
from .models import MayaFile

class MayaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MayaFile
        fields = '__all__'

