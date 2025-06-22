from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Purchase, PurchaseItem, PurchasePayment, Supplier
from django.db.models import Sum



@receiver([post_save, post_delete], sender=Purchase)
@receiver([post_save, post_delete], sender=PurchasePayment)
def update_supplier_on_change(sender, instance, **kwargs):
    if isinstance(instance, Purchase):
        supplier = instance.supplier
    elif isinstance(instance, PurchasePayment):
        supplier = instance.purchase.supplier
    else:
        return
    
    


def update_product_stock(product):
    total_remaining = PurchaseItem.objects.filter(product=product).aggregate(
        total=Sum('remaining_quantity')
    )['total'] or 0
    product.current_stock = total_remaining
    product.save()



