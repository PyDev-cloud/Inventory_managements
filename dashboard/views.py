from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, F
from calendar import monthrange
from decimal import Decimal

from inventory.models import Supplier, Product, Purchase, PurchasePayment, PurchaseItem
from sales.models import Sale, SalePayment, SaleItem, Customer
from accounts.models import (
    BankAccount, BkashAccount, CashAccount,
    SalarySheet, ExpensePayment, InvestMent, FundTransfer
)
from returns.models import Return, ReturnItem
from accounts.models import Employee

# Helper: Get return stats
def get_monthly_return_quantity_and_amount(year, month):
    start_of_month = timezone.datetime(year=year, month=month, day=1, tzinfo=timezone.get_current_timezone())
    last_day = monthrange(year, month)[1]
    end_of_month = timezone.datetime(year=year, month=month, day=last_day, hour=23, minute=59, second=59,
                                     tzinfo=timezone.get_current_timezone())

    return_items = ReturnItem.objects.filter(
        return_record__date__gte=start_of_month,
        return_record__date__lte=end_of_month
    )

    total_quantity = return_items.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    total_amount = return_items.annotate(
        total=F('quantity') * F('unit_price')
    ).aggregate(total_amount=Sum('total'))['total_amount'] or 0

    return total_quantity, total_amount

# FIFO-based COGS calculation
def calculate_fifo_cogs(sale_items):
    cogs_total = Decimal('0')

    for item in sale_items:
        product = item.product
        remaining_qty = item.quantity

        purchase_items = PurchaseItem.objects.filter(
            product=product
        ).order_by('purchase__date')

        for purchase_item in purchase_items:
            # You can enhance this logic with an actual 'remaining_qty' tracking
            available_qty = purchase_item.quantity  # Replace with actual remaining if maintained
            if available_qty <= 0:
                continue

            used_qty = min(available_qty, remaining_qty)
            cogs_total += used_qty * purchase_item.unit_price

            remaining_qty -= used_qty
            if remaining_qty <= 0:
                break

    return cogs_total

