from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Cart, CartItem, Order, OrderItem, ShippingInfo, Payment, CustomerUser, ProductCategoryLink
from .forms import CartAddForm, CheckoutForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User

# পণ্যের তালিকা
class ProductListView(ListView):
    model = ProductCategoryLink
    template_name = 'ecommerce/product_list.html'
    context_object_name = 'products'


# পণ্যের বিস্তারিত
class ProductDetailView(DetailView):
    model = ProductCategoryLink
    template_name = 'ecommerce/product_detail.html'
    context_object_name = 'product'


# কার্টে যোগ করা
class AddToCartView(View):
    def get(self, request, pk):
        """Allow adding to cart via GET (e.g., link click)"""
        try:
            product = get_object_or_404(ProductCategoryLink, pk=pk)
            quantity = int(request.GET.get('quantity', 1))
            return self.handle_add_to_cart(request, product, quantity)
        except Exception as e:
            return HttpResponse(f"❌ GET Error: {str(e)}")

    def post(self, request, pk):
        try:
            product = get_object_or_404(ProductCategoryLink, id=pk)
            quantity = int(request.POST.get("quantity", 1))
            return self.handle_add_to_cart(request, product, quantity)
        except Exception as e:
            return HttpResponse(f"❌ POST Error: {str(e)}")

    from inventory.models import Product  # ensure this import exists

    def handle_add_to_cart(self, request, product, quantity):
        """Handles cart retrieval and item adding logic with stock check (for both login and guest)"""

        # ✅ Step 1: Check stock from Product model
        available_stock = product.product.current_stock
        

        if quantity > available_stock:
            messages.warning(request, f"❌ Only {available_stock} item(s) available in stock.")
            print("Quantity empty")
            return redirect("ecommerce:product_detail", pk=product.pk)

        # ✅ Step 2: Get or create cart
        if request.user.is_authenticated:
            customer, _ = CustomerUser.objects.get_or_create(user=request.user)
            cart, _ = Cart.objects.get_or_create(customer=customer)
        else:
            cart_id = request.session.get("guest_cart_id")
            if cart_id:
                cart = Cart.objects.filter(id=cart_id, customer__isnull=True).first()
                if not cart:
                    cart = Cart.objects.create()
                    request.session["guest_cart_id"] = cart.id
            else:
                cart = Cart.objects.create()
                request.session["guest_cart_id"] = cart.id

        # ✅ Step 3: Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > available_stock:
                messages.warning(
                    request,
                    f"⚠️ You already have {cart_item.quantity} in your cart. Only {available_stock} item(s) in stock."
                )
                return redirect("ecommerce:cart_detail")
            cart_item.quantity = new_quantity
            cart_item.save()

        messages.success(request, "✅ Product added to cart.")
        return redirect("ecommerce:cart_detail")
        

# কার্টের বিস্তারিত



