from django.test import TestCase
from django.test import Client


# Create your tests here.
class FirstTest(TestCase):
    def test_order_confirmation(self):
        c = Client()
        response = c.post('order_confirmation/12')
        response.status_code
