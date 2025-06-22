from rest_framework.routers import DefaultRouter
from returns.api.views import ReturnViewSet, ReturnItemViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'returns', ReturnViewSet)
router.register(r'return-items', ReturnItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
