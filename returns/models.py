from django.db import models
from inventory.models import Product, Purchase, PurchaseItem, Supplier
from sales.models import Sale, SaleItem

class Return(models.Model):
    RETURN_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
    ]
    return_type = models.CharField(max_length=10, choices=RETURN_TYPE_CHOICES)
    reference_id =models.CharField(max_length=50)  # Purchase ID or Sale ID
    reason = models.TextField()
    is_damaged = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def get_total_amount(self):
        return sum(item.get_total() for item in self.items.all())
    def __str__(self):
        return f"{self.get_return_type_display()} Return - {self.date}" # type: ignore
    
    

class ReturnItem(models.Model):
    return_record = models.ForeignKey(Return, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def get_total(self):
        return self.quantity * self.unit_price
