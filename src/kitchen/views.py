from django.shortcuts import render, redirect
from .models import OrderTracker
from restaurant_admin.models import Restaurant
from customers.models import MenuItemCounter, Cart
from django.conf import settings
from twilio.rest import Client
from .auth_backend import PasswordlessAuthBackend
from .forms import KitchenLoginForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

# Create your views here.

def kitchen_login(request):
    form = KitchenLoginForm
    if request.method == "POST":
        form = KitchenLoginForm(request.POST)
        if Restaurant.objects.filter(kitchen_login_no = request.POST['login_no']).exists():
            restaurant = Restaurant.objects.filter(kitchen_login_no = request.POST['login_no']).first()
            return redirect('/kitchen/{rest_id}'.format(rest_id = restaurant.id))
        else:
            return render(request,'kitchen/kitchen_login.html', {'form': form})
    return render(request,'kitchen/kitchen_login.html', {'form': form})


#helper function for a query
def cart_query(restaurant_id):
    list = []
    carts = Cart.objects.filter(restaurant = Restaurant.objects.filter(id = restaurant_id).first()).filter(is_paid = True)
    for item in MenuItemCounter.objects.all():
        if item.cart in carts:
            list.append(item)
    return list


def see_orders(request, restaurant_id):
    restaurant = Restaurant.objects.filter(id = restaurant_id).first()
    trackers = OrderTracker.objects.filter(restaurant = restaurant).filter(is_complete = False)
    # print('length of trackers: ', len(trackers))
    items = cart_query(restaurant_id)
    tracker_item_dict = {}
    for i in range(len(trackers)):
        item_list = []
        for item in items:
            if item.cart == trackers[i].cart:
                item_list.append(item)
        if len(item_list) > 0:
            tracker_item_dict[trackers[i]] = item_list
            print(tracker_item_dict)
    return render(request, 'kitchen/active_orders.html', {'dict': tracker_item_dict, 'restaurant': restaurant})


""" helper function to find number of active orders """
def get_active_orders(rest_id):
    #should only get size from payed orders
    restaurant = Restaurant.objects.filter(id = rest_id).first()
    trackers = OrderTracker.objects.filter(restaurant = restaurant).filter(is_complete = False)
    paid_orders = []
    for tracker in trackers:
        if tracker.cart.is_paid:
            paid_orders.append(tracker)
    server_dict_length = len(paid_orders)
    return server_dict_length

def check_new_orders(request):
    browser_dict_length = request.GET.get('dict_length', None)
    rest_id = request.GET.get('rest_id', None)

    server_dict_length = get_active_orders(rest_id)

    if int(browser_dict_length) > int(server_dict_length) or int(browser_dict_length) == int(server_dict_length):
        data = {
            'new_orders': False
        }
    elif int(browser_dict_length) < int(server_dict_length):
        #new orders posted
        data = {
            'new_orders': True
        }

    return JsonResponse(data)


def mark_order_done(request, restaurant_id, tracker_id):
    if request.method == 'POST':
        tracker = OrderTracker.objects.filter(id = tracker_id).first()
        tracker.is_complete = True
        tracker.save()
        #twilio stuff
        if tracker.phone_number != None:
            client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                              from_='+14845099889',
                              body='¡Tu orden de Local Tres esta lista!',
                              to=str(tracker.phone_number)
                          )
    return redirect('/kitchen/{r_id}'.format(r_id = restaurant_id))
