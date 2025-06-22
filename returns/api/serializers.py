from rest_framework import serializers
from returns.models import Return, ReturnItem

class ReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        fields = '__all__'

class ReturnSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)

    class Meta:
        model = Return
        fields = ['id', 'return_type', 'source', 'date', 'note', 'total_amount', 'items']
