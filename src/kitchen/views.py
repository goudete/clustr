from django.shortcuts import render, redirect
from restaurant_admin.models import Restaurant
from customers.models import MenuItemCounter, Cart, OrderTracker
from django.conf import settings
from twilio.rest import Client
from .auth_backend import PasswordlessAuthBackend
from .forms import KitchenLoginForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import re
from django.utils.translation import gettext as _

# Create your views here.

def kitchen_login(request, rest_id):
    form = KitchenLoginForm
    if request.method == "POST":
        form = KitchenLoginForm(request.POST)
        print(Restaurant.objects.get(id = rest_id).kitchen_login_no)
        if form.is_valid():
            print('form valid')
            cd = form.cleaned_data
            kitchen_code = cd['kitchen_code']
            backend = PasswordlessAuthBackend()
            bknd = backend.authenticate(request, kitchen_code)
            print(bknd)
            if not bknd:
                return render(request, 'kitchen/kitchen_login.html', {'form': KitchenLoginForm})
            return redirect('/kitchen/see_orders/{r}'.format(r = rest_id))
    return render(request,'kitchen/kitchen_login.html',{'form':form})


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
            paid_orders.append(tracker.id)
    return paid_orders

""" helper function that checks the array of tracker id numbers, and determines if there are any new ones from get_active_orders()"""
def new_orders(old_list, new_list):
    union = list(set(old_list) | set(new_list))
    if union == old_list:
        return False
    return True

"""helper function that checks if the array of tracker id numbers from get_active_orders() lost any ids bc the order was completed"""
def orders_completed(old_list, new_list):
    intersection = list(set(old_list) & set(new_list))
    if intersection == old_list:
        return False
    return True

"""helper function to turn stringified JSON array back into list of ints"""
def string_to_list(str):
    ans = []
    for char in str:
        if char.isdigit():
            ans.append(int(char))
    return ans

def check_new_orders(request):
    browser_dict_length = request.GET.get('dict_length', None)
    rest_id = request.GET.get('rest_id', None)
    id_array = string_to_list(request.GET.get('id_array', None))
    server_list = get_active_orders(rest_id)
    data = {'new_orders':False, 'orders_completed': False}
    #use helper functions above with id_array
    if new_orders(id_array, server_list):
        data['new_orders'] = True
    elif orders_completed(id_array, server_list):
        data['orders_completed'] = True
    print(data)
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
                              body= _('¡Tu orden de {name} esta lista!').format(name = Restaurant.objects.get(id = restaurant_id).name),
                              to=str(tracker.phone_number)
                          )
    return redirect('/kitchen/see_orders/{r_id}'.format(r_id = restaurant_id))
