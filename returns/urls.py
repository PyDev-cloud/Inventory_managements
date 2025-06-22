from django.urls import path
from . import views
from .views import ReturnListView, ReturnDetailView, ReturnCreateView, ReturnUpdateView
app_name = 'returns'

urlpatterns = [
    path('return-list/', ReturnListView.as_view(), name='return_list'),
    path('create/', ReturnCreateView.as_view(), name='return_add'),
    path('<int:pk>/', ReturnDetailView.as_view(), name='return_detail'),
    path('<int:pk>/edit/', ReturnUpdateView.as_view(), name='return_edit'),
    path('ajax/get-unit-price/', views.get_unit_price, name='get_unit_price'),
]