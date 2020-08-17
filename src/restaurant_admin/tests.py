from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from .models import Restaurant, Menu
from django.contrib.auth.models import User


from .views import register_view, add_menu, sales, payment_question, remove_menu
# Create your tests here.

#1: MODEL CREATION PROCESSES
class TestRestaurantRegistration(TestCase):
    """Test the process of a restaurant registering and the ensuing model creation"""
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.userData = {'username': 'testRestReg',
                         'email':'luiscl@caltech.edu',
                         'password1':'fuckmysql',
                         'password2':'fuckmysql',
                         'name':'Louies'}
        self.loginData = {'username': 'testRestReg',
                         'password':'fuckmysql',
                         }

    def test_register_view(self):
        c = Client()
        url = reverse('register')
        response =  c.post(url, self.userData, follow=True)
        restaurant = Restaurant.objects.first()
        self.assertEquals(restaurant.name, self.userData['name'])
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.redirect_chain[0][0],'/restaurant_admin/my_menus')

        print(User.objects.first().is_authenticated)

class TestRestaurantViews(TestCase):
    """Test (LIST VIEWS HERE)"""
    def setUp(self):
        self.credentials = {'username': 'loginTest',
                         'password':'fuckmysql',
                         }
        self.user = User.objects.create(**self.credentials)
        self.restaurant = Restaurant.objects.create(user = self.user)

    def test_login_view(self):
        url = reverse('login')
        response =  self.client.post(url, self.credentials, follow=True)

class TestAddMenu(TestCase):
    """Test (LIST VIEWS HERE)"""
    def setUp(self):
        self.request_factory = RequestFactory()
        self.credentials = {'username': 'loginTest',
                         'password':'fuckmysql',
                         }
        self.user = User.objects.create(**self.credentials)
        self.restaurant = Restaurant.objects.create(user = self.user)

    def test_add_menu_view(self):
        url = reverse('add_menu')
        request = self.request_factory.post(url, {'name': 'pengest munch'})
        request.user = self.user
        response = add_menu(request)
        self.assertEquals(Menu.objects.first().name, 'pengest munch')

    def test_sales_view(self):
        url = reverse('sales')
        request = self.request_factory.post(url, {})
        request.user = self.user
        response = sales(request)
        self.assertEquals(response.status_code, 200)

    def test_payment_question_view(self):
        # test when they answer yes
        url = reverse('answer_question')
        request = self.request_factory.post(url,{'answer':'yes'})
        request.user = self.user
        response = payment_question(request)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response.url.startswith('https://connect.stripe.com'))
        self.assertTrue(Restaurant.objects.get(user=self.user).handle_payment)

    def test_remove_menu(self):
        menu = Menu.objects.create(name = 'testRemove', restaurant = self.restaurant)
        url = reverse('remove_menu', kwargs = {'menu_id':menu.id})
        request = self.request_factory.post(url, {})
        request.user = self.user
        response = remove_menu(request, menu.id)
