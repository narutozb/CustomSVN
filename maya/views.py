from rest_framework import viewsets
from .models import MayaFile,  SceneInfo, TransformNode, ShapeNode
from .serializers import MayaFileSerializer,  SceneInfoSerializer, TransformNodeSerializer, ShapeNodeSerializer

class MayaFileViewSet(viewsets.ModelViewSet):
    queryset = MayaFile.objects.all()
    serializer_class = MayaFileSerializer



class SceneInfoViewSet(viewsets.ModelViewSet):
    queryset = SceneInfo.objects.all()
    serializer_class = SceneInfoSerializer

class TransformNodeViewSet(viewsets.ModelViewSet):
    queryset = TransformNode.objects.all()
    serializer_class = TransformNodeSerializer

class ShapeNodeViewSet(viewsets.ModelViewSet):
    queryset = ShapeNode.objects.all()
    serializer_class = ShapeNodeSerializer
