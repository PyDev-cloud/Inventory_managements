from django import forms
from .models import Return, ReturnItem
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ['return_type', 'reference_id', 'reason', 'is_damaged', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2}),
        }

class ReturnItemForm(forms.ModelForm):
    class Meta:
        model = ReturnItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'unit_price': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control unit-price'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty <= 0:
            raise ValidationError("Quantity must be greater than 0")
        return qty

ReturnItemFormSet = inlineformset_factory(
    Return,
    ReturnItem,
    form=ReturnItemForm,
    extra=1,
    can_delete=True
)
