from django.shortcuts import render
from .forms import SubmitOrderCode, CashierLoginForm
from restaurant_admin.models import Menu, MenuItem, Restaurant
from .models import CashierProfile
from customers.models import Cart, MenuItemCounter
from .auth_backend import PasswordlessAuthBackend
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse, HttpResponseRedirect
import json
from django.shortcuts import redirect
from django.contrib.auth import update_session_auth_hash
from itertools import chain
from django.core.mail import send_mail, EmailMultiAlternatives
from clustr import settings
from kitchen.models import OrderTracker
from django.utils.translation import gettext as _
import datetime
from django.template.loader import get_template, render_to_string

# Create your views here.

#helper function for a query
def cart_query(restaurant_id, entered):
    carts = Cart.objects.filter(restaurant = Restaurant.objects.filter(id = restaurant_id).first()).filter(is_paid = True).filter(is_entered = entered)
    list = []
    for item in MenuItemCounter.objects.all():
        if item.cart in carts:
            list.append(item)
    return list


def orders_dict(restaurant_id, entered):
    restaurant = Restaurant.objects.filter(id = restaurant_id).first()
    trackers = OrderTracker.objects.filter(restaurant = restaurant).filter(is_complete = False)
    items = cart_query(restaurant_id, entered)
    tracker_item_dict = {}
    for i in range(len(trackers)):
        item_list = []
        for item in items:
            if item.cart == trackers[i].cart:
                item_list.append(item)
        if len(item_list) > 0:
            tracker_item_dict[trackers[i]] = item_list
    return tracker_item_dict


def baseView(request, rest_id, log_no):
    backend = CashierProfile.objects.filter(restaurant = rest_id, id = log_no).first()
    if not backend:
        return redirect('/cashier/cashier_login/{r}'.format(r = rest_id))
    logo_photo_path = backend.restaurant.photo_path
    unentered_orders = orders_dict(rest_id, False)
    incomplete_orders = orders_dict(rest_id, True)
    return render(request,'new_home.html',{'to_enter': unentered_orders, 'to_complete': incomplete_orders, 'log_no': log_no, 'rest_id': rest_id})

def mark_entered(request, rest_id, log_no, cart_id):
    if request.method == 'POST':
        cart = Cart.objects.filter(id = cart_id).first()
        if cart:
            cart.is_entered = True
            cart.save()
    return redirect('/cashier/base/{r}/{l}'.format(r = rest_id, l = log_no))


def loginCashier(request, rest_id):
    form = CashierLoginForm
    if request.method == "POST":
        form = CashierLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cashier_code = cd['cashier_code']
            backend = PasswordlessAuthBackend()
            cashier = backend.authenticate(request, rest_id, cashier_code)
            if cashier == None:
                return render(request,'cashier_login.html',{'form': CashierLoginForm})
            cashier.is_active = True
            cashier.save()
            return HttpResponseRedirect('/cashier/base/{rid}/{id}'.format(rid = rest_id, id = cashier.id))
    return render(request,'cashier_login.html',{'form':form})

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

def mark_order_done(request, restaurant_id, log_no, tracker_id):
    if request.method == 'POST':
        tracker = OrderTracker.objects.filter(id = tracker_id).first()
        if not tracker:
            return redirect('/cashier/base/{r_id}/{l_no}'.format(r_id = restaurant_id, l_no = log_no))
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
    return redirect('/cashier/base/{r_id}/{l_no}'.format(r_id = restaurant_id, l_no = log_no))
