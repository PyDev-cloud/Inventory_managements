# Admin for inventory# inventory/admin.py
from django.contrib import admin
from .models import Supplier, Product, Purchase, PurchaseItem, PurchasePayment

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'supplier', 'date', 'total_amount', 'paid_amount', 'due_amount', 'payment_method')
    search_fields = ('invoice_no', 'supplier__name')
    inlines = [PurchaseItemInline]

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'total_purchase', 'total_payment', 'advance_payment', 'due_amount')
    search_fields = ('name', 'phone')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'purchase_price', 'office_stock', 'godown_stock', 'current_stock')
    search_fields = ('name',)

class PurchasePaymentAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'amount', 'method', 'date')
    search_fields = ('purchase__invoice_no',)

admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(PurchasePayment, PurchasePaymentAdmin)