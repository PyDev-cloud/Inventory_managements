from django.contrib import admin
from .models import (
    BankAccount,
    CashAccount,
    Employee,
    SalarySheet,

    Expense
)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'bank_name', 'account_number', 'balance')
    search_fields = ('name', 'bank_name', 'account_number')


@admin.register(CashAccount)
class CashAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'phone')
    search_fields = ('name', 'phone')


@admin.register(SalarySheet)
class SalarySheetAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'basic_salary', 'advance_salary', 'bonus',  'total_salary',  'payment_date')
    list_filter = ('month', 'payment_date')
    search_fields = ('employee__name',)





@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description',)
    list_filter = ('description',)
    search_fields = ('description',)
