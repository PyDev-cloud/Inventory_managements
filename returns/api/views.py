from rest_framework import viewsets
from returns.models import Return, ReturnItem
from returns.api.serializers import ReturnSerializer, ReturnItemSerializer

class ReturnViewSet(viewsets.ModelViewSet):
    queryset = Return.objects.all().order_by('-date')
    serializer_class = ReturnSerializer

class ReturnItemViewSet(viewsets.ModelViewSet):
    queryset = ReturnItem.objects.all()
    serializer_class = ReturnItemSerializer
