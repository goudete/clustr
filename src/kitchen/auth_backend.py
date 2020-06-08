from django.contrib.auth.backends import ModelBackend
from .models import Kitchen
from django.contrib.auth.models import User

class PasswordlessAuthBackend(ModelBackend):
    """Log in to Django without providing a password, just a cashier code/login number

    """
    def authenticate(self, request, login_number=None):
        try:
            kitchen =  Kitchen.objects.get(login_number=login_number)
            return kitchen
        except Kitchen.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except Kitchen.DoesNotExist:
            return None
