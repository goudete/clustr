from django.db import models
from restaurant_admin.models import MenuItem
from django.core.validators import MinValueValidator, MaxValueValidator
from cashier.models import CashierProfile
from restaurant_admin.models import Restaurant, AddOnItem, AddOnGroup
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class ShippingInfo(models.Model):
    full_name = models.CharField(null = True, max_length = 255)
    email = models.EmailField(max_length=200)
    tel = models.CharField(null = True, max_length = 255)
    address = models.CharField(null = True, max_length = 255)
    city_name = models.CharField(null = True, max_length = 255)
    city_id = models.CharField(null = True, max_length = 255)
    postcode = models.CharField(null = True, max_length = 255)
    order_tracker = models.ForeignKey('OrderTracker', null = True, on_delete = models.CASCADE)


"""this model is synonymous with an order"""
class Cart(models.Model):
    restaurant = models.ForeignKey(Restaurant, null = True, on_delete = models.PROTECT)
    cashier = models.ForeignKey(CashierProfile, null = True, on_delete = models.PROTECT)
    is_paid = models.BooleanField(default = False)
    is_entered = models.BooleanField(default = False)
    shipping_cost = total = models.DecimalField(default = 0,decimal_places=2, max_digits=12, validators=[MinValueValidator(0.0)])
    total = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0.0)])
    stripe_order_id = models.CharField(null = True, max_length = 255) # The Stripe PaymentIntent API generates an id to reference paymentintent
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True)
    email = models.EmailField(max_length=200)
    receipt_html = models.TextField(null = True)
    is_cancelled = models.BooleanField(default = False)
    cash_payment = models.BooleanField(null = True)
    first_name = models.CharField(null = True, max_length = 255)
    last_name = models.CharField(null = True, max_length = 255)
    shipping_info = models.ForeignKey(ShippingInfo, null = True, on_delete = models.PROTECT)
    #ability for customer to pay with cash (depending on whether merchant/customer are in the same city)
    handle_cash = models.BooleanField(null = True)


"""this model has an associated cart and a boolean field of whether or not the order has been completed
there is also an optional phone number associated w/ the order, if it exists then the person will be texted at that number once the
boolean field is true """
class OrderTracker(models.Model):
    restaurant = models.ForeignKey(Restaurant, null = True, on_delete = models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    is_complete = models.BooleanField(default = False)


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

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    stripe_id =  models.CharField(null = True, max_length = 255)
    shipping_info = models.ForeignKey(ShippingInfo, null = True, on_delete = models.PROTECT)
    shipping_info_stored = models.BooleanField(default = False)
    card_stored = models.BooleanField(default = False)
