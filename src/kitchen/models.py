from django.db import models
from customers.models import Cart
from phonenumber_field.modelfields import PhoneNumberField
from restaurant_admin.models import Restaurant
from django.contrib.auth.models import User

# Create your models here.


"""this model has an associated cart and a boolean field of whether or not the order has been completed
there is also an optional phone number associated w/ the order, if it exists then the person will be texted at that number once the
boolean field is true """
class OrderTracker(models.Model):
    restaurant = models.ForeignKey(Restaurant, null = True, on_delete = models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    is_complete = models.BooleanField(default = False)
    phone_number = PhoneNumberField(null = True)

class Kitchen(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE)
    login_number = models.PositiveIntegerField(default = 0)
