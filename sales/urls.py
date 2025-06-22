from django.urls import path
from .views import SaleListView, SaleCreateView, SaleDetailView,CustomerListView,CustomerCreateView,SaleDuePaymentView

app_name = 'sales'

urlpatterns = [
    path('customer/', CustomerListView.as_view(), name='customer_list'),
    path('customer/create/', CustomerCreateView.as_view(), name='customer_create'),
    path('sales_List/', SaleListView.as_view(), name='sale_list'),
    path('create/', SaleCreateView.as_view(), name='sale_create'),
    path('<int:pk>/', SaleDetailView.as_view(), name='sale_detail'),
    path('sale/<int:pk>/pay-due/', SaleDuePaymentView.as_view(), name='sale_pay_due'),
]