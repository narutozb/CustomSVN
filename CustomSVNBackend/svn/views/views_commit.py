from django_filters import rest_framework as filters
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db.models import Q, Max
from django.utils import timezone
from rest_framework.exceptions import NotFound

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from functools import reduce
from operator import or_
from datetime import datetime, time
import logging

from svn._serializers.serializer_commit import CommitQuerySerializerS
from svn._serializers.serializer_file_change import FileChangeQuerySerializer
from svn.models import Commit, FileChange
from svn.pagination import CustomPagination


class CommitFilter(filters.FilterSet):
    # 现有的过滤器
    repo_name = filters.CharFilter(field_name='repository__name')
    message = filters.CharFilter()
    branch_name = filters.CharFilter(field_name='branch__name')
    revision = filters.NumberFilter()
    branch_id = filters.NumberFilter()

    repo_name_contains = filters.CharFilter(field_name='repository__name', lookup_expr='icontains')
    message_contains = filters.CharFilter(field_name='message', lookup_expr='icontains')
    branch_name_contains = filters.CharFilter(field_name='branch__name', lookup_expr='icontains')

    authors = filters.CharFilter(method='filter_authors', label='authors')
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte', method='filter_date_from')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte', method='filter_date_to')
    branch_ids = filters.CharFilter(method='filter_branch_ids', label='branch_ids')

    revision_from = filters.NumberFilter(field_name='revision', lookup_expr='gte')
    revision_to = filters.NumberFilter(field_name='revision', lookup_expr='lte')

    # 新增的 repository id 过滤器
    repo_id = filters.NumberFilter(field_name='repository__id')

    file_path_contains = filters.CharFilter(method='filter_file_path', label='file_path_contains')
    

    def filter_file_path(self, queryset, name, value):
        return queryset.filter(file_changes__path__icontains=value).distinct()

    def filter_message_contains(self, queryset, name, value):
        return queryset.filter(message__icontains=value)

    def filter_authors(self, queryset, name, value):
        if not value:
            return queryset
        authors = [author.strip() for author in value.split(',') if author.strip()]
        return queryset.filter(author__in=authors)

    def filter_branch_ids(self, queryset, name, value):
        if not value:
            return queryset
        branch_ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
        return queryset.filter(branch__id__in=branch_ids)

    def filter_date_from(self, queryset, name, value):
        if not value:
            return queryset
        date_from = timezone.make_aware(datetime.combine(value, time.min))
        return queryset.filter(date__gte=date_from)

    def filter_date_to(self, queryset, name, value):
        if not value:
            return queryset
        date_to = timezone.make_aware(datetime.combine(value, time.max))
        return queryset.filter(date__lte=date_to)

    class Meta:
        model = Commit
        fields = [
            'revision',
            'repo_name',
            'message',
            'branch_name',
            'repo_name_contains',
            'message_contains',
            'branch_name_contains',
            'authors',
            'date_from', 'date_to',
            'repo_id',
            'branch_id',
            'branch_ids',
            'revision_from',
            'revision_to',
            'message_contains',
            'file_path_contains',
        ]


logger = logging.getLogger(__name__)


class CommitQueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Commit.objects.all()
    serializer_class = CommitQuerySerializerS
    pagination_class = CustomPagination
    filterset_class = CommitFilter
    ordering_fields = ['revision', 'date', 'author']

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_queryset(self):
        queryset = super().get_queryset().select_related('repository', 'branch').prefetch_related('file_changes')
        message_contains = self.request.query_params.get('message_contains')
        file_path_contains = self.request.query_params.get('file_path_contains')

        if message_contains and file_path_contains:
            return queryset.filter(
                Q(message__icontains=message_contains) |
                Q(file_changes__path__icontains=file_path_contains)
            ).distinct()
        elif message_contains:
            return queryset.filter(message__icontains=message_contains)
        elif file_path_contains:
            return queryset.filter(file_changes__path__icontains=file_path_contains).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_empty_paginated_response(self, message):
        try:
            paginator = self.pagination_class()
            return paginator.get_empty_paginated_response(message)
        except Exception as e:
            logger.error(f"Error in get_empty_paginated_response: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['GET'])
    def latest_commit(self, request):
        try:
            branch_id = request.query_params.get('branch_id')

            if not branch_id:
                return Response({"detail": "BranchID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

            queryset = Commit.objects.filter(branch__id=branch_id)
            latest_commit = queryset.order_by('-revision').first()

            if not latest_commit:
                return Response({"detail": "No commits found for the specified criteria."},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(latest_commit)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error in latest_commit: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['GET'])
    def file_changes(self, request, pk=None):
        try:
            filter_kind = request.query_params.get('kind')
            filter_actions = request.query_params.getlist('action')
            filter_suffixes = request.query_params.getlist('suffix')

            commit = self.get_object()
            file_changes = FileChange.objects.filter(commit=commit)

            if filter_kind:
                file_changes = file_changes.filter(kind=filter_kind)

            if filter_actions:
                file_changes = file_changes.filter(action__in=filter_actions)

            if filter_suffixes:
                suffix_filters = [Q(path__endswith=f'.{suffix}') for suffix in filter_suffixes]
                file_changes = file_changes.filter(reduce(or_, suffix_filters))

            page = self.paginate_queryset(file_changes)
            if page is not None:
                serializer = FileChangeQuerySerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = FileChangeQuerySerializer(file_changes, many=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error in file_changes: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['GET'])
    def authors(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            authors = queryset.values('author').annotate(
                max_id=Max('id')
            ).values_list('author', flat=True)
            return Response(authors)

        except Exception as e:
            logger.error(f"Error in authors: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommitSearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Commit.objects.all()
    serializer_class = CommitQuerySerializerS
    pagination_class = CustomPagination
    filterset_class = CommitFilter
    ordering_fields = ['revision', 'date', 'author']
