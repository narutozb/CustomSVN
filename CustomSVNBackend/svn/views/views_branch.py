from xmlrpc.client import Fault

from django.core.paginator import EmptyPage
from django_filters import rest_framework as filters

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from django.db.models import Q
from functools import reduce
from operator import or_

from svn._serializers.serializer_branch import BranchQuerySerializer
from svn.models import Branch
from svn.pagination import CustomPagination


class BranchFilter(filters.FilterSet):
    name = filters.CharFilter()
    name_contains = filters.CharFilter(field_name='name', lookup_expr='icontains')
    repo_name = filters.CharFilter(field_name='repository__name')
    repo_id = filters.NumberFilter(field_name='repository__id')

    class Meta:
        model = Branch
        fields = ["name", 'repo_name', 'repo_id', 'name_contains']


class BranchQueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchQuerySerializer
    pagination_class = CustomPagination
    filterset_class = BranchFilter

    @action(detail=False, methods=['GET'])
    def get_root_tags(self, request):
        '''
        获取所有根标签.
        也就是那些只有一层的标签
        例如：/tags, /branches, /trunk, /test, /test1
        但是不包括那些有多层的标签

        可以根据repo_id来过滤结果,并且支持过滤多个repo_id,例如：
        ?repo_id=1&repo_id=2

        '''

        repo_id_list = request.query_params.getlist('repo_id')

        tags = Branch.objects.filter(
            Q(name__regex=r'^/[^/]+$')
        )

        if repo_id_list:
            tags = tags.filter(repository__id__in=repo_id_list)

        return Response(self.get_serializer(tags, many=True).data)
