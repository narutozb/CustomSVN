from rest_framework import viewsets
from .models import MayaFile
from .serializers import MayaFileSerializer


class MayaFileViewSet(viewsets.ModelViewSet):
    queryset = MayaFile.objects.all()
    serializer_class = MayaFileSerializer
