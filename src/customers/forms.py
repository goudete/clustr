from django import forms
from .models import MenuItemCounter, Cart, Feedback
from crispy_forms.helper import FormHelper

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

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback',]
        widgets = {
            'feedback': forms.Textarea(attrs={'cols': 5, 'rows': 10})
        }
