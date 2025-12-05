from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PayoutViewSet


app_name = 'api'

router = DefaultRouter()

router.register(r'payouts', PayoutViewSet, basename='payouts')

urlpatterns = [
    path('', include(router.urls)),
]
