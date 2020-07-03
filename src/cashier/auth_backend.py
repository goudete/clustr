from django.contrib.auth.backends import ModelBackend
from .models import CashierProfile
from django.contrib.auth.models import User

class PasswordlessAuthBackend(ModelBackend):
    """Log in to Django without providing a password, just a cashier code/login number

    """
    def authenticate(self, request, rest_id, login):
        try:
            cashier =  CashierProfile.objects.filter(restaurant = rest_id).filter(login_number = login).first()
            return cashier
        except CashierProfile.DoesNotExist:
            return None

    # def get_user(self, user_id):
    #     try:
    #         return User.objects.get(pk=user_id)
    #     except CashierProfile.DoesNotExist:
    #         return None
