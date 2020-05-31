from django import forms
from crispy_forms.helper import FormHelper
from customers.models import Cart
from .models import CashierProfile

class SubmitOrderCode(forms.Form):
    order_code = forms.CharField(max_length=100, required = True, widget=forms.Textarea(attrs={
    'size':40
    }))

    def clean_order_code(self):
        order_code_passed = self.cleaned_data.get('order_code')
        if not(Cart.objects.filter(cash_code=order_code_passed).exists()):
            raise forms.ValidationError("Order with this code does not exist.")
        return order_code_passed

    def __init__(self, *args, **kwargs):
        super(SubmitOrderCode, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

class CashierLoginForm(forms.Form):
    cashier_code = forms.CharField(max_length=100, required = True, widget=forms.Textarea(attrs={
    'size':40
    }))

    def clean_cashier_code(self):
        cashier_code_passed = self.cleaned_data.get('cashier_code')
        if not(CashierProfile.objects.filter(login_number=cashier_code_passed).exists()):
            raise forms.ValidationError("Not a valid cashier code.")
        return cashier_code_passed

    def __init__(self, *args, **kwargs):
        super(CashierLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

# class ReviewOrderForm(forms.Form):
#     price =
