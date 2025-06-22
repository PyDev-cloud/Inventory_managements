from django import forms
from .models import BankAccount,BkashAccount, CashAccount, Employee, SalarySheet, Expense,SalaryPayment,ExpensePayment,InvestMent,Withdrawal,FundTransfer,AdvancePayment,salaryStructure
from datetime import datetime
from django.db.models import Sum



class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields ="__all__"


class BkashAccountForm(forms.ModelForm):
    class Meta:
        model = BkashAccount
        fields ="__all__"



class CashAccountForm(forms.ModelForm):
    class Meta:
        model = CashAccount
        fields = "__all__"

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = "__all__"

    

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description']


class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = salaryStructure
        fields = '__all__'


class SalarySheetForm(forms.ModelForm):
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        input_formats=['%Y-%m'],
        label='Month'
    )

    total_salary = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    payment_status = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean_month(self):
        month = self.cleaned_data['month']
        return month.replace(day=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paid_amount'].required = False

    class Meta:
        model = SalarySheet
        fields = '__all__'

       

    
    

class SalaryPaymentForm(forms.ModelForm):
    class Meta:
        model = SalaryPayment
        fields = "__all__"

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        salary_sheet = self.cleaned_data.get('salary_sheet')

        if salary_sheet and amount:
            total_paid = SalaryPayment.objects.filter(salary_sheet=salary_sheet).aggregate(
                total=Sum('amount')  
            )['total'] or 0

            if total_paid + amount > salary_sheet.total_salary:
                raise forms.ValidationError(  
                    f"Total Salary cannot be paid more than {salary_sheet.total_salary}. You have already paid {total_paid}."
                )

        return amount
    

class ExpensePaymentForm(forms.ModelForm):
    class Meta:
        model = ExpensePayment
        fields = "__all__"
        widgets = {
            'expense': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'transaction_account': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("The amount must be greater than 0.")
        return amount


class InvestMentForm(forms.ModelForm):
    class Meta:
        model=InvestMent
        fields="__all__"
        widgets={
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'transaction_account': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model=Withdrawal
        fields="__all__"
        widgets={
            "amount":forms.NumberInput(attrs={'class':'form-control'}),
            'transaction_account':forms.Select(attrs={'class':'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

        }


class FundTransferForm(forms.ModelForm):
    class Meta:
        model=FundTransfer
        fields="__all__"
        widgets={
            "amount":forms.NumberInput(attrs={'class':'form-control'}),
            'transaction_form':forms.Select(attrs={'class':'form-select'}),
            'transaction_to':forms.Select(attrs={'class':'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }



class AdvancePaymentForm(forms.ModelForm):
    class Meta:
        model = AdvancePayment
        fields = ['payment_for', 'supplier', 'customer', 'amount', 'method']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initially make both optional
        self.fields['supplier'].required = False
        self.fields['customer'].required = False

        if 'data' in kwargs:
            payment_for = kwargs['data'].get('payment_for')
            if payment_for == 'Supplier':
                self.fields['supplier'].required = True
                self.fields['customer'].required = False
            elif payment_for == 'Customer':
                self.fields['customer'].required = True
                self.fields['supplier'].required = False