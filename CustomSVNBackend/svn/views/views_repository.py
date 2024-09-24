from django.db.models import Max
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.response import Response

from svn._serializers.serializer_branch import BranchQuerySerializer
from svn._serializers.serializer_commit import CommitQuerySerializerS
from svn._serializers.serializer_repository import RepositoryQuerySerializer, RepositoryQuerySoloSerializer, \
    RepositoryQuerySerializerS, RepositoryCommitSearchFilterSerializer
from svn.models import Repository, Branch, Commit
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
    serializer_class = RepositoryQuerySerializerS
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

    @action(detail=True, methods=['GET'])
    def detail_authors(self, request, pk=None):
        commits = Commit.objects.filter(repository_id=pk)
        authors = commits.values('author').annotate(
            max_id=Max('id')
        ).values_list('author', flat=True)

        return Response(authors)

    @action(detail=False, methods=['GET'])
    def authors(self, request):
        commits = Commit.objects
        authors = commits.values('author').annotate(
            max_id=Max('id')
        ).values_list('author', flat=True)

        return Response(authors)

    @action(detail=True, methods=['GET'])
    def solo(self, request, pk: None):
        # repo = Repository.objects.select_related("branch").get(id=pk)

        repo = Repository.objects.prefetch_related("branches").get(id=pk)
        print(repo)
        serializer = RepositoryQuerySoloSerializer(repo)
        # return Response(serializer.data)
        return Response()

    @action(detail=True, methods=['GET'])
    def commit_search_filter(self, request, pk=None):
        '''
        commit搜索页面的过滤其
        '''
        repositories = Repository.objects.get(id=pk)
        serializer = RepositoryCommitSearchFilterSerializer(repositories)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def latest_commit(self, request, pk=None):
        commit = Commit.objects.filter(repository_id=pk).order_by('-revision').first()
        serializer = CommitQuerySerializerS(commit)
        return Response(serializer.data)
