from rest_framework import routers
from django.urls import include, path
from .views import CustomUserViewSet


app_name = 'api'

router = routers.DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
