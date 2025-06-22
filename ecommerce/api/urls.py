from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, SubCategoryViewSet,
    CartItemViewSet, OrderViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'cart', CartItemViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = router.urls