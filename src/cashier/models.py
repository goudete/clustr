from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from restaurant_admin.models import Restaurant
# Create your models here.

class CashierProfile(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE)
    """ the login_number field is not unique because two cashiers from different restaurants
    can have the same login number, instead there will be a check to make sure that two cashiers that
    work at the same restaurant dont have the same login_number in the restaurant_admin.views"""
    login_number = models.PositiveIntegerField(default = 0)
    name = models.CharField(null = True, max_length = 255)
