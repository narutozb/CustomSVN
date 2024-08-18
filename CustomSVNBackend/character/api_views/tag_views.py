from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from character.CustomPaginations import CustomPagination
from character._serializers.tag_serializers import CharacterTagSerializer
from character.models import Tag


class CharacterTagQueryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = CharacterTagSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = ['id']  # 默认排序

    def get_queryset(self):
        queryset = super().get_queryset()
        # 添加任何额外的查询逻辑
        return queryset

    @action(detail=False, methods=['GET'])
    def filter_options(self, request):
        return Response({
            'search_fields': self.search_fields,
            'ordering_fields': self.ordering_fields,
            'table_fields': [
                {'key': 'name', 'label': 'Name', 'sortable': True, 'editable': True},
                {'key': 'description', 'label': 'Description', 'sortable': False, 'editable': True},
                {'key': 'active', 'label': 'Active', 'sortable': True, 'editable': True},
                {'key': 'updated_at', 'label': 'UpdateAt', 'sortable': True, 'editable': False},
                {'key': 'updated_by', 'label': 'UpdateBy', 'sortable': True, 'editable': False},
                {'key': 'create_at', 'label': 'CreateAt', 'sortable': True, 'editable': False},
                {'key': 'create_by', 'label': 'CreateBy', 'sortable': True, 'editable': False},
            ],
            'edit_fields': [
                {'key': 'name', 'label': 'Name', 'type': 'text', 'required': True},
                {'key': 'description', 'label': 'Description', 'type': 'textarea', 'required': False},
                {'key': 'active', 'label': 'Active', 'type': 'switch', 'required': False},
            ],
        })

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 处理搜索
        search = request.query_params.get('search')
        search_fields = request.query_params.get('search_fields')

        if search and search_fields:
            or_condition = Q()
            for field in search_fields.split(','):
                or_condition |= Q(**{f"{field}__icontains": search})
            queryset = queryset.filter(or_condition)

        # 处理排序
        ordering = request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CharacterTagCommandViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = CharacterTagSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

