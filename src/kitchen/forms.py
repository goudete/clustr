from django import forms
from crispy_forms.helper import FormHelper
from .models import Kitchen


class KitchenLoginForm(forms.Form):
    kitchen_code = forms.CharField(max_length=100, required = True, widget=forms.Textarea(attrs={
    'size':40
    }))

    def clean_kitchen_code(self):
        kitchen_code_passed = self.cleaned_data.get('kitchen_code')
        if not(Restaurant.objects.filter(kitchen_login_no=kitchen_code_passed).exists()):
            raise forms.ValidationError(_("Not a valid kitchen code."))
        return kitchen_code_passed

    def __init__(self, *args, **kwargs):
        super(KitchenLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
