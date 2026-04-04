from rest_framework import viewsets, filters
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend

from .models import Cat, Achievement, User
from .serializers import CatSerializer, UserSerializer, AchievementSerializer
from .permission import OwnerOrReadOnly, ReadOnly
from .throttling import WorkingHoursRateThrottle
from .pagination import CatsPagination

class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer

    permission_classes = (OwnerOrReadOnly,)

    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)

    throttle_scope = 'medium_request'

    pagination_class = CatsPagination

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)

    filterset_fields = ('color', 'birth_year')

    search_fields = ('^name',)

    ordering_fields = ('name', 'birth_year')

    ordering = ('birth_year',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = Cat.objects.all()

        color = self.request.query_params.get('color')
        if color is not None:
            queryset = queryset.filter(color=color)
        return queryset

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
