from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.response import Response

from svn._serializers.serializer_repository import RepositoryQuerySerializer
from svn.models import Repository
from svn.pagination import CustomPagination


class RepositoryFilter(filters.FilterSet):
    name = filters.CharFilter()

    class Meta:
        model = Repository
        fields = ['name', ]


class RepositoryQueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositoryQuerySerializer
    pagination_class = CustomPagination
    filterset_class = RepositoryFilter

    def list(self, request, *args, **kwargs):
        '''
        ?name=repository_name
        '''
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
