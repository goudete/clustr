from django import forms
from django.contrib.auth.models import User
from .models import Restaurant, Menu, MenuItem
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from django.contrib.auth.forms import UserCreationForm
from cashier.models import CashierProfile
from kitchen.models import Kitchen

#this form is to register a new user
class UserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        #input sizing
        self.fields['username'].widget.attrs.update(style='width: 200px;')
        self.fields['email'].widget.attrs.update(style='width: 200px;')
        self.fields['password1'].widget.attrs.update(style='width: 200px;')
        self.fields['password2'].widget.attrs.update(style='width: 200px;')


    def clean_email(self):
        email_passed = self.cleaned_data.get('email')
        if User.objects.filter(email=email_passed).exists():
            raise forms.ValidationError("User with that email already exists")
        return email_passed

    class Meta():
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }
        labels = {
            'username': None,
            'password1': None,
            'password2': None,
        }

#form for creating new restaurant
class RestaurantForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RestaurantForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        #stuff about input sizes
        self.fields['name'].widget.attrs.update(style='width: 200px;')

    class Meta:
        model = Restaurant
        fields = ('name',)

#form for creating new menu
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ('name',)

# #form for creating menuphoto
# class MenuCoverPhotoForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(MenuCoverPhotoForm, self).__init__(*args, **kwargs)
#         self.fields['photo'].required = False
#
#     class Meta:
#         model = MenuCoverPhoto
#         fields = ('photo',)

#form for creating new menu item
class MenuItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MenuItemForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['description'].required = False
        self.fields['category'].required = True
        self.fields['price'].required = True
        #sizing stuff
        self.fields['name'].widget.attrs.update(style='width: 450px;',id='add_item_name')
        self.fields['description'].widget.attrs.update(style='width: 450px;',id='add_item_description')
        self.fields['category'].widget.attrs.update(style='width: 450px;',id='add_item_course')
        self.fields['price'].widget.attrs.update(style='width: 450px;',id='add_item_price')

    class Meta:
        model = MenuItem
        fields = ('name', 'description', 'category', 'price')

    def clean_name(self):
        name_passed = self.cleaned_data.get("name")
        if len(MenuItem.objects.filter(name=name_passed))>0:
            raise forms.ValidationError("You have already created an item with this name")
        return name_passed


class CashierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CashierForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['login_number'].required = True

    def clean_login_number(self):
        login_no = self.cleaned_data.get('login_number')
        if CashierProfile.objects.filter(login_number = login_no).exists():
            raise forms.ValidationError("Cashier With that login exists")
        return login_no

    class Meta:
        model = CashierProfile
        fields = ('name', 'login_number')

class KitchenForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(KitchenForm, self).__init__(*args, **kwargs)
        self.fields['login_number'].required = True

    def clean_login_number(self):
        login_no = self.cleaned_data.get('login_number')
        if Kitchen.objects.filter(login_number = login_no).exists():
            raise forms.ValidationError("Kitchen With that login exists")
        return login_no

    class Meta:
        model = Kitchen
        fields = ('login_number',)

class MenuItemFormItemPage(MenuItemForm):
    def __init__(self, *args, **kwargs):
        super(MenuItemForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['category'].required = True
        self.fields['price'].required = True
        #sizing stuff
        self.fields['name'].widget.attrs.update(style='width: 450px;')
        self.fields['description'].widget.attrs.update(style='width: 450px;')
        self.fields['category'].widget.attrs.update(style='width: 450px;')
        self.fields['price'].widget.attrs.update(style='width: 450px;')

class DatesForm(forms.Form): #form for user inputing start and end date
    start_date = forms.CharField(max_length=100, required = True,
    widget=forms.DateInput(attrs={'id':'datepicker', 'class': 'require-if-active',
                                  'data-require-pair': '#include_date','placeholder':'dd-mm-yyyy'})
    )
    start_time = forms.CharField(max_length=100, required = True,
    widget=forms.TimeInput(attrs = {'id': 'timepicker', 'class': 'require-if-active', 'data-require-pair': '#include_time'})
    )

    end_date = forms.CharField(max_length=100, required = True,
    widget=forms.DateInput(attrs={'id':'datepicker2', 'class': 'require-if-active',
                                  'data-require-pair': '#include_date','placeholder':'dd-mm-yyyy'})
    )
    end_time = forms.CharField(max_length=100, required = True,
    widget=forms.TimeInput(attrs = {'id': 'timepicker2', 'class': 'require-if-active', 'data-require-pair': '#include_time'})
    )
    def __init__(self, *args, **kwargs):
        super(DatesForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].required = True
        self.fields['start_time'].required = True
        self.fields['end_date'].required = True
        self.fields['end_time'].required = True

class EditMenuItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditMenuItemForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['description'].required = False
        self.fields['category'].required = False
        self.fields['price'].required = False

        self.fields['name'].widget.attrs.update(id='add_item_name')
        self.fields['description'].widget.attrs.update(id='add_item_description',rows = '6', cols = '60')
        self.fields['category'].widget.attrs.update(id='add_item_course')
        self.fields['price'].widget.attrs.update(id='add_item_price')
        self.helper = FormHelper()
        self.helper.form_show_labels = False


    class Meta:
        model = MenuItem
        fields = ('name', 'description', 'category', 'price')
        required = ()

    def clean_name(self):
        name_passed = self.cleaned_data.get("name")
        if len(MenuItem.objects.filter(name=name_passed))>0:
            raise forms.ValidationError("You have already created an item with this name")
        return name_passed
