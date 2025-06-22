# Models for inventory# inventory/models.py
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    total_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advance_payment=models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return self.name

    @property
    def total_purchase(self):
        return self.purchase_set.aggregate(total=Sum('total_amount'))['total'] or 0

    @property
    def due_amount(self):
        return self.total_purchase - self.total_payment if self.total_purchase > self.total_payment else 0

    

    def get_purchase_summary_by_date(self, start_date, end_date):
        purchases = self.purchase_set.filter(date__range=(start_date, end_date))
        payments = PurchasePayment.objects.filter(purchase__supplier=self, date__range=(start_date, end_date))

        total_purchase = purchases.aggregate(total=Sum('total_amount'))['total'] or 0
        total_payment = payments.aggregate(total=Sum('amount'))['total'] or 0
        due_amount = max(total_purchase - total_payment, 0)
        advance = max(total_payment - total_purchase, 0)

        return {
            'total_purchase': total_purchase,
            'total_payment': total_payment,
            'due_amount': due_amount,
            'advance_payment': advance
        }
    

class Product(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50)
    current_stock = models.IntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    office_stock = models.IntegerField(default=0)
    godown_stock = models.IntegerField(default=0)
    damage_stock=models.IntegerField(default=0)


    def save(self, *args, **kwargs):
        self.current_stock = self.office_stock + self.godown_stock
        super().save(*args, **kwargs)
    
    @property
    def calculated_stock(self):
        return PurchaseItem.objects.filter(product=self).aggregate(
            total=Sum('remaining_quantity')
        )['total'] or 0
    def __str__(self):
        return self.name
    

class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    invoice_no = models.CharField(max_length=100, unique=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2,default=0,blank=True)
    payment_method = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('bank', 'Bank'), ('bkash', 'Bkash')])
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            today = timezone.now().date()
            date_str = today.strftime('%Y%m%d')
            # Count how many sales already exist today
            count_today = Purchase.objects.filter(date=today).count() + 1
            serial = str(count_today).zfill(4)  # pad with leading zeros
            self.invoice_no = f"INV-{date_str}-{serial}"
        super().save(*args, **kwargs)
    def __str__(self):
        return self.invoice_no

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_quantity = models.IntegerField(default=0)
    

    def subtotal(self):
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_quantity = self.quantity  # নতুন রেকর্ড হলে initialize
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class PurchasePayment(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('bank', 'Bank'), ('bkash', 'Bkash')])
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.amount} on {self.date}"
    





