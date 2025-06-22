from rest_framework import serializers
from sales.models import Sale, SaleItem

class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'subtotal']

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'customer', 'invoice_no', 'date',
            'total_amount', 'payment_method', 'paid_amount',
            'due_amount', 'packing_charge', 'delivery_charge',
            'advance_payment', 'note', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sale = Sale.objects.create(**validated_data)
        for item_data in items_data:
            SaleItem.objects.create(sale=sale, **item_data)
            # Update stock (reduce)
            product = item_data['product']
            product.current_stock -= item_data['quantity']
            product.save()
        return sale

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        instance.customer = validated_data.get('customer', instance.customer)
        instance.invoice_no = validated_data.get('invoice_no', instance.invoice_no)
        instance.total_amount = validated_data.get('total_amount', instance.total_amount)
        instance.payment_method = validated_data.get('payment_method', instance.payment_method)
        instance.paid_amount = validated_data.get('paid_amount', instance.paid_amount)
        instance.due_amount = validated_data.get('due_amount', instance.due_amount)
        instance.packing_charge = validated_data.get('packing_charge', instance.packing_charge)
        instance.delivery_charge = validated_data.get('delivery_charge', instance.delivery_charge)
        instance.advance_payment = validated_data.get('advance_payment', instance.advance_payment)
        instance.note = validated_data.get('note', instance.note)
        instance.save()

        # Updating Sale Items:
        # Simplest: delete old items and create new
        instance.items.all().delete()
        for item_data in items_data:
            SaleItem.objects.create(sale=instance, **item_data)
            product = item_data['product']
            product.current_stock -= item_data['quantity']
            product.save()
        return instance