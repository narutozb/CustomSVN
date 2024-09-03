from crypt import methods

from django.core.serializers import serialize
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.response import Response

from svn._serializers.serializer_branch import BranchQuerySerializer
from svn._serializers.serializer_repository import RepositoryQuerySerializer
from svn.models import Repository, Branch
from svn.pagination import CustomPagination


class RepositoryFilter(filters.FilterSet):
    name = filters.CharFilter()
    commit_id = filters.NumberFilter(field_name='commits__id')
    file_change_id = filters.NumberFilter(field_name='commits__file_changes')

    class Meta:
        model = Repository
        fields = ['name', 'id', 'commit_id', 'file_change_id']


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

    @action(detail=True, methods=['GET'])
    def branches(self, request, pk=None):
        branches = Branch.objects.filter(repository_id=pk)
        page = self.paginate_queryset(branches)
        if page is not None:
            branches = page

        serializer = BranchQuerySerializer(branches, many=True)

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)
