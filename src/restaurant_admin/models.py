from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
# Create your models here.

class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    name = models.CharField(_('Restaurant Name'), default = '', max_length = 200)
    info = models.CharField(max_length = 255) #restaurant info
    photo_path = models.CharField(null = True, max_length = 255) #restaurant logo reference

class Menu(models.Model):
    name = models.CharField(_('Name'), default = '', max_length = 200)
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE) #this connects menu to restaurant
    photo_path = models.CharField(null = True, max_length = 255) #to easily reference the s3 storage

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete = models.CASCADE) #this is how the item is linked to a specific menu
    name = models.CharField(_('Name'), default = '', max_length = 200)
    description = models.TextField(_('Description'), default = '')
    course = models.CharField(_('Course'), default = '', max_length = 200) #this is to help organize the menu, somethting like appetizer, entree, dessert, etc..
    price = models.PositiveIntegerField(_('Price'), default = 0)
    photo_path = models.CharField(null = True, max_length = 255) #to easily reference the s3 storage
