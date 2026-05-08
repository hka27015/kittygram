from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from cat_of_day.views import DailyCatViewSet, PredictionViewSet
from cats.views import (
    CatViewSet,
    UserViewSet,
    AchievementViewSet
)

router = DefaultRouter()
router.register('cats', CatViewSet)
router.register('users', UserViewSet)
router.register('achievements', AchievementViewSet)
router.register('cat-of-day', DailyCatViewSet, basename="cat-of-day")
router.register('predictions', PredictionViewSet, basename="predictions")


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
]