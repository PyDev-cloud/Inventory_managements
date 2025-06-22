from django import forms
from .models import Order

class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label='Quantity')

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_method']