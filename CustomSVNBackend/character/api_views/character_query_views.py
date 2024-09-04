from rest_framework import mixins, viewsets

from character.CustomPaginations import CustomPagination
from character._serializers.character_serializers import CharacterQueryCommonSerializer, CharacterCommandSerializer
from character.models import Character


# 查询视图
class CharacterQueryViewSet(mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    '''
    CharacterQueryViewSet ---
    '''
    queryset = Character.objects.all()
    serializer_class = CharacterQueryCommonSerializer
    pagination_class = CustomPagination


# 写入视图
class CharacterCommandViewSet(
    # mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Character.objects.all()
    serializer_class = CharacterCommandSerializer

    def perform_create(self, serializer):
        print('before-perform_create')
        super().perform_create(serializer)
        print('after-perform_create')

    def perform_update(self, serializer):
        if serializer.is_valid():
            print(serializer.validated_data)

        print('before-perform_update')
        super().perform_update(serializer)
        print('after-perform_update')
