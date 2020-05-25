from django import forms
from django.contrib.auth.models import User
from .models import Restaurant, Menu, MenuItem
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from django.contrib.auth.forms import UserCreationForm

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
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
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
        self.fields['info'].required = False
        self.fields['about'].required = False
        #stuff about input sizes
        self.fields['name'].widget.attrs.update(style='width: 200px;')
        self.fields['info'].widget.attrs.update(style='width: 200px; height: 80px;')
        self.fields['about'].widget.attrs.update(style='width: 200px; height: 80px;')

    class Meta:
        model = Restaurant
        fields = ('name', 'info', 'about')

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
        self.fields['description'].required = True
        self.fields['course'].required = True
        self.fields['price'].required = True
        #sizing stuff
        self.fields['name'].widget.attrs.update(style='width: 200px;')
        self.fields['description'].widget.attrs.update(style='width: 200px;')
        self.fields['course'].widget.attrs.update(style='width: 200px;')
        self.fields['price'].widget.attrs.update(style='width: 200px;')

    class Meta:
        model = MenuItem
        fields = ('name', 'description', 'course', 'price')
