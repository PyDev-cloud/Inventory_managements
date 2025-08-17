from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse

from .models import Return, ReturnItem
from .forms import ReturnForm, ReturnItemFormSet
from inventory.models import Product, PurchaseItem,Purchase
from sales.models import SaleItem,Sale, SaleItem
from django.contrib.auth.mixins import LoginRequiredMixin

# Return List
class ReturnListView(LoginRequiredMixin,ListView):
    model = Return
    template_name = 'returns/return_list.html'
    context_object_name = 'returns'
    paginate_by = 20
    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('items', 'items__product')
        return_type = self.request.GET.get('return_type')
        is_damaged = self.request.GET.get('is_damaged')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        reference_id = self.request.GET.get('reference_id')
        product_name = self.request.GET.get('product_name')

        if return_type:
            queryset = queryset.filter(return_type=return_type)
        if is_damaged == 'true':
            queryset = queryset.filter(is_damaged=True)
        elif is_damaged == 'false':
            queryset = queryset.filter(is_damaged=False)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if reference_id:
            queryset = queryset.filter(reference_id=reference_id)
        if product_name:
            queryset = queryset.filter(items__product__name__icontains=product_name).distinct()
        

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['return_type'] = self.request.GET.get('return_type', '')
        context['is_damaged'] = self.request.GET.get('is_damaged', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['reference_id'] = self.request.GET.get('reference_id', '')
        context['product_name'] = self.request.GET.get('product_name', '')
        return context

# Return Details
class ReturnDetailView(LoginRequiredMixin,DetailView):
    model = Return
    template_name = 'returns/return_detail.html'
    context_object_name = 'return_record'

# Return Creation
class ReturnCreateView(LoginRequiredMixin,CreateView):
    model = Return
    form_class = ReturnForm
    template_name = 'returns/return_form.html'
    success_url = reverse_lazy('returns:return_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = ReturnItemFormSet(self.request.POST)
        else:
            data['items'] = ReturnItemFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']

        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()

                # Stock rollback logic
                for item in items:
                    product = item.cleaned_data['product']
                    qty = item.cleaned_data['quantity']

                    if self.object.is_damaged:
                        # ✅ Damaged Return
                        if self.object.return_type == 'sale':
                            # Customer returned damaged product after sale  added to damage_stock
                            product.damage_stock += qty
                        elif self.object.return_type == 'purchase':
                            # Found damaged during purchase  Excluded from office_stock only
                            product.office_stock -= qty
                            product.damage_stock += qty
                    else:
                        # ✅ Normal Return
                        if self.object.return_type == 'sale':
                            # Sold, returned  added to stock
                            product.office_stock += qty
                        elif self.object.return_type == 'purchase':
                            # Bought, returned  Out of stock
                            product.office_stock -= qty

                    product.save()
            else:
                return self.form_invalid(form)

        messages.success(self.request, "Return created successfully!")
        return super().form_valid(form)

# Return Update
class ReturnUpdateView(LoginRequiredMixin,UpdateView):
    model = Return
    form_class = ReturnForm
    template_name = 'returns/return_form.html'
    success_url = reverse_lazy('returns:return_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = ReturnItemFormSet(self.request.POST, instance=self.object)
        else:
            data['items'] = ReturnItemFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']

        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()

                # Stock rollback logic (optional on update; advanced logic needed to handle stock diff)
                for item in items:
                    product = item.cleaned_data['product']
                    qty = item.cleaned_data['quantity']

                    if self.object.return_type == 'sale':
                        product.total_stock += qty
                    elif self.object.return_type == 'purchase':
                        product.total_stock -= qty

                    product.save()
            else:
                return self.form_invalid(form)

        messages.success(self.request, "Return updated successfully!")
        return super().form_valid(form)





# Unit Price Fetch API
def get_unit_price(request):
    product_id = request.GET.get('product_id')
    ref_id = request.GET.get('ref_id')
    return_type = request.GET.get('type')

    print(f"DEBUG: product_id={product_id}, ref_id={ref_id}, return_type={return_type}")

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        print("DEBUG: Product not found")
        return JsonResponse({'unit_price': None})

    item = None
    if return_type == 'purchase':
        purchase = Purchase.objects.filter(invoice_no=ref_id).first()
        print(f"DEBUG: Purchase found: {purchase}")
        if purchase:
            item = PurchaseItem.objects.filter(purchase=purchase, product=product).first()
            print(f"DEBUG: PurchaseItem found: {item}")

    elif return_type == 'sale':
        sale = Sale.objects.filter(invoice_no=ref_id).first()
        print(f"DEBUG: Sale found: {sale}")
        if sale:
            item = SaleItem.objects.filter(sale=sale, product=product).first()
            print(f"DEBUG: SaleItem found: {item}")

    unit_price = item.unit_price if item else None
    print(f"DEBUG: unit_price={unit_price}")
    return JsonResponse({'unit_price': unit_price})
