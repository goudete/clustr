from django.db import models
from restaurant_admin.models import MenuItem
from django.core.validators import MinValueValidator, MaxValueValidator
from restaurant_admin.models import Restaurant
from cashier.models import CashierProfile
from restaurant_admin.models import Restaurant, AddOnItem, AddOnGroup
# Create your models here.

"""this model is synonymous with an order"""
class Cart(models.Model):
    restaurant = models.ForeignKey(Restaurant, null = True, on_delete = models.PROTECT)
    cashier = models.ForeignKey(CashierProfile, null = True, on_delete = models.PROTECT)
    is_paid = models.BooleanField(default = False)
    cash_code = models.CharField(default = None, null = True, max_length = 255) #the code generated if customer wants to pay cash
    total = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0.0)])
    stripe_order_id = models.CharField(null = True, max_length = 255) # The Stripe PaymentIntent API generates an id to reference paymentintent
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True)
    tip = models.DecimalField(default = 0.0, decimal_places=2, max_digits=12, validators=[MinValueValidator(0.0)])
    custom_tip = models.BooleanField(default = False)
    total_with_tip = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0.0)])
    email = models.EmailField(max_length=200)
    receipt_html = models.TextField(null = True)
    is_cancelled = models.BooleanField(default = False)
    dine_in = models.BooleanField(null = True)


""" this model acts as a way to keep track of how many of a MenuItem are in a cart
it has a MenuItem, quantity of that MenuItem, custom instructions for order
and an associated Cart"""
class MenuItemCounter(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField(default = 1)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    custom_instructions = models.CharField(null = True, blank= True, max_length = 255, default=None)
    price = models.DecimalField(decimal_places = 2, max_digits = 12,validators=[MinValueValidator(0.0)], default=0)
    addon_items = models.ManyToManyField(AddOnItem, blank=True)

class Feedback(models.Model):
    feedback = models.CharField(null = True, max_length = 255)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
