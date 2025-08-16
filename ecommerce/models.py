# ecommerce/models.py
from django.db import models
from django.contrib.auth.models import User
from inventory.models import Product

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# Inventory Product এর সাথে Category/Subcategory লিঙ্ক
class ProductCategoryLink(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    subcategory = models.ForeignKey('SubCategory', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/')
    description=models.TextField(max_length=500)
    previous_price=models.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True)
    selles_price=models.DecimalField(max_digits=6,decimal_places=2)


    def __str__(self):
        return f"{self.product.name} -> {self.category.name} / {self.subcategory.name if self.subcategory else ''}"


class CustomerUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.username


class Cart(models.Model):
    customer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, null=True,blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.customer}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductCategoryLink, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.product.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned')
    ]
    customer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE,null=True,blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField(blank=True, null=True)  # Add this
    payment_method = models.CharField(max_length=20, blank=True, null=True)  # Add this
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class ShippingInfo(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Shipping for Order {self.order.id}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('bkash', 'bKash')
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} via {self.method}"
