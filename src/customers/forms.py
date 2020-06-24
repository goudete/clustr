from django import forms
from .models import MenuItemCounter, Cart, Feedback
from crispy_forms.helper import FormHelper
from phonenumber_field.formfields import PhoneNumberField
import phonenumbers
from django.utils.translation import gettext as _

class CustomOrderForm(forms.ModelForm):
    class Meta:
        model = MenuItemCounter
        fields = ('custom_instructions', 'quantity')
        widgets = {
            'custom_instructions': forms.Textarea(attrs={'cols': 5, 'rows': 10})
        }

class CustomTipForm(forms.Form):
    tip = forms.DecimalField()

class EmailForm(forms.Form):
    email_input = forms.EmailField(required=False, max_length=200)


class PhoneForm(forms.Form):
    phone_number = PhoneNumberField(required = False)

    # def clean_phone_number(self):
    #     num = self.cleaned_data.get('phone_number')
    #     num = phonenumbers.parse('+52' + num, "MX")
    #     print('num: ', num)
    #     if not phonenumbers.is_valid_number(num):
    #         raise forms.ValidationError(_("Invalid Phone Number"), code='invalid')
    #     else:
    #         print('valid number: ', num)
    #         return num



    # def __init__(self, *args, **kwargs):
    #     super(PhoneForm, self).__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.form_show_labels = False


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback',]
        widgets = {
            'feedback': forms.Textarea(attrs={'cols': 5, 'rows': 10})
        }
