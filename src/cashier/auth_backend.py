from django.contrib.auth.backends import ModelBackend
from .models import CashierProfile

class PasswordlessAuthBackend(ModelBackend):
    """Log in to Django without providing a password, just a cashier code/login number

    """
    def authenticate(self, login_number=None):
        try:
            cashier =  CashierProfile.objects.get(login_number=login_number)
            return cashier
        except CashierProfile.DoesNotExist:
            return None

    def get_user(self, login_number):
        try:
            return CashierProfile.objects.get(login_number=login_number)
        except CashierProfile.DoesNotExist:
            return None