class RemoveFromCartView(View):
    def get(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.delete()
        messages.success(request, "Item removed from your cart.")
        return redirect('ecommerce:cart_detail')


class IncreaseQuantityView(View):
    def get(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        product = cart_item.product.product  # Assuming product is FK to inventory.models.Product
        
        if cart_item.quantity + 1 > product.current_stock:
            messages.error(request, f"Not available Stock {product.name} ")
            
            return redirect('ecommerce:cart_detail')
        
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Quantity increased for {product.name}.")
        return redirect('ecommerce:cart_detail')

class DecreaseQuantityView(View):
    def get(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f"Quantity decreased for {cart_item.product.product.name}.")
        else:
            messages.warning(request, f"Minimum quantity is 1. Cannot decrease further.")

        return redirect('ecommerce:cart_detail')



class CartDetailView(View):
    def get(self, request):
        cart = None

        if request.user.is_authenticated:
            try:
                cart = Cart.objects.filter(customer=request.user.customeruser).first()
            except:
                cart = None
        else:
            cart_id = request.session.get('guest_cart_id')  # ✅ এখানে ঠিক করা হয়েছে
            if cart_id:
                cart = Cart.objects.filter(id=cart_id, customer__isnull=True).first()

        cart_items = cart.items.all() if cart else []

        # Subtotal calculate for each item
        items_with_subtotal = []
        total = 0
        for item in cart_items:
            price = item.product.selles_price  # নিশ্চিত হন এই ফিল্ড মডেলে আছে
            subtotal = price * item.quantity
            total += subtotal
            items_with_subtotal.append({
                'item': item,
                'subtotal': subtotal
            })

        return render(request, 'ecommerce/cart_detail.html', {
            'cart_items': items_with_subtotal,
            'total': total
        })

# চেকআউট ও অর্ডার তৈরি

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cart, CartItem, CustomerUser, Order, OrderItem, ShippingInfo, Payment
from inventory.models import Product
from .models import ProductCategoryLink

class CheckoutView(View):
    def get_cart(self, request):
        """Returns the user's cart — logged-in or guest."""
        if request.user.is_authenticated:
            customer, _ = CustomerUser.objects.get_or_create(user=request.user)
            cart, _ = Cart.objects.get_or_create(customer=customer)
            return cart
        else:
            cart_id = request.session.get("guest_cart_id")
            if cart_id:
                cart = Cart.objects.filter(id=cart_id, customer__isnull=True).first()
                if cart:
                    return cart
            return None

    def get(self, request):
        cart = self.get_cart(request)

        if not cart or not cart.items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect("ecommerce:product_list")  # change to your actual product list URL name

        cart_items = cart.items.all()
        subtotal = sum(item.product.selles_price * item.quantity for item in cart_items)

        # Default shipping
        shipping_fee = 60  # default inside Dhaka
        total = subtotal + shipping_fee

        context = {
            "cart_items": cart_items,
            "subtotal": subtotal,
            "total": total,
        }
        return render(request, "ecommerce/checkout.html", context)

    def post(self, request):
        cart = self.get_cart(request)

        if not cart or not cart.items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect("ecommerce:product_list")

        # Get billing info from POST
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name", "")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        email = request.POST.get("email", "")
        order_notes = request.POST.get("order_notes", "")
        shipping_option = request.POST.get("shipping_option", "inside")
        payment_method = request.POST.get("payment_method", "cod")

        # Calculate totals
        cart_items = cart.items.all()
        subtotal = sum(item.product.selles_price * item.quantity for item in cart_items)
        shipping_fee = 60 if shipping_option == "inside" else 110
        total_price = subtotal + shipping_fee

        # Create or get customer
        if request.user.is_authenticated:
            customer, _ = CustomerUser.objects.get_or_create(user=request.user)
        else:
            customer = None  # Guest order

        # Create Order
        order = Order.objects.create(
            customer=customer,
            total_price=total_price,
            status="pending",
            shipping_address=address,
            payment_method=payment_method,
        )
        
        # Create OrderItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product.product,  # Original inventory product
                quantity=item.quantity,
                price=item.product.selles_price,
            )

        

        # Create ShippingInfo
        ShippingInfo.objects.create(
            order=order,
            full_name=f"{first_name} {last_name}".strip(),
            phone=phone,
            address=address,
            city="Dhaka" if shipping_option == "inside" else "Outside Dhaka",
            postal_code="N/A"
        )

        # Create Payment (optional for cod)
        if payment_method == "cod":
            Payment.objects.create(
                order=order,
                method="cash",
                amount=total_price
            )

        # Clear cart
        cart.items.all().delete()

        messages.success(request, "✅ Order placed successfully!")
        return redirect("ecommerce:order_success", pk=order.pk)  # Create this template/page

# অর্ডার সফল পেজ
class OrderSuccessView(DetailView):
    model = Order
    template_name = 'ecommerce/order_success.html'
    context_object_name = 'order'
