from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order
from inventory.models import Product

@receiver(pre_save, sender=Order)
def deduct_inventory_only_on_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # নতুন অর্ডার, কিছু করব না

    previous = Order.objects.get(pk=instance.pk)
    if previous.status != 'confirmed' and instance.status == 'confirmed':
        for item in instance.order_items.all():
            product = item.product
            qty_to_deduct = item.quantity

            if product.office_stock >= qty_to_deduct:
                product.office_stock -= qty_to_deduct
            else:
                remaining = qty_to_deduct - product.office_stock
                product.office_stock = 0
                product.godown_stock -= remaining

            product.save()