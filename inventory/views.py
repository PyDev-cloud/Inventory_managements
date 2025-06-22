# Views for inventory# inventory/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Supplier, Product, Purchase, PurchaseItem, PurchasePayment
from accounts.models import BankAccount,CashAccount,BkashAccount
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from .forms import PurchaseForm, PurchaseItemFormSet,SupplierForm,ProductForm,DuePaymentForm,StockTransferForm
from django.db import transaction
from .signals import update_product_stock
from django.contrib import messages
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum,Q

class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier/supplier_list.html'
    context_object_name = 'suppliers'
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(phone__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context



class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier-list')  # Change to your actual list URL name





class ProductListView(ListView):
    model = Product
    template_name = 'inventory/product/product_list.html'
    context_object_name = 'products'
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        unit = self.request.GET.get('unit')
        min_stock = self.request.GET.get('min_stock')
        max_stock = self.request.GET.get('max_stock')

        if query:
            queryset = queryset.filter(Q(name__icontains=query))
        if unit:
            queryset = queryset.filter(unit__iexact=unit)
        if min_stock:
            queryset = queryset.filter(current_stock__gte=min_stock)
        if max_stock:
            queryset = queryset.filter(current_stock__lte=max_stock)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['unit'] = self.request.GET.get('unit', '')
        context['min_stock'] = self.request.GET.get('min_stock', '')
        context['max_stock'] = self.request.GET.get('max_stock', '')
        return context



class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product/product_form.html'
    success_url = reverse_lazy('inventory:product-list')  # Change if you have a product list URL



class PurchaseListView(ListView):
    model = Purchase
    template_name = 'inventory/purchase/purchase_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('supplier')
        invoice = self.request.GET.get('invoice')
        supplier_id = self.request.GET.get('supplier')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        payment_method = self.request.GET.get('payment_method')
        payment_status = self.request.GET.get('payment_status')  

        if invoice:
            queryset = queryset.filter(invoice_no__icontains=invoice)
        if supplier_id:
            queryset = queryset.filter(supplier__id=supplier_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        # ✅ Paid/Unpaid Filter
        if payment_status == 'paid':
            queryset = queryset.filter(due_amount=0)
        elif payment_status == 'unpaid':
            queryset = queryset.filter(due_amount__gt=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = Supplier.objects.all()
        context['invoice'] = self.request.GET.get('invoice', '')
        context['supplier_id'] = self.request.GET.get('supplier', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['payment_method'] = self.request.GET.get('payment_method', '')
        context['payment_status'] = self.request.GET.get('payment_status', '')  
        return context

class PurchaseCreateView(View):
    def get(self, request):
        form = PurchaseForm()
        formset = PurchaseItemFormSet()
        suppliers = Supplier.objects.all()
        return render(request, 'inventory/purchase/purchase_form.html', {'form': form, 'formset': formset,'suppliers': suppliers })

    def post(self, request):
        form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST)
        suppliers = Supplier.objects.all()
        if form.is_valid() and formset.is_valid():
            purchase = form.save(commit=False)

            supplier = form.cleaned_data['supplier']
            input_paid = form.cleaned_data['paid_amount']
            advance_available = supplier.advance_payment
            print(advance_available)
            paid_from_advance = 0
            paid_from_account = 0

            # Determine how much can be paid from advance
            if advance_available >= input_paid:
                paid_from_advance = input_paid
            else:
                paid_from_advance = advance_available
                paid_from_account = input_paid - advance_available

            total_paid = paid_from_advance + paid_from_account
            purchase.paid_amount = total_paid
            purchase.due_amount = purchase.total_amount - total_paid

            # Check account balances only if real account payment is needed
            insufficient_balance = False
            error_message = ""

            if paid_from_account > 0:
                if purchase.payment_method == 'bkash':
                    bkash_account = BkashAccount.objects.first()
                    if not bkash_account or bkash_account.balance < paid_from_account:
                        insufficient_balance = True
                        error_message = "There is not enough balance in the Bkash account.।"
                elif purchase.payment_method == 'cash':
                    cash_account = CashAccount.objects.first()
                    if not cash_account or cash_account.balance < paid_from_account:
                        insufficient_balance = True
                        error_message = "There is not enough balance in the Cash account."
                elif purchase.payment_method == 'bank':
                    bank_account = BankAccount.objects.first()
                    if not bank_account or bank_account.balance < paid_from_account:
                        insufficient_balance = True
                        error_message = "There is not enough balance in the Bank account."

            if insufficient_balance:
                form.add_error(None, error_message)
                return render(request, 'inventory/purchase/purchase_form.html', {'form': form, 'formset': formset})

            # Save everything inside atomic block
            with transaction.atomic():
                purchase.save()
                formset.instance = purchase
                items = formset.save(commit=False)

                for item in items:
                    item.remaining_quantity = item.quantity
                    item.save()

                    product = item.product
                    product.godown_stock += item.quantity
                    update_product_stock(product)

                formset.save_m2m()

                # Record payments
                if paid_from_advance > 0:
                    PurchasePayment.objects.create(
                        purchase=purchase,
                        amount=paid_from_advance,
                        method='advance',
                        note='Paid from advance payment'
                    )
                    supplier.advance_payment -= paid_from_advance
                    supplier.total_payment += paid_from_advance
                    supplier.save()

                if paid_from_account > 0:
                    PurchasePayment.objects.create(
                        purchase=purchase,
                        amount=paid_from_account,
                        method=purchase.payment_method,
                        note='Paid from account'
                    )

                    if purchase.payment_method == 'bkash':
                        bkash_account.balance -= paid_from_account
                        bkash_account.save()
                    elif purchase.payment_method == 'cash':
                        cash_account.balance -= paid_from_account
                        cash_account.save()
                    elif purchase.payment_method == 'bank':
                        bank_account.balance -= paid_from_account
                        bank_account.save()

                    supplier.total_payment += paid_from_account
                    supplier.save()

            return redirect('inventory:purchase_list')

        return render(request, 'inventory/purchase/purchase_form.html', {'form': form, 'formset': formset, 'suppliers': suppliers})





class PurchaseDuePaymentView(View):
    def get(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk)
        form = DuePaymentForm(initial={
            'amount': purchase.due_amount,
            'method': purchase.payment_method
        })
        return render(request, 'inventory/purchase/pay_due_form.html', {'purchase': purchase, 'form': form})

    def post(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk)
        form = DuePaymentForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            method = form.cleaned_data['method']
            note = form.cleaned_data['note']

            if amount > purchase.due_amount:
                form.add_error('amount', 'The repayment amount cannot exceed the due amount.')
                return render(request, 'inventory/purchase/pay_due_form.html', {'purchase': purchase, 'form': form})

            # Check balance
            insufficient_balance = False
            if method == 'bkash':
                account = BkashAccount.objects.first()
            elif method == 'cash':
                account = CashAccount.objects.first()
            elif method == 'bank':
                account = BankAccount.objects.first()
            else:
                account = None

            if not account or account.balance < amount:
                insufficient_balance = True

            if insufficient_balance:
                form.add_error('amount', f"{method.title()} There is not enough balance in the account.")
                return render(request, 'inventory/purchase/pay_due_form.html', {'purchase': purchase, 'form': form})

            # Save payment and update account
            with transaction.atomic():
                PurchasePayment.objects.create(
                    purchase=purchase,
                    amount=amount,
                    method=method,
                    note=note or "Due payment"
                )
                account.balance -= amount
                account.save()

                purchase.paid_amount += amount
                purchase.due_amount -= amount
                purchase.save()
                supplier = purchase.supplier
                supplier.total_payment += amount
                supplier.save()

            return redirect('inventory:purchase_list')

        return render(request, 'inventory/purchase/pay_due_form.html', {'purchase': purchase, 'form': form})






class PurchaseDetailView(DetailView):
    model = Purchase
    template_name = 'inventory/purchase/purchase_detail.html'
    context_object_name = 'purchase'




class TransferStockView(View):
    def get(self, request):
        form = StockTransferForm()
        # Get all products in the form's queryset
        products = form.fields['product'].queryset
        # Prepare product ID to godown_stock mapping
        product_stock = {p.id: p.godown_stock for p in products}

        context = {
            'form': form,
            'product_stock_json': json.dumps(product_stock, cls=DjangoJSONEncoder),
        }
        return render(request, 'inventory/transfer_stock.html', context)

    def post(self, request):
        form = StockTransferForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            qty = form.cleaned_data['quantity']
            if product.godown_stock >= qty:
                product.godown_stock -= qty
                product.office_stock += qty
                update_product_stock(product)
                messages.success(request, "Stock transferred successfully.")
            else:
                messages.error(request, "Not enough stock in godown.")
            return redirect('inventory:transfer_stock')
        return render(request, 'inventory/transfer_stock.html', {'form': form})