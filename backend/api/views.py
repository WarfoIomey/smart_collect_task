from rest_framework import viewsets

from .serializers import (
    PayoutReadSerializer,
    PayoutCreateSerializer,
    PayoutUpdateSerializer
)
from payouts.models import Payout


class PayoutViewSet(viewsets.ModelViewSet):
    queryset = Payout.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return PayoutCreateSerializer
        if self.action == 'partial_update':
            return PayoutUpdateSerializer
        return PayoutReadSerializer
