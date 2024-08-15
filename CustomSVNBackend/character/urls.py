from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views.character_query_views import CharacterQueryViewSet, CharacterCommandViewSet
from .api_views.tag_views import CharacterTagQueryViewSet, CharacterTagCommandViewSet
from .views import GenderViewSet, RaceViewSet, CharacterViewSet, ThumbnailViewSet, TagViewSet, ItemViewSet, \
    ItemAttributeViewSet, CharacterItemViewSet, CharacterItemAttributeViewSet, get_max_thumbnails

router = DefaultRouter()
router.register(r'genders', GenderViewSet)
router.register(r'races', RaceViewSet)
router.register(r'tags', TagViewSet)
router.register(r'items', ItemViewSet)
router.register(r'itemattributes', ItemAttributeViewSet)
router.register(r'characters', CharacterViewSet)
router.register(r'characteritems', CharacterItemViewSet)
router.register(r'characteritemattributes', CharacterItemAttributeViewSet)
router.register(r'thumbnails', ThumbnailViewSet)
router.register(r'_characters/query', CharacterQueryViewSet, basename='character-query')
router.register(r'_characters/command', CharacterCommandViewSet, basename='character-command')
router.register('_charactertags/query', CharacterTagQueryViewSet, basename='charactertag-query')
router.register('_charactertags/command', CharacterTagCommandViewSet, basename='charactertag-command')

urlpatterns = [
    path('', include(router.urls)),
    path('max-thumbnails/', get_max_thumbnails, name='max-thumbnails'),
]
