from rest_framework import viewsets
from .models import MayaFile, TransformNode, ShapeNode
from .serializers import MayaFileSerializer, TransformNodeSerializer, ShapeNodeSerializer

class MayaFileViewSet(viewsets.ModelViewSet):
    queryset = MayaFile.objects.all()
    serializer_class = MayaFileSerializer

class TransformNodeViewSet(viewsets.ModelViewSet):
    queryset = TransformNode.objects.all()
    serializer_class = TransformNodeSerializer

class ShapeNodeViewSet(viewsets.ModelViewSet):
    queryset = ShapeNode.objects.all()
    serializer_class = ShapeNodeSerializer
