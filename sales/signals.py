from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale, SalePayment

@receiver(post_save, sender=Sale)
@receiver(post_save, sender=SalePayment)
def update_customer_financials(sender, instance, **kwargs):
    instance.customer.calculate_financials() if sender == Sale else instance.sale.customer.calculate_financials()




