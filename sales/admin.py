from django.contrib import admin
from .models import Customer, Sale, SaleItem, SalePayment


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'total_sales', 'total_payment', 'advance_payment', 'due_amount')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('name',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'customer', 'date', 'total_amount', 'paid_amount', 'due_amount', 'payment_method')
    list_filter = ('date', 'payment_method')
    search_fields = ('invoice_no', 'customer__name')
    inlines = [SaleItemInline, SalePaymentInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('sale__date', 'product')
    search_fields = ('sale__invoice_no', 'product__name')


@admin.register(SalePayment)
class SalePaymentAdmin(admin.ModelAdmin):
    list_display = ('sale', 'date', 'amount', 'method')
    list_filter = ('method', 'date')
    search_fields = ('sale__invoice_no',)
