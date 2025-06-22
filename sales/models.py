from django.db import models
from django.utils import timezone
from inventory.models import Product  

class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advance_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def calculate_financials(self):
        from django.db.models import Sum
        from .models import Sale, SalePayment

        # Total Sales Calculation (including packing + delivery charge)
        sales = Sale.objects.filter(customer=self)
        total_sales_amount = sum([sale.total_amount for sale in sales])

        # Total Payment Calculation (SalePayment only)
        payment_from_payments = SalePayment.objects.filter(sale__customer=self).aggregate(Sum('amount'))['amount__sum'] or 0

        # There is no advance_payment in the Sale model, so use Customer's advance_payment
        payment_from_advance = self.advance_payment  # Customer

        total_payment = payment_from_payments + payment_from_advance

        # Assign to fields
        self.total_sales = total_sales_amount
        self.total_payment = total_payment

        # Due or Advance Calculation
        if total_sales_amount > total_payment:
            self.due_amount = total_sales_amount - total_payment
            self.advance_payment = 0
        else:
            self.due_amount = 0
            self.advance_payment = total_payment - total_sales_amount

        self.save()
    def __str__(self):
        return self.name
        
        

class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    invoice_no = models.CharField(max_length=100,unique=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2,default=0)
    payment_method = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('bank', 'Bank'), ('bkash', 'Bkash')])
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_amount = models.DecimalField(max_digits=12, decimal_places=2)
    packing_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  
    note = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            today = timezone.now().date()
            date_str = today.strftime('%Y%m%d')
            # Count how many sales already exist today
            count_today = Sale.objects.filter(date=today).count() + 1
            serial = str(count_today).zfill(4)  # pad with leading zeros
            self.invoice_no = f"INV-{date_str}-{serial}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_no

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class SalePayment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('bank', 'Bank'), ('bkash', 'Bkash')])
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.amount} on {self.date}"