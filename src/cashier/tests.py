from django.test import TestCase, Client
from .models import CashierProfile
from restaurant_admin.models import Restaurant
from customers.models import Cart, MenuItemCounter
from kitchen.models import OrderTracker
from django.contrib.auth.models import User
# Create your tests here.
class CashierTestCase(TestCase):
    def setup(self):
        #create all the players in the cahier side
        #user
        User.objects.create(username = 'testUser', password = 'testUs3rr')
        #restaurant
        Restaurant.objects.create(user = User.objects.first(), name = 'testRestaurant')
        #cashier
        CashierProfile.objects.create(restaurant = Restaurant.objects.first(), login_number = 42069, name = 'testCashier')
        #cart
        Cart.objects.create(restaurant = Restaurant.objects.first(), total = 0, total_with_tip = 0)
        #order tracker
        OrderTracker.objects.create(restaurant = Restaurant.objects.first(), cart = Cart.objects.first())

    def test_login_API(self):
        self.setup()
        c = Client()
        rest = Restaurant.objects.first()
        cashier = CashierProfile.objects.first()
        print("login_API")
        #w/ wrong cashier code
        wrong_cashier_code = c.post('http://localhost:8000/cashier/cashier_login/{correct_id}'.format(correct_id = rest.id), {'cashier_code': -1})
        print("invalid cashier_code: ", wrong_cashier_code.status_code)
        #w/ wrong restaruant id
        wrong_rest_id = c.post('http://localhost:8000/cashier/cashier_login/0', {'cashier_code':cashier.login_number})
        print("invalid restaurant id: ", wrong_rest_id.status_code)
        #w/ GET request
        get_request = c.get('http://localhost:8000/cashier/cashier_login/{correct_id}'.format(correct_id = rest.id))
        print("with a get request: ", get_request.status_code)
        #w/ correct credentials
        correct = c.post('http://localhost:8000/cashier/cashier_login/{correct_id}'.format(correct_id = rest.id), {'cashier_code':cashier.login_number})
        print("with correct creds: ", correct.status_code)
        print("")

    def test_base_API(self):
        self.setup()
        rest = Restaurant.objects.first()
        cashier = CashierProfile.objects.first()
        c = Client()
        print('base_API')
        #w/ wrong cashier code
        wrong_cashier_code = c.post('http://localhost:8000/cashier/base/{correct_id}/{cashier_code}'.format(correct_id = rest.id, cashier_code = 0))
        print("invalid cashier code: ", wrong_cashier_code.status_code)
        #w/ wrong restaruant id
        wrong_rest_id = c.post('http://localhost:8000/cashier/base/0/{cashier_code}'.format(cashier_code = cashier.login_number))
        print("invalid restaurant id: ", wrong_rest_id.status_code)
        #w/ GET request
        get_request = c.get('http://localhost:8000/cashier/base/{correct_id}/{cashier_code}'.format(correct_id = rest.id, cashier_code = cashier.login_number))
        print("with get request: ", get_request.status_code)
        print("")

    def test_mark_entered_API(self):
        self.setup()
        rest = Restaurant.objects.first()
        cashier = CashierProfile.objects.first()
        cart = Cart.objects.first()
        c = Client()
        print('mark entered API')
        #w/ wrong restaurant id
        wrong_rest_id = c.post('http://localhost:8000/cashier/mark_entered/{r}/{l}/{c}'.format(r = 0, l = cashier.login_number, c = cart.id), {})
        print('wrong restaurant id: ', wrong_rest_id.status_code)
        #w/ wrong login number
        wrong_login_no = c.post('http://localhost:8000/cashier/mark_entered/{r}/{l}/{c}'.format(r = rest.id, l = 0, c = cart.id), {})
        print('wrong login number: ', wrong_login_no.status_code)
        #w/ wrong cart id
        wrong_cart_id = c.post('http://localhost:8000/cashier/mark_entered/{r}/{l}/{c}'.format(r = rest.id, l = cashier.login_number, c = 0), {})
        print('wrong cart id: ', wrong_cart_id.status_code)
        #get request
        get = c.get('http://localhost:8000/cashier/mark_entered/{r}/{l}/{c}'.format(r = rest.id, l = cashier.login_number, c = cart.id))
        print('get requst: ', get.status_code)
        print("")

    def test_check_orders_API(self):
        self.setup()
        rest = Restaurant.objects.first()
        cashier = CashierProfile.objects.first()
        cart = Cart.objects.first()
        c = Client()
        print('check for new orders ajax listener')
        #as a post request
        post_req = c.post('http://localhost:8000/cashier/ajax/check_new_orders', {'random_data':123})
        print('on recieve post request: ', post_req.status_code)
        #invalid restaurant id
        bad_rest_id = c.get('http://localhost:8000/cashier/ajax/check_new_orders', {'dict_length':123, 'rest_id': 0, 'id_array':'[1,5,11,19]'})
        print('invalid restaurant id: ', bad_rest_id.status_code)
        #invalid id array input
        bad_id_array = c.get('http://localhost:8000/cashier/ajax/check_new_orders', {'dict_length':123, 'rest_id': 1, 'id_array':'[\^--=+,P.}'})
        print('invalid id array data: ', bad_id_array.status_code)

    def test_order_done_API(self):
        self.setup()
        rest = Restaurant.objects.first()
        cashier = CashierProfile.objects.first()
        cart = Cart.objects.first()
        tracker = OrderTracker.objects.first()
        c = Client()
        print('check order as done API test')
        #with invalid restaurant id
        bad_rest_id = c.post('http://localhost:8000/cashier/mark_ready/{rid}/{login}/{tid}'.format(rid = 0, login = cashier.login_number, tid = tracker.id))
        print('invalid restaurant id: ', bad_rest_id.status_code)
        #with invalid login number
        bad_log_no = c.post('http://localhost:8000/cashier/mark_ready/{rid}/{login}/{tid}'.format(rid = rest.id, login = 98765, tid = tracker.id))
        print('invalid login number: ', bad_log_no.status_code)
        #with invalid tracker id
        bad_tracker = c.post('http://localhost:8000/cashier/mark_ready/{rid}/{login}/{tid}'.format(rid = rest.id, login = cashier.login_number, tid = 0))
        print('invalid tracker id: ', bad_tracker.status_code)
