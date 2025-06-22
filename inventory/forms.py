# inventory/forms.py
from django import forms
from .models import Purchase, PurchaseItem,Supplier,Product
from django.forms.models import inlineformset_factory


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SupplierForm, self).__init__(*args, **kwargs)

        # These fields will not be required during form submission
        self.fields['total_payment'].required = False
        self.fields['advance_payment'].required = False
        self.fields['advance_payment'].required = False


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        
        # এই ফিল্ডগুলোর required ফ্ল্যাগ False করে দেওয়া হলো
        optional_fields = ['current_stock', 'purchase_price', 'office_stock', 'godown_stock', 'damage_stock']
        for field in optional_fields:
            if field in self.fields:
                self.fields[field].required = False


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier',  'total_amount','discount_amount', 'payment_method', 'paid_amount', 'due_amount', 'note']
        
PurchaseItemFormSet = inlineformset_factory(
    parent_model=Purchase,
    model=PurchaseItem,
    fields=['product', 'quantity', 'unit_price',],
    extra=1,
    can_delete=True
)


class DuePaymentForm(forms.Form):
    amount = forms.DecimalField(label="Amount", max_digits=10, decimal_places=2)
    method = forms.ChoiceField(choices=[('cash', 'Cash'), ('bkash', 'Bkash'), ('bank', 'Bank')])
    note = forms.CharField(label="Note", required=False)


class StockTransferForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '1'})
    )