from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenderViewSet, RaceViewSet, CharacterViewSet, ThumbnailViewSet, TagViewSet, ItemViewSet, \
    ItemAttributeViewSet, CharacterItemViewSet, CharacterItemAttributeViewSet

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

urlpatterns = [
    path('', include(router.urls)),
]