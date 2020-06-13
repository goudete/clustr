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
    def validate_phone_number(self):
        num = self.cleaned_data.get('phone')
        if phonenumbers.is_valid_number(num):
            return num
        else:
            raise forms.ValidationError(_("Invalid Phone Number"))

    phone = PhoneNumberField(required = False)

    def __init__(self, *args, **kwargs):
        super(PhoneForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback',]
        widgets = {
            'feedback': forms.Textarea(attrs={'cols': 5, 'rows': 10})
        }
