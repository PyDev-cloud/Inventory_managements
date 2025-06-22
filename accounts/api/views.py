from rest_framework import viewsets
from accounts.models import BankAccount, CashAccount, Employee, SalarySheet, Transaction, Expense
from .serializers import (
    BankAccountSerializer, CashAccountSerializer, EmployeeSerializer,
    SalarySheetSerializer, TransactionSerializer, ExpenseSerializer
)

class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

class CashAccountViewSet(viewsets.ModelViewSet):
    queryset = CashAccount.objects.all()
    serializer_class = CashAccountSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class SalarySheetViewSet(viewsets.ModelViewSet):
    queryset = SalarySheet.objects.all()
    serializer_class = SalarySheetSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
