from django import forms
from .models import MenuItemCounter
from crispy_forms.helper import FormHelper

class CustomOrderForm(forms.ModelForm):
    class Meta:
        model = MenuItemCounter
        fields = ('custom_instructions', 'quantity')
        widgets = {
            'custom_instructions': forms.Textarea(attrs={'cols': 5, 'rows': 10})
        }

# class CustomOrderForm(forms.ModelForm):
