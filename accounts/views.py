from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import BankAccount,BkashAccount, CashAccount, Employee, SalarySheet, Expense,SalaryPayment,ExpensePayment,InvestMent,Withdrawal,FundTransfer,AdvancePayment,salaryStructure
from .forms import BankAccountForm,BkashAccountForm, CashAccountForm, EmployeeForm, SalarySheetForm,ExpenseForm,SalaryPaymentForm,ExpensePaymentForm,InvestMentForm,WithdrawalForm,FundTransferForm,AdvancePaymentForm,SalaryStructureForm
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import redirect,get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from inventory.models import Supplier
from sales.models import Customer
from django.utils.timezone import now
from django.utils import timezone
from datetime import datetime
import calendar


# Bank Accounts CRUD

class BankAccountListView(ListView):
    model = BankAccount
    template_name = 'accounts/bank/bankaccount_list.html'
    context_object_name = 'bank_accounts'

class BankAccountCreateView(CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'accounts/bank/bankaccount_form.html'
    success_url = reverse_lazy('accounts:bankaccount_list')

class BankAccountUpdateView(UpdateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'accounts/bank/bankaccount_form.html'
    success_url = reverse_lazy('accounts:bankaccount_list')

class BankAccountDeleteView(DeleteView):
    model = BankAccount
    template_name = 'accounts/bank/bankaccount_confirm_delete.html'
    success_url = reverse_lazy('accounts:bankaccount_list')
    
# Bkash CRUD


class BkashAccountListView(ListView):
    model = BkashAccount
    template_name = 'accounts/bkash/bkashaccount_list.html'
    context_object_name = 'bkash_accounts'

class BkashAccountCreateView(CreateView):
    model = BkashAccount
    form_class = BkashAccountForm
    template_name = 'accounts/bkash/bkashaccount_form.html'
    success_url = reverse_lazy('accounts:bkashaccount_list')

class BkashAccountUpdateView(UpdateView):
    model = BkashAccount
    form_class = BkashAccountForm
    template_name = 'accounts/bkash/bkashaccount_form.html'
    success_url = reverse_lazy('accounts:bkashaccount_list')

class BkashAccountDeleteView(DeleteView):
    model = BkashAccount
    template_name = 'accounts/bkash/bkashaccount_confirm_delete.html'
    success_url = reverse_lazy('accounts:bkashaccount_list') 

# Cash Account CRUD
class CashAccountListView(ListView):
    model = CashAccount
    template_name = 'accounts/cash/cashaccount_list.html'
    context_object_name = 'cash_accounts'

class CashAccountCreateView(CreateView):
    model = CashAccount
    form_class = CashAccountForm
    template_name = 'accounts/cash/cashaccount_form.html'
    success_url = reverse_lazy('accounts:cashaccount-list')

class CashAccountUpdateView(UpdateView):
    model = CashAccount
    form_class = CashAccountForm
    template_name = 'accounts/cash/cashaccount_form.html'
    success_url = reverse_lazy('accounts:cashaccount-list')

class CashAccountDeleteView(DeleteView):
    model = CashAccount
    template_name = 'accounts/cash/cashaccount_confirm_delete.html'
    success_url = reverse_lazy('accounts:cashaccount-list')

# Employee CRUD
class EmployeeListView(ListView):
    model = Employee
    template_name = 'accounts/employe/employee_list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        position = self.request.GET.get('position')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if position:
            queryset = queryset.filter(position__icontains=position)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = self.request.GET.get('name', '')
        context['email'] = self.request.GET.get('email', '')
        context['position'] = self.request.GET.get('position', '')
        return context

class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'accounts/employe/employee_form.html'
    success_url = reverse_lazy('accounts:employee_list')
    


class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'accounts/employe/employee_form.html'
    success_url = reverse_lazy('accounts:employee_list')

class EmployeeDeleteView(DeleteView):
    model = Employee
    template_name = 'accounts/employe/employee_confirm_delete.html'
    success_url = reverse_lazy('accounts:employee_list')





class SalaryStructureListView(ListView):
    model = salaryStructure
    template_name = 'accounts/salarystructure/salarystructure_list.html'
    context_object_name = 'structures'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee')
        name = self.request.GET.get('name')
        basic_salary = self.request.GET.get('basic_salary')
        house_rent = self.request.GET.get('house_rent')
        conveyance = self.request.GET.get('conveyance')
        provident_fund = self.request.GET.get('provident_fund')
        medical_allowance = self.request.GET.get('medical_allowance')
        special_allowance = self.request.GET.get('special_allowance')
        telephone_bill = self.request.GET.get('telephone_bill')

        if name:
            queryset = queryset.filter(employee__name__icontains=name)
        if basic_salary:
            queryset = queryset.filter(basic_salary=basic_salary)
        if house_rent:
            queryset = queryset.filter(house_rent=house_rent)
        if conveyance:
            queryset = queryset.filter(conveyance=conveyance)
        if provident_fund:
            queryset = queryset.filter(provident_fund=provident_fund)
        if medical_allowance:
            queryset = queryset.filter(medical_allowance=medical_allowance)
        if special_allowance:
            queryset = queryset.filter(special_allowance=special_allowance)
        if telephone_bill:
            queryset = queryset.filter(telephone_bill=telephone_bill)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = ['name', 'basic_salary', 'house_rent', 'conveyance', 'provident_fund',
                  'medical_allowance', 'special_allowance', 'telephone_bill']
        for field in fields:
            context[field] = self.request.GET.get(field, '')
        return context

class SalaryStructureCreateView(CreateView):
    model = salaryStructure
    form_class = SalaryStructureForm
    template_name = 'accounts/salarystructure/salarystructure_form.html'
    success_url = reverse_lazy('accounts:salarystructure_list')

    def form_valid(self, form):
        employee = form.cleaned_data['employee']
        if salaryStructure.objects.filter(employee=employee).exists():
            form.add_error('employee', 'This employee has already made pay structure')
            return self.form_invalid(form)
        return super().form_valid(form)

class SalaryStructureUpdateView(UpdateView):
    model = salaryStructure
    form_class = SalaryStructureForm
    template_name = 'accounts/salarystructure/salarystructure_form.html'
    success_url = reverse_lazy('accounts:salarystructure_list')

class SalaryStructureDeleteView(DeleteView):
    model = salaryStructure
    template_name = 'accounts/salarystructure/salarystructure_confirm_delete.html'
    success_url = reverse_lazy('accounts:salarystructure_list')








# Salary Sheet 
class SalarySheetListView(ListView):
    model = SalarySheet
    template_name = 'accounts/salary/salarysheet_list.html'
    context_object_name = 'sheets'

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request.GET

        # Filter fields from GET params
        name = request.get('name')
        month = request.get('month')  # Format: YYYY-MM
        status = request.get('status')

        # Salary filters
        basic_min = request.get('basic_min')
        basic_max = request.get('basic_max')

        medical_min = request.get('medical_min')
        medical_max = request.get('medical_max')

        house_min = request.get('house_min')
        house_max = request.get('house_max')

        # Filter by employee name
        if name:
            queryset = queryset.filter(employee__name__icontains=name)

        # Filter by month (expecting YYYY-MM)
        if month:
            try:
                year, mon = map(int, month.split('-'))
                queryset = queryset.filter(month__year=year, month__month=mon)
            except:
                pass

        # Filter by status
        if status:
            queryset = queryset.filter(payment_status=status)

        # Filter salary ranges
        if basic_min:
            queryset = queryset.filter(basic_salary__gte=basic_min)
        if basic_max:
            queryset = queryset.filter(basic_salary__lte=basic_max)

        if medical_min:
            queryset = queryset.filter(medical_allowance__gte=medical_min)
        if medical_max:
            queryset = queryset.filter(medical_allowance__lte=medical_max)

        if house_min:
            queryset = queryset.filter(house_rent__gte=house_min)
        if house_max:
            queryset = queryset.filter(house_rent__lte=house_max)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = self.request.GET.get('name', '')
        context['month'] = self.request.GET.get('month', '')
        context['status'] = self.request.GET.get('status', '')

        context['basic_min'] = self.request.GET.get('basic_min', '')
        context['basic_max'] = self.request.GET.get('basic_max', '')

        context['medical_min'] = self.request.GET.get('medical_min', '')
        context['medical_max'] = self.request.GET.get('medical_max', '')

        context['house_min'] = self.request.GET.get('house_min', '')
        context['house_max'] = self.request.GET.get('house_max', '')

        return context






def get_salary_structure(request, employee_id):
    try:
        structure = salaryStructure.objects.get(employee_id=employee_id)
        data = {
            "basic_salary": float(structure.basic_salary),
            "house_rent": float(structure.house_rent),
            "medical_allowance": float(structure.medical_allowance),
            "conveyance": float(structure.conveyance),
            "special_allowance": float(structure.special_allowance),
            "telephone_bill": float(structure.telephone_bill),
            "provident_fund": float(structure.provident_fund),
        }
        return JsonResponse(data)
    except salaryStructure.DoesNotExist:
        return JsonResponse({"error": "Salary structure not found"}, status=404)

class SalarySheetCreateView(CreateView):
    model = SalarySheet
    form_class = SalarySheetForm
    template_name = 'accounts/salary/salarysheet_form.html'
    success_url = reverse_lazy('accounts:salarysheet_list')

    def form_valid(self, form):
        employee = form.cleaned_data['employee']
        try:
            structure = salaryStructure.objects.get(employee=employee)
        except salaryStructure.DoesNotExist:
            form.add_error('employee', 'This employee has no salary structure.')
            return self.form_invalid(form)

        salary_sheet = form.save(commit=False)
        # Set again from the salary structure for security.
        salary_sheet.basic_salary = structure.basic_salary
        salary_sheet.house_rent = structure.house_rent
        salary_sheet.medical_allowance = structure.medical_allowance
        salary_sheet.conveyance = structure.conveyance
        salary_sheet.special_allowance = structure.special_allowance
        salary_sheet.telephone_bill = structure.telephone_bill
        salary_sheet.provident_fund = structure.provident_fund
        salary_sheet.save()

        messages.success(self.request, 'Salary sheet created successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        print("Form errors:", form.errors)  # Check server logs
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fixed_fields'] = [
            "basic_salary",
            "house_rent",
            "conveyance",
            "provident_fund",
            "medical_allowance",
            "special_allowance",
            "telephone_bill"
        ]
        return context






class SalarySheetUpdateView(UpdateView):
    model = SalarySheet
    form_class = SalarySheetForm
    template_name = 'accounts/salary/salarysheet_form.html'
    success_url = reverse_lazy('accounts:salarysheet_list')

class SalarySheetDeleteView(DeleteView):
    model = SalarySheet
    template_name = 'accounts/salary/salarysheet_confirm_delete.html'
    success_url = reverse_lazy('accounts:salarysheet_list')


# Expense CRUD
class ExpenseListView(ListView):
    model = Expense
    template_name = 'accounts/expance/expense_list.html'
    context_object_name = 'expenses'

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'accounts/expance/expense_list_create.html'
    success_url = reverse_lazy('accounts:expense_list')

class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'accounts/expance/expense_list_create.html'
    success_url = reverse_lazy('accounts:expense_list')
    def form_valid(self, form):
        messages.success(self.request, "Expense updated successfully ✅")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update expense ❌")
        return super().form_invalid(form)

class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'accounts/expance/expense_confirm_delete.html'
    success_url = reverse_lazy('accounts:expense_list')




class SalaryPaymentListView(ListView):
    model = SalaryPayment
    template_name = 'accounts/Employe/salary_payment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('salary_sheet__employee')
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')

        now = timezone.now()
        month = int(month) if month else now.month
        year = int(year) if year else now.year

        return queryset.filter(payment_date__month=month, payment_date__year=year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        selected_month = int(self.request.GET.get('month', now.month))
        selected_year = int(self.request.GET.get('year', now.year))

        # Month List
        months = [(i, calendar.month_name[i]) for i in range(1, 13)]
        years = list(range(now.year - 2, now.year + 2))  

        context.update({
            'month_name': calendar.month_name[selected_month],
            'year': selected_year,
            'current_month': selected_month,
            'current_year': selected_year,
            'months': months,
            'year_range': years,
        })
        return context





class SalaryPaymentCreateView(CreateView):
    model = SalaryPayment
    form_class = SalaryPaymentForm
    template_name = 'accounts/Employe/salary_payment_form.html'
    success_url = reverse_lazy('accounts:salarysheet_list')

    def form_valid(self, form):
        with transaction.atomic():
            payment = form.save(commit=False)
            amount = payment.amount
            account_type = payment.transaction_account

            # Account Selection and Balance
            account = None
            error_message = ""

            if account_type == 'cash':
                account = CashAccount.objects.first()
                error_message = "Insufficient balance in Cash Account."
            elif account_type == 'bkash':
                account = BkashAccount.objects.first()
                error_message = "Insufficient balance in Bkash Account."
            elif account_type == 'bank':
                account = BankAccount.objects.first()
                error_message = "Insufficient balance in Bank Account."

           
            if not account or account.balance < amount:
                form.add_error(None, error_message)
                return self.form_invalid(form)

            # Decrease in balance
            account.balance -= amount
            account.save()

          # SalarySheet's paid_amount will be auto-updated from save() of SalaryPayment model
            payment.save()

            messages.success(self.request, " The payment has been completed successfully.")
            return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "❌ There are some errors in the form. Please correct them.")
        return super().form_invalid(form)


def get_salary_structure_from_sheet(request, sheet_id):
    try:
        sheet = SalarySheet.objects.get(id=sheet_id)
    except SalarySheet.DoesNotExist:
        raise Http404("Salary sheet not found.")

    data = {
        'paid_amount': float(sheet.paid_amount or 0),
        'total_salary': float(sheet.total_salary or 0),
    }
    return JsonResponse(data)

    




class ExpensePaymentListView(ListView):
    model = ExpensePayment
    template_name = 'accounts/expance/expense_payment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        queryset = super().get_queryset()
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')

        now = datetime.now()
        if not month:
            month = now.month
        if not year:
            year = now.year

        return queryset.filter(payment_date__month=month, payment_date__year=year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        month = int(self.request.GET.get('month', now.month))
        year = int(self.request.GET.get('year', now.year))

        # Custom context for filter dropdowns
        context['months'] = [(i, calendar.month_name[i]) for i in range(1, 13)]
        context['year_range'] = range(now.year - 5, now.year + 2)
        context['current_month'] = month
        context['current_year'] = year
        context['month_name'] = calendar.month_name[month]
        context['year'] = year
        return context



class ExpencePaymentCreateView(CreateView):
    model = ExpensePayment
    form_class = ExpensePaymentForm
    template_name = 'accounts/expance/expense_form.html'
    success_url = reverse_lazy('accounts:salarysheet_list')

    def form_valid(self, form):
        with transaction.atomic():
            payment = form.save(commit=False)
            amount = payment.amount
            account_type = payment.transaction_account

            
            if account_type == 'cash':
                account = CashAccount.objects.first()
                if not account or account.balance < amount:
                    form.add_error(None, "Insufficient balance in Cash Account.")
                    return self.form_invalid(form)
                account.balance -= amount
                account.save()

            elif account_type == 'bkash':
                account = BkashAccount.objects.first()
                if not account or account.balance < amount:
                    form.add_error(None, "Insufficient balance in Bkash Account")
                    return self.form_invalid(form)
                account.balance -= amount
                account.save()

            elif account_type == 'bank':
                account = BankAccount.objects.first()
                if not account or account.balance < amount:
                    form.add_error(None, "Insufficient balance in Bank Account.")
                    return self.form_invalid(form)
                account.balance -= amount
                account.save()

            # Payment and SalarySheet Updates
            payment.save()  # This will make salary_sheet.paid_amount + amount
            messages.success(self.request, "The payment has been completed successfully.")
            return redirect(self.success_url)
        


class InvestMentListView(ListView):
    model = InvestMent
    template_name = 'accounts/investment/investment_list.html'
    context_object_name = 'investments'

    def get_queryset(self):
        queryset = super().get_queryset()
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')

        now = datetime.now()
        if not month:
            month = now.month
        if not year:
            year = now.year

        return queryset.filter(payment_date__month=month, payment_date__year=year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        month = int(self.request.GET.get('month', now.month))
        year = int(self.request.GET.get('year', now.year))

        context['months'] = [(i, calendar.month_name[i]) for i in range(1, 13)]
        context['year_range'] = range(now.year - 5, now.year + 2)
        context['current_month'] = month
        context['current_year'] = year
        context['month_name'] = calendar.month_name[month]
        context['year'] = year
        return context


class InvestMentCreateView(CreateView):
    model = InvestMent
    form_class = InvestMentForm
    template_name = 'accounts/investment/investment_form.html'
    success_url = reverse_lazy('accounts:salarysheet_list')

    def form_valid(self, form):
        with transaction.atomic():
            payment = form.save(commit=False)
            amount = payment.amount
            account_type = payment.transaction_account

            # deduction from account balance
            if account_type == 'cash':
                account = CashAccount.objects.first()
                if not account:
                    form.add_error(None, "Cash Account is Not Valid ")
                    return self.form_invalid(form)
                account.balance += amount
                account.save()

            elif account_type == 'bkash':
                account = BkashAccount.objects.first()
                if not account :
                    form.add_error(None, "Bkash Account is not valid")
                    return self.form_invalid(form)
                account.balance += amount
                account.save()

            elif account_type == 'bank':
                account = BankAccount.objects.first()
                if not account:
                    form.add_error(None, "Bank Account is not valid")
                    return self.form_invalid(form)
                account.balance += amount
                account.save()

            # Payment and SalarySheet Updates
            payment.save()  # This will make salary_sheet.paid_amount + amount
            messages.success(self.request, "The payment has been completed successfully.")
            return redirect(self.success_url)
        

class WithdrawalListView(ListView):
    model = Withdrawal
    template_name = 'accounts/withdrawal/withdrawal_list.html'
    context_object_name = 'withdrawals'

    def get_queryset(self):
        queryset = super().get_queryset()
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')

        now = datetime.now()
        if not month:
            month = now.month
        if not year:
            year = now.year

        return queryset.filter(payment_date__month=month, payment_date__year=year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        month = int(self.request.GET.get('month', now.month))
        year = int(self.request.GET.get('year', now.year))

        context['months'] = [(i, calendar.month_name[i]) for i in range(1, 13)]
        context['year_range'] = range(now.year - 5, now.year + 2)
        context['current_month'] = month
        context['current_year'] = year
        context['month_name'] = calendar.month_name[month]
        context['year'] = year
        return context

class WithdrawalCreateView(CreateView):
    model = Withdrawal
    form_class = WithdrawalForm
    template_name = 'accounts/withdrawal/withdrawal_form.html'
    success_url = reverse_lazy('accounts:salarysheet_list')

    def form_valid(self, form):
        with transaction.atomic():
            payment = form.save(commit=False)
            amount = payment.amount
            account_type = payment.transaction_account

            # Reduce account balance
            if account_type == 'cash':
                account = CashAccount.objects.first()
                if not account or account.balance < amount:
                    form.add_error(None, "Insufficient balance in Cash Account.")
                    return self.form_invalid(form)
                account.balance -= amount
                account.save()

            elif account_type == 'bkash':
                account = BkashAccount.objects.first()
                if not account or account.balance < amount:
                    form.add_error(None, "Insufficient balance in Bkash Account.")
                    return self.form_invalid(form)
                account.balance -= amount
                account.save()

            elif account_type == 'bank':
                account = BankAccount.objects.first()
                if not account or account.balance < amount:
                    form.add_error(None, "Insufficient balance in Bank Account.")
                    return self.form_invalid(form)
                account.balance -= amount
                account.save()

            # Payment and SalarySheet Updates
            payment.save()  # This will make salary_sheet.paid_amount + amount
            messages.success(self.request, "The payment has been completed successfully.")
            return redirect(self.success_url)


class FundTransferListView(ListView):
    model = FundTransfer
    template_name = 'accounts/fundTransfer/fundtransfer_list.html'
    context_object_name = 'transfers'

    def get_queryset(self):
        queryset = super().get_queryset()
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')

        now = datetime.now()
        if not month:
            month = now.month
        if not year:
            year = now.year

        return queryset.filter(payment_date__month=month, payment_date__year=year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        month = int(self.request.GET.get('month', now.month))
        year = int(self.request.GET.get('year', now.year))

        context['months'] = [(i, calendar.month_name[i]) for i in range(1, 13)]
        context['year_range'] = range(now.year - 5, now.year + 2)
        context['current_month'] = month
        context['current_year'] = year
        context['month_name'] = calendar.month_name[month]
        context['year'] = year
        return context

class FundTransferCreateView(CreateView):
    model = FundTransfer
    form_class = FundTransferForm
    template_name = 'accounts/fundTransfer/fundTransfer_form.html'
    success_url = reverse_lazy('accounts:salarysheet_list')

    def form_valid(self, form):
        with transaction.atomic():
            transfer = form.save(commit=False)
            amount = transfer.amount
            from_acc = transfer.transaction_form
            to_acc = transfer.transaction_to

            if from_acc == to_acc:
                form.add_error(None, "Funds cannot be transferred to the same account.")
                return self.form_invalid(form)

            # ====== FROM ACCOUNT
            if from_acc == 'cash':
                from_account = CashAccount.objects.first()
            elif from_acc == 'bkash':
                from_account = BkashAccount.objects.first()
            elif from_acc == 'bank':
                from_account = BankAccount.objects.first()

            if not from_account:
                form.add_error(None, f"{from_acc.capitalize()} Account not found.")
                return self.form_invalid(form)

            if from_account.balance < amount:
                form.add_error(None, f"{from_acc.capitalize()} There is not enough balance in the account.")
                return self.form_invalid(form)

            # ====== TO ACCOUNT  ======
            to_account = None
            if to_acc == 'cash':
                to_account = CashAccount.objects.first()
            elif to_acc == 'bkash':
                to_account = BkashAccount.objects.first()
            elif to_acc == 'bank':
                to_account = BankAccount.objects.first()

            if not to_account:
                form.add_error(None, f"{to_acc.capitalize()} Account not found.")
                return self.form_invalid(form)

            # ====== Amount Transfer======
            from_account.balance -= amount
            from_account.save()

            to_account.balance += amount
            to_account.save()

            transfer.save()
            messages.success(self.request, "Fund transfer completed successfully.")
            return redirect(self.success_url)



class AdvancePaymentListView(ListView):
    model = AdvancePayment
    template_name = 'accounts/advancePayment/advancepayment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        queryset = super().get_queryset()
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        supplier_id = self.request.GET.get('supplier')
        customer_id = self.request.GET.get('customer')
        method = self.request.GET.get('method')

        now = datetime.now()
        month = int(month) if month else now.month
        year = int(year) if year else now.year

        queryset = queryset.filter(created_at__month=month, created_at__year=year)

        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if method:
            queryset = queryset.filter(method=method)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()

        # Filter values for repopulating the form
        month = int(self.request.GET.get('month', now.month))
        year = int(self.request.GET.get('year', now.year))
        supplier_id = self.request.GET.get('supplier', '')
        customer_id = self.request.GET.get('customer', '')
        method = self.request.GET.get('method', '')

        context.update({
            'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
            'year_range': range(now.year - 5, now.year + 2),
            'current_month': month,
            'current_year': year,
            'month_name': calendar.month_name[month],
            'year': year,
            'suppliers': Supplier.objects.all(),
            'customers': Customer.objects.all(),
            'methods': [('cash', 'Cash'), ('bank', 'Bank'), ('bkash', 'Bkash')],
            'selected_supplier': supplier_id,
            'selected_customer': customer_id,
            'selected_method': method,
        })

        return context



class AdvancePaymentCreateView(CreateView):
    model = AdvancePayment
    form_class = AdvancePaymentForm
    template_name = 'accounts/advancePayment/advance_payment_form.html'
    success_url = reverse_lazy('accounts:salarysheet_list')  


    def form_valid(self, form):
        with transaction.atomic():
            payment = form.save(commit=False)
            amount = payment.amount
            method = payment.method
            payment_for = payment.payment_for

            # Account Select
            if method == 'cash':
                account = CashAccount.objects.first()
            elif method == 'bkash':
                account = BkashAccount.objects.first()
            elif method == 'bank':
                account = BankAccount.objects.first()
            else:
                form.add_error(None, "Invalid Payment Method")
                return self.form_invalid(form)

            if not account:
                form.add_error(None, "The selected payment account could not be found.")
                return self.form_invalid(form)

            #  Supplier Logic
            if payment_for == 'Supplier':
                supplier = payment.supplier
                if not supplier:
                    form.add_error('supplier', "It is necessary to select a supplier.")
                    return self.form_invalid(form)

                if supplier.due_amount > 0:
                    
                    form.add_error('amount', f"{supplier.name} has a due of {supplier.due_amount}. Please pay this due first, advance payments are not possible.")
                    return self.form_invalid(form)
                else:
                    # Full advance (because there is no due)
                    supplier.advance_payment += amount

                if account.balance < amount:
                    form.add_error(None, f"{method.capitalize()} There is not enough balance in the account.")
                    return self.form_invalid(form)

                account.balance -= amount
                account.save()

                supplier.total_payment += amount
                supplier.save()

            # ✅ Customer Logic
            elif payment_for == 'Customer':
                customer = payment.customer
                if not customer:
                    form.add_error('customer', "Buyer selection is required.")
                    return self.form_invalid(form)

                if customer.due_amount > 0:
                
                    form.add_error('amount', f"{customer.name} has a due of {customer.due_amount}. Please pay this due first, advance payment is not possible.")
                    return self.form_invalid(form)
                else:
                    # previous advance
                    customer.advance_payment += amount

                account.balance += amount
                account.save()

                customer.total_payment += amount
                customer.save()

            else:
                form.add_error('payment_for', "Invalid Payment_for Value")
                return self.form_invalid(form)

            payment.save()
            messages.success(self.request, "Payment completed successfully.")
            return super().form_valid(form)
