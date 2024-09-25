import re
from datetime import datetime, time

from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import serializers, viewsets

from svn._serializers.serializer_commit import CommitQuerySerializerS
from svn.models import Commit, FileChange
from svn.pagination import CustomPagination


# svn/filters.py

class CommitFilter(filters.FilterSet):
    """
    FilterSet for the Commit model, defining various filtering options.
    """
    # 直接字段过滤器
    repo_name = filters.CharFilter(field_name='repository__name')
    message = filters.CharFilter()
    branch_name = filters.CharFilter(field_name='branch__name')
    revision = filters.NumberFilter()
    branch_id = filters.NumberFilter()
    repo_id = filters.NumberFilter(field_name='repository__id')

    # 包含关系过滤器
    repo_name_contains = filters.CharFilter(field_name='repository__name', lookup_expr='icontains')
    branch_name_contains = filters.CharFilter(field_name='branch__name', lookup_expr='icontains')

    # 范围过滤器
    revision_from = filters.NumberFilter(field_name='revision', lookup_expr='gte')
    revision_to = filters.NumberFilter(field_name='revision', lookup_expr='lte')

    # 自定义方法过滤器
    authors = filters.CharFilter(method='filter_authors', label='authors')
    date_from = filters.DateFilter(method='filter_date_from', label='date_from')
    date_to = filters.DateFilter(method='filter_date_to', label='date_to')
    branch_ids = filters.CharFilter(method='filter_branch_ids', label='branch_ids')

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
            'revision', 'repo_name', 'message', 'branch_name',
            'repo_name_contains', 'branch_name_contains',
            'authors', 'date_from', 'date_to',
            'repo_id', 'branch_id', 'branch_ids',
            'revision_from', 'revision_to',
        ]


class _HighlightedFileChangeSerializer(serializers.ModelSerializer):
    """
    Serializer for FileChange model with highlighted fields based on search terms.
    """
    path = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()

    class Meta:
        model = FileChange
        fields = ['id', 'commit', 'path', 'action', 'kind']

    def _highlight_text(self, text, search_term):
        if not search_term or not text:
            return text

        # 使用正则表达式进行不区分大小写的搜索和替换
        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        highlighted = pattern.sub(lambda m: f'<mark>{escape(m.group())}</mark>', text)
        return mark_safe(highlighted)

    def get_path(self, obj):
        return self._highlight_text(obj.path, self.context.get('file_path_contains'))

    def get_action(self, obj):
        return obj.action
        # return self._highlight_text(obj.action, self.context.get('file_path_contains'))

    def get_kind(self, obj):
        return obj.kind
        # return self._highlight_text(obj.kind, self.context.get('file_path_contains'))


class HighlightedCommitSerializer(CommitQuerySerializerS):
    """
    Serializer for Commit model with highlighted fields and nested file changes.
    """
    repo_name = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    file_changes = serializers.SerializerMethodField()

    class Meta(CommitQuerySerializerS.Meta):
        fields = CommitQuerySerializerS.Meta.fields + [
            'repo_name', 'message',
            'branch_name', 'file_changes',
        ]

    def _highlight_text(self, text, search_term):
        """
        Highlights the search_term in the given text by wrapping it with <mark> tags.
        """
        if not search_term or not text:
            return text
        highlighted = text.replace(search_term, f'<mark>{escape(search_term)}</mark>')
        return mark_safe(highlighted)

    def get_repo_name(self, obj):
        return self._highlight_text(obj.repository.name, self.context.get('repo_name_contains'))

    def get_message(self, obj):
        return self._highlight_text(obj.message, self.context.get('message_contains'))

    def get_branch_name(self, obj):
        branch_name = obj.branch.name if obj.branch else ''
        return self._highlight_text(branch_name, self.context.get('branch_name_contains'))

    def get_file_changes(self, obj):
        file_changes = obj.file_changes.all()
        context = self.context.copy()
        # 确保 file_path_contains 参数被传递给 FileChange 序列化器
        context['file_path_contains'] = self.context.get('file_path_contains') or self.context.get('message_contains')
        serializer = _HighlightedFileChangeSerializer(file_changes, many=True, context=context)
        return serializer.data


# svn/views.py

class HighlightedCommitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and retrieving Commit instances with highlighting functionality.
    """
    queryset = Commit.objects.all()
    serializer_class = HighlightedCommitSerializer
    pagination_class = CustomPagination
    filterset_class = CommitFilter
    ordering_fields = ['revision', 'date', 'author']

    def get_serializer_context(self):
        """
        Adds additional context to the serializer, including the search terms for highlighting.
        """
        context = super().get_serializer_context()
        context.update({
            'repo_name_contains': self.request.query_params.get('repo_name_contains', ''),
            'message_contains': self.request.query_params.get('message_contains', ''),
            'branch_name_contains': self.request.query_params.get('branch_name_contains', ''),
            'file_path_contains': self.request.query_params.get('file_path_contains', ''),
        })
        return context

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        message_contains = self.request.query_params.get('message_contains', '')
        file_path_contains = self.request.query_params.get('file_path_contains', '')

        if message_contains or file_path_contains:
            q_objects = Q()
            if message_contains:
                q_objects |= Q(message__icontains=message_contains)
            if file_path_contains:
                q_objects |= Q(file_changes__path__icontains=file_path_contains)
            queryset = queryset.filter(q_objects).distinct()

        return queryset
