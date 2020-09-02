from django.db import models
from customers.models import Cart
from restaurant_admin.models import Restaurant
from django.contrib.auth.models import User

# Create your models here.
class Kitchen(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE)
    login_number = models.PositiveIntegerField(default = 0)