# Dashboard view
def dashboard_view(request):
    today = timezone.now()
    year = today.year
    month = today.month

    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = monthrange(year, month)[1]
    end_of_month = today.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    # Basic counts
    total_suppliers = Supplier.objects.count()
    total_products = Product.objects.count()
    stock_totals = Product.objects.aggregate(
        total_office_stock=Sum('office_stock'),
        total_godown_stock=Sum('godown_stock'),
        total_damage_stock=Sum('damage_stock')
    )

    # Purchases
    monthly_purchases = Purchase.objects.filter(date__range=(start_of_month, end_of_month))
    monthly_purchase_total = monthly_purchases.aggregate(total=Sum('total_amount'))['total'] or 0
    monthly_purchase_discount_total = Purchase.objects.filter(date__range=(start_of_month, end_of_month)).aggregate(total=Sum('discount_amount'))['total'] or 0
    total_advance = Supplier.objects.aggregate(total=Sum('advance_payment'))['total'] or 0
    monthly_purchase_payment_total = PurchasePayment.objects.filter(date__range=(start_of_month, end_of_month)).aggregate(total=Sum('amount'))['total'] or 0
    totalpayment=max(monthly_purchase_payment_total + total_advance,0)
    monthly_purchase_due = max(monthly_purchase_total - monthly_purchase_payment_total, 0)
    monthly_purchase_advance = max(totalpayment - monthly_purchase_total, 0)

    # Sales
    monthly_sales = Sale.objects.filter(date__range=(start_of_month, end_of_month))
    monthly_sales_total = sum(sale.total_amount for sale in monthly_sales) or 0
    monthly_discount_total = Sale.objects.filter(date__range=(start_of_month, end_of_month)).aggregate(total=Sum('discount_amount'))['total'] or 0
    total_sales_advance = Customer.objects.aggregate(total=Sum('advance_payment'))['total'] or 0
    monthly_sales_payment_total = SalePayment.objects.filter(date__range=(start_of_month, end_of_month)).aggregate(total=Sum('amount'))['total'] or 0
    totalsales_payment=max(monthly_sales_payment_total + total_sales_advance,0)
    monthly_sales_due = max(monthly_sales_total - monthly_sales_payment_total, 0)
    monthly_sales_advance = max(totalsales_payment - monthly_sales_total, 0)

    total_customer = Customer.objects.count()

    # Returns
    monthly_returns = Return.objects.filter(date__range=(start_of_month, end_of_month))
    purchase_returns = monthly_returns.filter(return_type='purchase')
    purchase_return_count = purchase_returns.count()
    purchase_return_total_amount = sum(r.get_total_amount() for r in purchase_returns) or 0

    sale_returns = monthly_returns.filter(return_type='sale')
    sale_return_count = sale_returns.count()
    sale_return_total_amount = sum(r.get_total_amount() for r in sale_returns) or 0

    # Account balances
    cash_balance = CashAccount.objects.aggregate(total=Sum('balance'))['total'] or 0
    bank_balance = BankAccount.objects.aggregate(total=Sum('balance'))['total'] or 0
    bkash_balance = BkashAccount.objects.aggregate(total=Sum('balance'))['total'] or 0

    # Salaries
    total_employee =Employee.objects.count()

    salary_sheets = SalarySheet.objects.filter(payment_date__range=(start_of_month, end_of_month))
    total_salary = salary_sheets.aggregate(total=Sum('total_salary'))['total'] or 0
    salary_paid = salary_sheets.aggregate(total=Sum('paid_amount'))['total'] or 0
    total_due = max(total_salary - salary_paid, 0)
    salary_unpaid_count = salary_sheets.filter(payment_status='unpaid').count()
    salary_partial_count = salary_sheets.filter(payment_status='partial').count()
    salary_paid_count = salary_sheets.filter(payment_status='paid').count()

    # Expenses and Investments
    expense_paid = ExpensePayment.objects.filter(payment_date__range=(start_of_month, end_of_month)).aggregate(total=Sum('amount'))['total'] or 0
    invested = InvestMent.objects.filter(payment_date__range=(start_of_month, end_of_month)).aggregate(total=Sum('amount'))['total'] or 0
    fund_transferred = FundTransfer.objects.filter(payment_date__range=(start_of_month, end_of_month)).aggregate(total=Sum('amount'))['total'] or 0

    # FIFO-based Profit & Loss Calculation
    sale_items = SaleItem.objects.filter(sale__date__range=(start_of_month, end_of_month))
    sales_revenue = sale_items.aggregate(total=Sum(F('quantity') * F('unit_price')))['total'] or 0
    cogs = calculate_fifo_cogs(sale_items)
    gross_profit = sales_revenue - cogs
    net_profit = gross_profit - (salary_paid + expense_paid + invested)

    context = {
        'total_suppliers': total_suppliers,
        'total_products': total_products,
        'total_office_stock': stock_totals['total_office_stock'] or 0,
        'total_godown_stock': stock_totals['total_godown_stock'] or 0,
        'total_damage_stock': stock_totals['total_damage_stock'] or 0,
        'total_stock': (stock_totals['total_office_stock'] or 0) + (stock_totals['total_godown_stock'] or 0),
        'monthly_purchase_count': monthly_purchases.count(),
        'monthly_purchase_total': monthly_purchase_total,
        'monthly_purchase_discount_total':monthly_purchase_discount_total,
        'totalpayment': totalpayment,
        'monthly_purchase_due': monthly_purchase_due,
        'monthly_purchase_advance': monthly_purchase_advance,
        'monthly_sales_count': monthly_sales.count(),
        'monthly_discount_total':monthly_discount_total,
        'monthly_sales_total': monthly_sales_total,
        'monthly_sales_payment_total': monthly_sales_payment_total,
        'totalsales_payment':totalsales_payment,
        'monthly_sales_due': monthly_sales_due,
        'monthly_sales_advance': monthly_sales_advance,
        'purchase_return_count': purchase_return_count,
        'purchase_return_total_amount': purchase_return_total_amount,
        'sale_return_count': sale_return_count,
        'sale_return_total_amount': sale_return_total_amount,
        'cash_balance': cash_balance,
        'bank_balance': bank_balance,
        'bkash_balance': bkash_balance,
        'total_employee':total_employee,
        'salary_total': total_salary,
        'salary_paid': salary_paid,
        'salary_due': total_due,
        'salary_unpaid_count': salary_unpaid_count,
        'salary_partial_count': salary_partial_count,
        'salary_paid_count': salary_paid_count,
        'expense_paid': expense_paid,
        'invested': invested,
        'fund_transferred': fund_transferred,
        'sales_revenue': sales_revenue,
        'cogs': cogs,
        'gross_profit': gross_profit,
        'net_profit': net_profit,
        'is_profit': net_profit >= 0,
        'profit': net_profit if net_profit >= 0 else 0,
        'loss': abs(net_profit) if net_profit < 0 else 0,
        'total_customer': total_customer,
    }

    return render(request, 'dashboard/dashboard.html', context)
