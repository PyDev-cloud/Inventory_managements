from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Product, Category, SubCategory, CartItem, Order
from .forms import CartAddForm, CheckoutForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ProductListView(ListView):
    model = Product
    template_name = 'ecommerce/product_list.html'
    context_object_name = 'products'

class ProductDetailView(DetailView):
    model = Product
    template_name = 'ecommerce/product_detail.html'
    context_object_name = 'product'

@method_decorator(login_required, name='dispatch')
class AddToCartView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = CartAddForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            return redirect('cart_detail')
        return redirect('product_detail', pk=pk)

@method_decorator(login_required, name='dispatch')
class CartDetailView(View):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        total = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'ecommerce/cart_detail.html', {'cart_items': cart_items, 'total': total})

@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    def get(self, request):
        form = CheckoutForm()
        return render(request, 'ecommerce/checkout.html', {'form': form})

    def post(self, request):
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            # Add cart items to order
            cart_items = CartItem.objects.filter(user=request.user)
            for item in cart_items:
                order.items.create(product=item.product, quantity=item.quantity)
                # Decrease inventory
                item.product.current_stock -= item.quantity
                item.product.save()
            cart_items.delete()
            return redirect('order_success', pk=order.pk)
        return render(request, 'ecommerce/checkout.html', {'form': form})

class OrderSuccessView(DetailView):
    model = Order
    template_name = 'ecommerce/order_success.html'
    context_object_name = 'order'
