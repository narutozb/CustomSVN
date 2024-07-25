import json

from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Gender, Race, Tag, Item, ItemAttribute, Character, CharacterItem, CharacterItemAttribute, Thumbnail
from .serializers import GenderSerializer, RaceSerializer, TagSerializer, ItemSerializer, ItemAttributeSerializer, \
    CharacterSerializer, CharacterItemSerializer, CharacterItemAttributeSerializer, ThumbnailSerializer


class GenderViewSet(viewsets.ModelViewSet):
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer


class RaceViewSet(viewsets.ModelViewSet):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemAttributeViewSet(viewsets.ModelViewSet):
    queryset = ItemAttribute.objects.all()
    serializer_class = ItemAttributeSerializer


class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        instance = serializer.save()
        self._handle_thumbnails(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._handle_thumbnails(instance)

    def _handle_thumbnails(self, instance):
        thumbnails = self.request.data.get('thumbnails')
        new_thumbnails = self.request.FILES.getlist('new_thumbnails')

        if thumbnails:
            thumbnail_ids = json.loads(thumbnails)
            instance.thumbnails.exclude(id__in=thumbnail_ids).delete()

        for thumbnail in new_thumbnails:
            Thumbnail.objects.create(character=instance, image=thumbnail)


class CharacterItemViewSet(viewsets.ModelViewSet):
    queryset = CharacterItem.objects.all()
    serializer_class = CharacterItemSerializer


class CharacterItemAttributeViewSet(viewsets.ModelViewSet):
    queryset = CharacterItemAttribute.objects.all()
    serializer_class = CharacterItemAttributeSerializer


class ThumbnailViewSet(viewsets.ModelViewSet):
    queryset = Thumbnail.objects.all()
    serializer_class = ThumbnailSerializer


@api_view(['GET'])
def get_max_thumbnails(request):
    return Response({'max_thumbnails': settings.MAX_THUMBNAILS_PER_CHARACTER})
