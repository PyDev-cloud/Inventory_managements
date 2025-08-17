from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView,CreateView
from django.urls import reverse_lazy
from django.views import View
from .models import Sale, Customer,SalePayment
from accounts.models import BankAccount,CashAccount,BkashAccount
from inventory.models import PurchaseItem
from .forms import SaleForm, SaleItemFormSet,CustomerForm,DuePaymentForm
from django.contrib import messages
from .services import update_product_stock
from django.db import transaction
from inventory.utils import reduce_office_stock, update_product_stock
from django.contrib.auth.mixins import LoginRequiredMixin

class CustomerListView(LoginRequiredMixin,ListView):
    model = Customer
    template_name = 'sales/customers/customer_list.html'  # your template path
    context_object_name = 'customers'
    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')
        phone = self.request.GET.get('phone')
        email = self.request.GET.get('email')
        payment_status = self.request.GET.get('payment_status')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if phone:
            queryset = queryset.filter(phone__icontains=phone)
        if email:
            queryset = queryset.filter(email__icontains=email)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = self.request.GET.get('name', '')
        context['phone'] = self.request.GET.get('phone', '')
        context['email'] = self.request.GET.get('email', '')
        return context


class CustomerCreateView(LoginRequiredMixin,CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customers/customer_form.html'  # your template path
    success_url = reverse_lazy('sales:customer_list')  # redirect after success, adjust name accordingly


class SaleListView(LoginRequiredMixin,ListView):
    model = Sale
    template_name = 'sales/sales_templete/sales_list.html'
    context_object_name = 'sales'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('customer')
        invoice = self.request.GET.get('invoice')
        customer_id = self.request.GET.get('customer')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        payment_method = self.request.GET.get('payment_method')
        payment_status = self.request.GET.get('payment_status')

        if invoice:
            queryset = queryset.filter(invoice_no__icontains=invoice)
        if customer_id:
            queryset = queryset.filter(customer__id=customer_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        if payment_status == 'paid':
            queryset = queryset.filter(due_amount=0)
        elif payment_status == 'unpaid':
            queryset = queryset.filter(due_amount__gt=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        context['invoice'] = self.request.GET.get('invoice', '')
        context['customer_id'] = self.request.GET.get('customer', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['payment_method'] = self.request.GET.get('payment_method', '')
        context['payment_status'] = self.request.GET.get('payment_status', '')
        return context

class SaleDetailView(LoginRequiredMixin,DetailView):
    model = Sale
    template_name = 'sales/sales_templete/sales_detail.html'
    context_object_name = 'sale'

class SaleCreateView(LoginRequiredMixin,View):
    def get(self, request):
        form = SaleForm()
        formset = SaleItemFormSet()
        customers = Customer.objects.all()
        return render(request, 'sales/sales_templete/sales_form.html', {
            'form': form,
            'formset': formset,
            'customers':customers
        })

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)
        customers = Customer.objects.all()
        if form.is_valid() and formset.is_valid():
            sale = form.save(commit=False)
            use_advance_payment = form.cleaned_data.get("use_advance_payment", False)
            print("Form valid?", form.is_valid())
            print("Form errors:", form.errors)
            print("Formset valid?", formset.is_valid())
            print("Formset errors:", formset.errors)
            try:
                with transaction.atomic():
                    sale.save()
                    items = formset.save(commit=False)

                    for item in items:
                        item.sale = sale
                        # Stock Deduction
                        reduce_office_stock(item.product, item.quantity)

                        # FIFO selling process
                        unit_cost, total_cogs = self.sell_product_fifo(item.product, item.quantity)
                        item.cost_price = unit_cost
                        item.save()

                    customer = sale.customer
                    total_paid = sale.paid_amount

                    if use_advance_payment:
                        if customer.advance_payment >= total_paid:
                            # Deduct the full amount from the advance.
                            customer.advance_payment -= total_paid
                            customer.save()
                        else:
                            # From partial advance, remaining payment is separate
                            advance_used = customer.advance_payment
                            remaining = total_paid - advance_used
                            customer.advance_payment = 0
                            customer.save()

                            if remaining > 0:
                                SalePayment.objects.create(
                                    sale=sale,
                                    amount=remaining,
                                    method=sale.payment_method,
                                    note="Partially manual payment"
                                )
                                self.update_account_balance(sale.payment_method, remaining)
                    else:
                        if total_paid > 0:
                            SalePayment.objects.create(
                                sale=sale,
                                amount=total_paid,
                                method=sale.payment_method,
                                note="Manual payment"
                            )
                            self.update_account_balance(sale.payment_method, total_paid)

                    # Update customer financials
                    customer.calculate_financials()

            except ValueError as e:
                form.add_error(None, str(e))
                return render(request, 'sales/sales_templete/sales_form.html', {
                    'form': form,
                    'formset': formset
                })

            messages.success(request, "Sale created successfully!")
            return redirect('sales:sale_list')

        return render(request, 'sales/sales_templete/sales_form.html', {
            'form': form,
            'formset': formset,
            'customers':customers
        })

    def sell_product_fifo(self, product, quantity_to_sell):
        purchase_items = PurchaseItem.objects.filter(
            product=product,
            remaining_quantity__gt=0
        ).order_by('purchase__date')

        qty_left = quantity_to_sell
        total_cogs = 0

        for item in purchase_items:
            if qty_left <= 0:
                break

            available_qty = item.remaining_quantity
            qty_used = min(available_qty, qty_left)

            total_cogs += qty_used * item.unit_price
            item.remaining_quantity -= qty_used
            item.save()

            qty_left -= qty_used

        if qty_left > 0:
            raise ValueError(f"Not enough stock for {product.name}.")

        unit_cost = total_cogs / quantity_to_sell
        return unit_cost, total_cogs

    def update_account_balance(self, method, amount):
        if method == 'bkash':
            account = BkashAccount.objects.first()
        elif method == 'cash':
            account = CashAccount.objects.first()
        elif method == 'bank':
            account = BankAccount.objects.first()
        else:
            return

        account.balance += amount
        account.save()


class SaleDuePaymentView(LoginRequiredMixin,View):
    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)
        form = DuePaymentForm(initial={
            'amount': sale.due_amount,
            'method': sale.payment_method
        })
        return render(request, 'sales/sales_templete/pay_due_form.html', {'sale': sale, 'form': form})

    def post(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)
        form = DuePaymentForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            method = form.cleaned_data['method']
            note = form.cleaned_data['note']

            if amount > sale.due_amount:
                form.add_error('amount', 'The repayment amount cannot exceed the due amount.')
                return render(request, 'sales/sales_templete/pay_due_form.html', {'sale': sale, 'form': form})

            # Account verification
            if method == 'bkash':
                account = BkashAccount.objects.first()
            elif method == 'cash':
                account = CashAccount.objects.first()
            elif method == 'bank':
                account = BankAccount.objects.first()
            else:
                account = None

            if not account:
                form.add_error('method', f"{method.title()} Account not found.")
                return render(request, 'sales/sales_templete/pay_due_form.html', {'sale': sale, 'form': form})

            with transaction.atomic():
                # Payment Entry
                SalePayment.objects.create(
                    sale=sale,
                    amount=amount,
                    method=method,
                    note=note or "Due Payment"
                )

                # Increase Account balance
                account.balance += amount
                account.save()

                # Sell update
                sale.paid_amount += amount
                sale.due_amount -=amount
                sale.save()

                # Customar file update
                sale.customer.calculate_financials()

                messages.success(request, "Due payment completed successfully!")
                return redirect('sales:sale_list')

        return render(request, 'sales/sales_templete/pay_due_form.html', {'sale': sale, 'form': form})