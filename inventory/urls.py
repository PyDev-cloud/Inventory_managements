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
    PurchaseDuePaymentView,
    CategoryListView,CategoryCreateView,CategoryUpdateView,CategoryDeleteView,
    SubCategoryListView,SubCategoryCreateView,SubCategoryUpdateView,SubCategoryDeleteView
)
from . import views

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







    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category-add'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category-edit'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),

    # SubCategory URLs
    path('subcategories/', SubCategoryListView.as_view(), name='subcategory-list'),
    path('subcategories/add/', SubCategoryCreateView.as_view(), name='subcategory-add'),
    path('subcategories/<int:pk>/edit/', SubCategoryUpdateView.as_view(), name='subcategory-edit'),
    path('subcategories/<int:pk>/delete/', SubCategoryDeleteView.as_view(), name='subcategory-delete'),
    path('dashboard2/', views.dashboard, name='dashboard'),
    # Product URLs
    path('products_ecommerch/', views.products, name='products_ecommerch'),
    path('products_ecommerch/add/', views.product_add, name='products_ecommerch_add'),
    path('products_ecommerch/edit/<int:pk>/', views.product_edit, name='products_ecommerch_edit'),
    path('products_ecommerch/delete/<int:pk>/', views.product_delete, name='products_ecommerch_delete'),

    # Order URLs
    path('orders/', views.orders, name='orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    # Customer URLs
    path('customers/', views.customers, name='customers'),

]