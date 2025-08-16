# ecommerce/urls.py
from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    AddToCartView,
    CartDetailView,
    CheckoutView,
    OrderSuccessView,
    RemoveFromCartView,
    IncreaseQuantityView,
    DecreaseQuantityView
)

app_name = "ecommerce"

urlpatterns = [
    # হোম/প্রোডাক্ট লিস্ট
    path("", ProductListView.as_view(), name="product_list"),

    # প্রোডাক্ট ডিটেইল
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),

    # কার্টে যোগ করা
    path('cart/add/<int:pk>/', AddToCartView.as_view(), name='add_to_cart'),

    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/increase/<int:item_id>/', IncreaseQuantityView.as_view(), name='increase_qty'),
    path('cart/decrease/<int:item_id>/', DecreaseQuantityView.as_view(), name='decrease_qty'),


    # কার্ট ডিটেইল
    path("cart/", CartDetailView.as_view(), name="cart_detail"),

    # চেকআউট
    path("checkout/", CheckoutView.as_view(), name="checkout"),

    # অর্ডার সফল পেজ
    path("order/success/<int:pk>/", OrderSuccessView.as_view(), name="order_success"),
]
