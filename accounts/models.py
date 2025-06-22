

# Create your models here.
from django.db import models
from inventory.models import Supplier
from sales.models import Customer
from django.utils import timezone


class BankAccount(models.Model):
    name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"
    

class BkashAccount(models.Model):
    name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} - {self.account_number}"

class CashAccount(models.Model):
    name = models.CharField(max_length=255, default='Cash')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100, null=False,blank=False)
    father_name=models.CharField(max_length=100)
    mother_name=models.CharField(max_length=100)
    national_Id=models.CharField(max_length=25)
    date_of_birth=models.DateField(blank=True, null=True)
    email=models.EmailField(max_length=90)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address=models.CharField(max_length=20)
    designation = models.CharField(max_length=255, blank=True, null=True)
    status=models.BooleanField(default=True)
    joining_date=models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    

class salaryStructure(models.Model):
    employee = models.OneToOneField(Employee,on_delete=models.CASCADE)
    basic_salary=models.DecimalField(max_digits=12, decimal_places=2,default=0)
    house_rent=models.DecimalField(max_digits=12, decimal_places=2,default=0)
    conveyance=models.DecimalField(max_digits=12, decimal_places=2,default=0)
    provident_fund=models.DecimalField(max_digits=12, decimal_places=2,default=0)
    medical_allowance=models.DecimalField(max_digits=12, decimal_places=2,default=0)
    special_allowance=models.DecimalField(max_digits=12, decimal_places=2,default=0)
    telephone_bill=models.DecimalField(max_digits=12,decimal_places=2,default=0)

    def __str__(self):
        return self.employee.name

    

class SalarySheet(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.DateField()  
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    house_rent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    conveyance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    provident_fund = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    telephone_bill = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Every Month Extra Field 
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advance_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    salary_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Calculated Total and payment info
    total_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    payment_status = models.CharField(
        max_length=10,
        choices=[('unpaid', 'unpaid'), ('partial', 'partial'), ('paid', 'paid')],
        default='unpaid'
    )
    payment_date = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'month') 

    def __str__(self):
        return f"{self.employee.name} - {self.month.strftime('%B %Y')}"

    def calculate_total_salary(self):
        total = (
            self.basic_salary +
            self.house_rent +
            self.conveyance +
            self.medical_allowance +
            self.special_allowance +
            self.telephone_bill +
            self.bonus
        )
        total -= (self.advance_salary + self.salary_deduction)
        return total

    def update_payment_status(self):
        if self.paid_amount == 0:
            self.payment_status = 'unpaid'
        elif self.paid_amount >= self.total_salary:
            self.payment_status = 'paid'
        else:
            self.payment_status = 'partial'

    def save(self, *args, **kwargs):
        self.total_salary = self.calculate_total_salary()
        self.update_payment_status()
        super().save(*args, **kwargs)




class SalaryPayment(models.Model):
    salary_sheet = models.ForeignKey(SalarySheet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_account = models.CharField(
        max_length=50,
        choices=[('bank', 'Bank'), ('cash', 'Cash'), ('bkash', 'Bkash')],
        default='cash'
    )
    payment_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.salary_sheet.paid_amount += self.amount
        self.salary_sheet.save()

    

class Expense(models.Model):
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return self.description
    


class ExpensePayment(models.Model):
    expense=models.ForeignKey(Expense,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=13,decimal_places=2)
    transaction_account = models.CharField(
        max_length=50,
        choices=[('bank', 'Bank'), ('cash', 'Cash'), ('bkash', 'Bkash')],
        default='cash'
    )
    payment_date = models.DateField(auto_now_add=True)
    note=models.TextField(max_length=200,blank=True)




class InvestMent(models.Model):
    transaction_account = models.CharField(
        max_length=50,
        choices=[('bank', 'Bank'), ('cash', 'Cash'), ('bkash', 'Bkash')],
        default='cash'
    )

    amount=models.DecimalField(max_digits=13,decimal_places=2)
    note=models.TextField(max_length=200,blank=True)
    payment_date = models.DateField(auto_now_add=True)




class Withdrawal(models.Model):

    transaction_account = models.CharField(
        max_length=50,
        choices=[('bank', 'Bank'), ('cash', 'Cash'), ('bkash', 'Bkash')],
        default='cash'
    )

    amount=models.DecimalField(max_digits=13,decimal_places=2)
    note=models.TextField(max_length=200,blank=True)
    payment_date = models.DateField(auto_now_add=True)




class FundTransfer(models.Model):

    transaction_form= models.CharField(
        max_length=50,
        choices=[('bank', 'Bank'), ('cash', 'Cash'), ('bkash', 'Bkash')],
        default='cash'
    )
    transaction_to= models.CharField(
        max_length=50,
        choices=[('bank', 'Bank'), ('cash', 'Cash'), ('bkash', 'Bkash')],
        default='cash'
    )

    amount=models.DecimalField(max_digits=13,decimal_places=2)
    note=models.TextField(max_length=200,blank=True)
    payment_date = models.DateField(auto_now_add=True)




class AdvancePayment(models.Model):
    payment_for= models.CharField(
        max_length=50,
        choices=[('Supplier', 'Supplier'), ('Customer', 'Customer')],
        default='cash'
    )
    supplier=models.ForeignKey(Supplier,on_delete=models.CASCADE,null=True, blank=True)
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE,null=True, blank=True)
    amount=models.DecimalField(max_digits=13,decimal_places=2)
    method = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('bank', 'Bank'), ('bkash', 'Bkash')])
    created_at = models.DateField(auto_now_add=True)


