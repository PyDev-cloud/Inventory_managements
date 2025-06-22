from rest_framework.routers import DefaultRouter
from .views import (
    BankAccountViewSet, CashAccountViewSet, EmployeeViewSet,
    SalarySheetViewSet, TransactionViewSet, ExpenseViewSet
)

router = DefaultRouter()
router.register(r'bankaccounts', BankAccountViewSet)
router.register(r'cashaccounts', CashAccountViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'salarysheets', SalarySheetViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'expenses', ExpenseViewSet)

urlpatterns = router.urls
