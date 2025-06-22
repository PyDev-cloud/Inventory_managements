from django.urls import path
from .import views
from .views import (
    BankAccountListView, BankAccountCreateView, BankAccountUpdateView, BankAccountDeleteView,
    BkashAccountCreateView,BkashAccountListView,BkashAccountDeleteView,BkashAccountUpdateView,
    CashAccountListView,CashAccountDeleteView,CashAccountUpdateView,CashAccountCreateView,
    EmployeeListView, EmployeeCreateView, EmployeeUpdateView, EmployeeDeleteView,
    SalarySheetListView, SalarySheetCreateView, SalarySheetUpdateView, SalarySheetDeleteView,
  
    ExpenseListView, ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView,SalaryPaymentCreateView,ExpencePaymentCreateView,InvestMentCreateView,get_salary_structure,
    WithdrawalCreateView,FundTransferCreateView,AdvancePaymentCreateView,SalaryPaymentListView,ExpensePaymentListView,InvestMentListView,WithdrawalListView,
    FundTransferListView,AdvancePaymentListView
)
app_name = 'accounts'
urlpatterns = [
    path('bankaccounts/', BankAccountListView.as_view(), name='bankaccount_list'),
    path('bankaccounts/add/', BankAccountCreateView.as_view(), name='bankaccount_create'),
    path('bankaccounts/<int:pk>/edit/', BankAccountUpdateView.as_view(), name='bankaccount_update'),
    path('bankaccounts/<int:pk>/delete/', BankAccountDeleteView.as_view(), name='bankaccount_delete'),

    
    path('bkashaccounts/', BkashAccountListView.as_view(), name='bkashaccount_list'),
    path('bkashaccounts/add/', BkashAccountCreateView.as_view(), name='bkashaccount_create'),
    path('bkashaccounts/<int:pk>/edit/', BkashAccountUpdateView.as_view(), name='bkashaccount_update'),
    path('bkashaccounts/<int:pk>/delete/', BkashAccountDeleteView.as_view(), name='bkashaccount_delete'),


    path('cash/', CashAccountListView.as_view(), name='cashaccount-list'),
    path('cash/create/', CashAccountCreateView.as_view(), name='cashaccount-create'),
    path('cash/<int:pk>/edit/', CashAccountUpdateView.as_view(), name='cashaccount-update'),
    path('cash/<int:pk>/delete/', CashAccountDeleteView.as_view(), name='cashaccount-delete'),



    path('employees/', EmployeeListView.as_view(), name='employee_list'),
    path('employees/add/', EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee_delete'),
    path('salary_payment_list/',SalaryPaymentListView.as_view(),name="salary_payment_list"),
    path('Salary-pament/', SalaryPaymentCreateView.as_view(), name='payment_salary'),
    path('api/get-salary-structure-from-sheet/<int:sheet_id>/', views.get_salary_structure_from_sheet, name='get_salary_structure_from_sheet'),
    
    

    path('salary-structures/', views.SalaryStructureListView.as_view(), name='salarystructure_list'),
    path('salary-structures/create/', views.SalaryStructureCreateView.as_view(), name='salarystructure_create'),
    path('salary-structures/<int:pk>/edit/', views.SalaryStructureUpdateView.as_view(), name='salarystructure_edit'),
    path('salary-structures/<int:pk>/delete/', views.SalaryStructureDeleteView.as_view(), name='salarystructure_delete'),
    path('api/get-salary-structure/<int:employee_id>/', views.get_salary_structure, name='get_salary_structure'),

    path('salarysheets/', SalarySheetListView.as_view(), name='salarysheet_list'),
    path('salarysheets/add/', SalarySheetCreateView.as_view(), name='salarysheet_create'),
    path('salarysheets/<int:pk>/edit/', SalarySheetUpdateView.as_view(), name='salarysheet_update'),
    path('salarysheets/<int:pk>/delete/', SalarySheetDeleteView.as_view(), name='salarysheet_delete'),
    
    

    

    path('expenses/', ExpenseListView.as_view(), name='expense_list'),
    path('expenses/add/', ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/edit/', ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/<int:pk>/delete/', ExpenseDeleteView.as_view(), name='expense_delete'),
    path('Expanse-pament/', ExpencePaymentCreateView.as_view(), name='payment_expanse'),
    path('expense-payments_list/', ExpensePaymentListView.as_view(), name='expense_payment_list'),


     path('investment-list/', InvestMentListView.as_view(), name='investment_list'),
    path('investment/',InvestMentCreateView.as_view(),name="investment_create"),
    path('withdrawals/', WithdrawalListView.as_view(), name='withdrawal_list'),
    path('withdrawal_create/',WithdrawalCreateView.as_view(),name="withdrawal_create"),
    path('fundtransfers/', FundTransferListView.as_view(), name='fundtransfer_list'),
    path('Fund_Transfer/',FundTransferCreateView.as_view(),name="fund_transfer"),
     path('advance-payments/', AdvancePaymentListView.as_view(), name='advance_payment_list'),
    path('Advance-Payment/',AdvancePaymentCreateView.as_view(),name='Advance_Payment')
]