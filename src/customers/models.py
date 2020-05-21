from django.db import models
from restaurant_admin.models import MenuItem
# Create your models here.

class Cart(models.Model):
    is_paid = models.BooleanField(default = False)
    menu_items = models.ManyToManyField(MenuItem)
    cash_code = models.CharField(null = True, max_length = 255) #the code generated if customer wants to pay cash
