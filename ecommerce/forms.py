from django import forms
from .models import Order,ProductCategoryLink

from inventory.models import Product

class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label='Quantity')

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_method']




class ProductCategoryLinkForm(forms.ModelForm):
    class Meta:
        model = ProductCategoryLink
        fields = [
            'product',
            'category',
            'subcategory',
            'image',
            'description',
            'previous_price',
            'selles_price',
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'previous_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'selles_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
