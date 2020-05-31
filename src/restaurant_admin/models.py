from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import django.utils.timezone as timezone
# Create your models here.

class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    name = models.CharField(_('Restaurant Name'), default = '', max_length = 200)
    info = models.TextField(_('Additional Info'), null = True, max_length = 255) #restaurant info
    photo_path = models.CharField(null = True, max_length = 255) #restaurant logo reference
    about = models.TextField(_("Your Restaurant's Vision"), null = True, max_length = 255)
    created_at = models.DateTimeField(auto_now_add=True)

class Menu(models.Model):
    name = models.CharField(_('Name'), default = '', max_length = 200)
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE) #this connects menu to restaurant
    photo_path = models.CharField(null = True, max_length = 255) #to easily reference the s3 storage
    created_at = models.DateTimeField(auto_now_add=True)

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete = models.CASCADE) #this is how the item is linked to a specific menu
    name = models.CharField(_('Name'), default = '', max_length = 200)
    description = models.TextField(_('Description'), default = '')
    course = models.CharField(_('Course'), default = '', max_length = 200) #this is to help organize the menu, somethting like appetizer, entree, dessert, etc..
    price = models.DecimalField(_('Price'), decimal_places=2, max_digits=8, validators=[MinValueValidator(0.0)])
    photo_path = models.CharField(null = True, max_length = 255) #to easily reference the s3 storage
    created_at = models.DateTimeField(auto_now_add=True)
