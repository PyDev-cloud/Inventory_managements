from django.db.models import Sum
from inventory.models import PurchaseItem

def update_product_stock(product):
    total_remaining = PurchaseItem.objects.filter(product=product).aggregate(
        total=Sum('remaining_quantity')
    )['total'] or 0
    product.current_stock = total_remaining
    product.save()
