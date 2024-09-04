from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from maya.api_serializers.serializer_maya_file import MayaFileSerializer, BulkMayaFileSerializer
from maya.models import MayaFile


class MayaFileQueryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = MayaFile.objects.all()
    serializer_class = MayaFileSerializer
    filter_backends = [DjangoFilterBackend]


class MayaFileCommandViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    queryset = MayaFile.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return BulkMayaFileSerializer
        return MayaFileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        maya_files = serializer.save()
        return Response(MayaFileSerializer(maya_files, many=True).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        maya_files = serializer.save()
        return Response(MayaFileSerializer(maya_files, many=True).data, status=status.HTTP_200_OK)
