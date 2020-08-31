from django import forms
from .models import MenuItemCounter, Cart, Feedback, ShippingInfo
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

class NameForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)

class EmailForm(forms.Form):
    email_input = forms.EmailField(required=False, max_length=200)

class PhoneForm(forms.Form):
    phone_number = PhoneNumberField(required = False)

CHOICES = [('TOGO', 'To Go'), ('DINEIN', 'Dine In')]


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback',]
        widgets = {
            'feedback': forms.Textarea(attrs={'cols': 5, 'rows': 10})
        }

class ShippingInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShippingInfoForm, self).__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs.update({'id':'full_name', 'name':'full_name', 'class':'form-control'})
        self.fields['email'].widget.attrs.update({'id':'email', 'name':'email', 'class':'form-control'})
        self.fields['tel'].widget.attrs.update({'id':'tel', 'name':'tel', 'class':'form-control'})
        self.fields['address'].widget.attrs.update({'id':'address', 'name':'address', 'class':'form-control'})
        self.fields['postcode'].widget.attrs.update({'id':'postcode', 'name':'postcode', 'class':'form-control'})
        self.fields['city_id'].widget.attrs.update({'id':'placeID', 'name':'placeID', 'style':'display: none;'})
        self.fields['city_name'].widget.attrs.update({'id':'placeName', 'name':'placeName', 'style':'display: none;'})
        self.fields['city_id'].required = False
        self.fields['city_name'].required = False


        # self.fields['name'].required = False
        # self.fields['description'].required = False
        # self.fields['category'].required = False
        # self.fields['price'].required = False
        #
        # self.fields['name'].widget.attrs.update(id='add_item_name')
        # self.fields['description'].widget.attrs.update(id='add_item_description',rows = '6', cols = '60')
        # self.fields['category'].widget.attrs.update(id='add_item_course')
        # self.fields['price'].widget.attrs.update(id='add_item_price')
        # self.helper = FormHelper()
        # self.helper.form_show_labels = False
    class Meta:
        model = ShippingInfo
        fields = ('full_name', 'email','tel','address','city_name','city_id','postcode')
