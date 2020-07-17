from django import forms
from crispy_forms.helper import FormHelper
from customers.models import Cart
from .models import CashierProfile
from django.utils.translation import gettext as _


def stringToUpper(string):
    indices = set([0,1])
    return "".join(c.upper() if i in indices else c for i, c in enumerate(string))


class SubmitOrderCode(forms.Form):
    order_code = forms.CharField(max_length=100, required = True, widget=forms.Textarea(attrs={
    'size':40
    }))

    def clean_order_code(self):
        order_code_passed = stringToUpper(self.cleaned_data.get('order_code'))
        if not(Cart.objects.filter(cash_code=order_code_passed).exists()):
            raise forms.ValidationError(_("Order with this code does not exist."))
        elif not(Cart.objects.filter(cash_code=order_code_passed).filter(is_paid = False).exists()):
            raise forms.ValidationError(_("Order is already paid"))
        return order_code_passed

    def __init__(self, *args, **kwargs):
        super(SubmitOrderCode, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

class CashierLoginForm(forms.Form):
    # cashier_code = forms.CharField(max_length=100, required = True, widget=forms.Textarea(attrs={
    # 'size':40
    # }))

    cashier_code = forms.IntegerField(required = True, widget=forms.Textarea(attrs={
    'size':40
    }))
    def clean_cashier_code(self):
        cashier_code_passed = self.cleaned_data.get('cashier_code')
        if not(CashierProfile.objects.filter(login_number=cashier_code_passed).exists()):
            raise forms.ValidationError(_("Not a valid cashier code."))
        return cashier_code_passed

    def __init__(self, *args, **kwargs):
        super(CashierLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

# class ReviewOrderForm(forms.Form):
#     price =
