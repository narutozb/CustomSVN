from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenderViewSet, RaceViewSet, CharacterViewSet, ThumbnailViewSet

router = DefaultRouter()
router.register(r'genders', GenderViewSet)
router.register(r'races', RaceViewSet)
router.register(r'characters', CharacterViewSet)
router.register(r'thumbnails', ThumbnailViewSet)

urlpatterns = [
    path('', include(router.urls)),
]