from django.contrib import admin
from .models import (
    Category, SubCategory, CustomerUser,
    Cart, CartItem, Order, OrderItem,
    ShippingInfo, Payment
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category')
    list_filter = ('category',)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)


@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')
    search_fields = ('user__username', 'phone')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at')
    inlines = [CartItemInline]
    list_filter = ('created_at',)
    search_fields = ('customer__user__username',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__user__username',)
    inlines = [OrderItemInline]


@admin.register(ShippingInfo)
class ShippingInfoAdmin(admin.ModelAdmin):
    list_display = ('order', 'full_name', 'phone', 'city', 'postal_code')
    search_fields = ('full_name', 'phone', 'city', 'order__id')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'amount', 'paid_at')
    list_filter = ('method', 'paid_at')
    search_fields = ('order__id',)
