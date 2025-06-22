from django.contrib import admin
from .models import Return, ReturnItem

@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ['id', 'return_type', 'reference_id', 'date', 'is_damaged', 'get_total_quantity']

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())
    get_total_quantity.short_description = 'Total Quantity'


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_return_id', 'product', 'quantity']

    def get_return_id(self, obj):
        return obj.return_record.id
    get_return_id.short_description = 'Return ID'
