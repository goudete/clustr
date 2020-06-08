from django.shortcuts import render, redirect
from .models import OrderTracker
from restaurant_admin.models import Restaurant
from customers.models import MenuItemCounter, Cart
from django.conf import settings
from twilio.rest import Client
from .auth_backend import PasswordlessAuthBackend
from .forms import KitchenLoginForm
from django.contrib.auth import login, authenticate
# Create your views here.

def kitchen_login(request):
    form = KitchenLoginForm
    if request.method == "POST":
        form = KitchenLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            kitchen_code = cd['kitchen_code']
            backend = PasswordlessAuthBackend()
            kitchen = backend.authenticate(request,login_number=kitchen_code)
            login(request,kitchen.user,backend='kitchen.auth_backend.PasswordlessAuthBackend')
            id_no = kitchen.restaurant.id
            return redirect('/kitchen/{rest_id}'.format(rest_id = id_no))
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
    trackers = OrderTracker.objects.filter(restaurant = Restaurant.objects.filter(id = restaurant_id).first()).filter(is_complete = False)
    items = cart_query(restaurant_id)
    tracker_item_dict = {}
    for i in range(len(trackers)):
        item_list = []
        for item in items:
            if item.cart == trackers[i].cart:
                item_list.append(item)
        tracker_item_dict[trackers[i]] = item_list
    return render(request, 'kitchen/active_orders.html', {'dict': tracker_item_dict})


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
                              body='Your Order is Ready',
                              to=str(tracker.phone_number)
                          )
    return redirect('/kitchen/{r_id}'.format(r_id = restaurant_id))
