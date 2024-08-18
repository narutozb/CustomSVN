from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from character.CustomPaginations import CustomPagination
from character._serializers.character_gender_serializers import CharacterGenderSerializer

from character.models import Gender


class CharacterGenderQueryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Gender.objects.all()
    serializer_class = CharacterGenderSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', ]
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
            ],
            'edit_fields': [
                {'key': 'name', 'label': 'Name', 'type': 'text', 'required': True},
                {'key': 'description', 'label': 'Description', 'type': 'textarea', 'required': False},
            ],
        })

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 处理搜索
        search = request.query_params.get('search')
        search_fields = request.query_params.get('search_fields')
        use_regex = request.query_params.get('use_regex', 'false').lower() == 'true'

        if search and search_fields:
            or_condition = Q()
            for field in search_fields.split(','):
                if use_regex:
                    or_condition |= Q(**{f"{field}__regex": search})
                else:
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


class CharacterGenderCommandViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Gender.objects.all()
    serializer_class = CharacterGenderSerializer
    pagination_class = CustomPagination
