from django.urls import path
from .views import (
    SupplierListView,
    ProductListView,
    PurchaseListView,
    PurchaseCreateView,
    PurchaseDetailView,
    SupplierCreateView,
    ProductCreateView,
    TransferStockView,
    PurchaseDuePaymentView
)

app_name = 'inventory'

urlpatterns = [
    path('suppliers/', SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/create/', SupplierCreateView.as_view(), name='supplier_create'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('purchases/', PurchaseListView.as_view(), name='purchase_list'),
    path('purchases/create/', PurchaseCreateView.as_view(), name='purchase_create'),
    path('purchases/<int:pk>/', PurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchase/<int:pk>/pay-due/', PurchaseDuePaymentView.as_view(), name='purchase_pay_due'),
    path('transfer-stock/', TransferStockView.as_view(), name='transfer_stock'),
]