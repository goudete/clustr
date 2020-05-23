from django.db import models
from restaurant_admin.models import MenuItem
from django.core.validators import MinValueValidator
# Create your models here.

"""this model is synonymous with an order"""
class Cart(models.Model):
    is_paid = models.BooleanField(default = False)
    cash_code = models.CharField(null = True, max_length = 255) #the code generated if customer wants to pay cash
    total = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0.0)])


""" this model acts as a way to keep track of how many of a MenuItem are in a cart
it has a MenuItem, quantity of that MenuItem, custom instructions for order
and an associated Cart"""
class MenuItemCounter(models.Model):
    item = models.ForeignKey(MenuItem, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField(default = 1)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    custom_instructions = models.CharField(null = True, blank= True, max_length = 255)
