from django.utils.html import escape
from django.utils.safestring import mark_safe
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, time
import operator
from functools import reduce

from svn._serializers.serializer_commit import CommitQuerySerializerS
from svn.models import Commit, FileChange
from svn.pagination import CustomPagination
from svn.views.views_commit import CommitFilter


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


class HighlightedFileChangeSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()


    class Meta:
        model = FileChange
        fields = ['id', 'commit', 'path', 'action', 'kind',]

    def _highlight_text(self, text, search_term):
        if not search_term or not text:
            return text
        highlighted = text.replace(search_term, f'<mark>{escape(search_term)}</mark>')
        return mark_safe(highlighted)

    def get_path(self, obj):
        return self._highlight_text(obj.path, self.context.get('file_path_contains'))

    def get_action(self, obj):
        return self._highlight_text(obj.action, self.context.get('file_path_contains'))

    def get_kind(self, obj):
        return self._highlight_text(obj.kind, self.context.get('file_path_contains'))


class HighlightedCommitSerializer(CommitQuerySerializerS):
    repo_name = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    file_changes = serializers.SerializerMethodField()

    def _highlight_text(self, text, search_term):
        if not search_term or not text:
            return text
        highlighted = text.replace(search_term, f'<mark>{escape(search_term)}</mark>')
        return mark_safe(highlighted)

    def get_repo_name(self, obj):
        return self._highlight_text(obj.repository.name, self.context.get('repo_name_contains'))

    def get_message(self, obj):
        return self._highlight_text(obj.message, self.context.get('message_contains'))

    def get_branch_name(self, obj):
        return self._highlight_text(obj.branch.name if obj.branch else '', self.context.get('branch_name_contains'))

    def get_file_changes(self, obj):
        file_path_contains = self.context.get('file_path_contains')
        only_matched = self.context.get('only_matched_file_changes', False)

        file_changes = obj.file_changes.all()

        if only_matched and file_path_contains:
            file_changes = [fc for fc in file_changes if file_path_contains.lower() in fc.path.lower()]

        serializer = HighlightedFileChangeSerializer(file_changes, many=True, context=self.context)
        return serializer.data

    class Meta(CommitQuerySerializerS.Meta):
        fields = CommitQuerySerializerS.Meta.fields + [
            'repo_name', 'message',
            'branch_name', 'file_changes'
        ]


class HighlightedCommitViewSet(viewsets.ModelViewSet):
    queryset = Commit.objects.all()
    serializer_class = HighlightedCommitSerializer
    pagination_class = CustomPagination
    filterset_class = CommitFilter
    ordering_fields = ['revision', 'date', 'author']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'repo_name_contains': self.request.query_params.get('repo_name_contains', ''),
            'message_contains': self.request.query_params.get('message_contains', ''),
            'branch_name_contains': self.request.query_params.get('branch_name_contains', ''),
            'file_path_contains': self.request.query_params.get('file_path_contains', ''),
            'only_matched_file_changes': self.request.query_params.get('only_matched_file_changes',
                                                                       '').lower() == 'true',
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset().select_related('repository', 'branch').prefetch_related('file_changes')
        message_contains = self.request.query_params.get('message_contains')
        file_path_contains = self.request.query_params.get('file_path_contains')
        only_matched_file_changes = self.request.query_params.get('only_matched_file_changes', '').lower() == 'true'

        if message_contains and file_path_contains:
            queryset = queryset.filter(
                Q(message__icontains=message_contains) |
                Q(file_changes__path__icontains=file_path_contains)
            ).distinct()
        elif message_contains:
            queryset = queryset.filter(message__icontains=message_contains)
        elif file_path_contains:
            queryset = queryset.filter(file_changes__path__icontains=file_path_contains).distinct()

        if only_matched_file_changes and file_path_contains:
            queryset = queryset.filter(file_changes__path__icontains=file_path_contains)

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
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)