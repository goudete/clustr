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

CHOICES = [('TOGO', 'To Go'), ('DINEIN', 'Dine In')]

# class DineInForm(forms.Form):
#     dine_in = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback',]
        widgets = {
            'feedback': forms.Textarea(attrs={'cols': 5, 'rows': 10})
        }
