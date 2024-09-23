from django_filters import rest_framework as filters
from rest_framework import viewsets

from maya.api_serializers.serializer_transform_node import TransformNodeQuerySerializer
from maya.models import TransformNode
from svn.pagination import CustomPagination


class TransformNodeFilter(filters.FilterSet):
    node_name = filters.CharFilter(field_name='node_name')
    parent_node_name = filters.CharFilter(field_name='parent__node_name')


class TransformNodeQueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransformNode.objects.all()
    serializer_class = TransformNodeQuerySerializer
    pagination_class = CustomPagination
    filterset_class = TransformNodeFilter
