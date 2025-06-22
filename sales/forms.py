from django import forms
from .models import Sale, SaleItem,Customer



class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)

        # Make financial fields not required in form
        self.fields['total_sales'].required = False
        self.fields['total_payment'].required = False
        self.fields['advance_payment'].required = False
        self.fields['due_amount'].required = False



class SalePaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, required=True)
    method = forms.ChoiceField(choices=[('cash', 'Cash'), ('bank', 'Bank'), ('bkash', 'Bkash')])
    note = forms.CharField(widget=forms.Textarea, required=False)

    
    
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'customer', 'discount_amount', 'total_amount', 'payment_method',
            'paid_amount', 'due_amount', 'packing_charge', 'delivery_charge',
             'note'
        ]

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price']

SaleItemFormSet = forms.inlineformset_factory(
    Sale, SaleItem, form=SaleItemForm,
    fields=['product', 'quantity', 'unit_price'], extra=1, can_delete=True
)

class DuePaymentForm(forms.Form):
    amount = forms.DecimalField(label="Amount", max_digits=10, decimal_places=2)
    method = forms.ChoiceField(label="Payment Method", choices=[
        ('cash', 'Cash'),
        ('bkash', 'Bkash'),
        ('bank', 'Bank'),
    ])
    note = forms.CharField(label="Note", required=False)