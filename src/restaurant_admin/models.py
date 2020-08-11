from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import django.utils.timezone as timezone
import pyqrcode

class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    name = models.CharField(_('Restaurant Name'), default = '', max_length = 200)
    info = models.TextField(_('Additional Info'), null = True, max_length = 255) #restaurant info
    photo_path = models.CharField(null = True, max_length = 255) #restaurant logo reference
    about = models.TextField(_("Your Restaurant's Vision"), null = True, max_length = 255)
    created_at = models.DateTimeField(auto_now_add=True)
    kitchen_login_no = models.IntegerField(null = True, unique = True)
    #boolean field, if they answered whether or not they want us to handle payments (a popup is there if not)
    answered_pay_question = models.BooleanField(default = False)
    #boolean field if they want us to handle their payments or not, can be null b/c before they answer its neither
    handle_payment = models.BooleanField(null = True)
    #boolean field if they have input their logo/ about info
    info_input = models.BooleanField(default = False)
    #stripe account id
    stripe_account_id = models.CharField(null = True, default = '', max_length = 255)
    dine_in = models.BooleanField(default = False)
    #language
    language = models.CharField(default = 'en-us', max_length = 10)
    #open and closing time
    opening_time = models.TimeField(null = True, auto_now = False, auto_now_add = False)
    closing_time = models.TimeField(null = True, auto_now = False, auto_now_add = False)
    order_stream_email = models.EmailField(null=True,max_length=254)
    #whether emailing order info to order_stream_email is active or not.
    order_stream = models.BooleanField(default = False)
    qr_code_path = models.CharField(null = True, max_length = 255)

class Menu(models.Model):
    name = models.CharField(_('Name'), default = '', max_length = 200)
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE) #this connects menu to restaurant
    photo_path = models.CharField(null = True, max_length = 255) #to easily reference the s3 storage
    qr_code_path = models.CharField(null = True, max_length = 255) #path to qr code svg in S3
    created_at = models.DateTimeField(auto_now_add=True)
    displaying = models.BooleanField(default = True) #control whether or not a menu should appear for customers

class MenuItem(models.Model):
    menus = models.ManyToManyField(Menu) #this is how the item is linked to a specific menu
    restaurant = models.ForeignKey(Restaurant, null=True, on_delete = models.CASCADE)
    name = models.CharField(_('Name'), default = '', max_length = 200)
    description = models.TextField(_('Description'), null = True, default = '')
    category = models.CharField(_('Category'), default = '', max_length = 200) #this is to help organize the menu, somethting like appetizer, entree, dessert, etc..
    price = models.DecimalField(_('Price'), decimal_places=2, max_digits=8, validators=[MinValueValidator(0.0)])
    photo_path = models.CharField(null = True, max_length = 255) #to easily reference the s3 storage
    created_at = models.DateTimeField(auto_now_add=True)
    is_in_stock = models.BooleanField(default = True)

class SelectOption(models.Model):
    name = models.CharField(default = '', max_length = 200)
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE)
    menus = models.ManyToManyField(Menu)

class AddOnGroup(models.Model):
    name = models.CharField(_('Name'), default='', max_length=255)
    restaurant = models.ForeignKey(Restaurant, null = True, on_delete = models.CASCADE)
    menu_items = models.ManyToManyField(MenuItem)

class AddOnItem(models.Model):
    name = models.CharField(_('Name'), default='', max_length=200)
    price = models.DecimalField(_('Price'), decimal_places=2, max_digits=8, validators=[MinValueValidator(0.0)])
    group = models.ForeignKey(AddOnGroup, null=True, on_delete=models.CASCADE)
