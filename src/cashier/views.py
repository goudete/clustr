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
from qr import settings
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
    backend = CashierProfile.objects.get(id = log_no)
    logo_photo_path = backend.restaurant.photo_path
    unentered_orders = orders_dict(rest_id, False)
    incomplete_orders = orders_dict(rest_id, True)
    return render(request,'new_home.html',{'to_enter': unentered_orders, 'to_complete': incomplete_orders, 'log_no': log_no, 'rest_id': rest_id})

def mark_entered(request, rest_id, log_no, cart_id):
    if request.method == 'POST':
        cart = Cart.objects.get(id = cart_id)
        cart.is_entered = True
        cart.save()
        print(cart.is_entered)
    return redirect('/cashier/base/{r}/{l}'.format(r = rest_id, l = log_no))


def cashPaymentView(request, log_no):
    backend = CashierProfile.objects.get(id = log_no)
    logo_photo_path = backend.restaurant.photo_path
    print("we in the wrong view")
    if request.method == "POST":
        form = SubmitOrderCode(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            order_code = cd['order_code']
            print(order_code)
            curr_cart = Cart.objects.filter(cash_code=order_code).first()
            item_counters = MenuItemCounter.objects.filter(cart = curr_cart).all()
            # backend = PasswordlessAuthBackend()
            # user = backend.get_user(request.user.id)
            restaurant = backend.restaurant
            items = MenuItem.objects.filter(restaurant=restaurant)
            alphabetically_sorted = sorted(items, key = lambda x: x.name)
            context = {'cart':curr_cart,'item_counters':item_counters, 'cash_code':order_code,'items':alphabetically_sorted,
                       'name': backend.name,'path':logo_photo_path, 'cashier':backend}
            return render(request,'review_order2.html',context)
        else:
            print("here")
            return render(request,'cash_payment.html',{'form':form})
    form = SubmitOrderCode()
    return render(request,'cash_payment.html',{'form':form})

def reviewOrderView(request, log_no):
    if request.method == "POST":
        jdp = json.dumps(request.POST) #get request into json form
        jsn = json.loads(jdp)
        jsn.pop("csrfmiddlewaretoken")
        cash_code = jsn['cash_code']
        if "confirm_payment" in request.POST: #cashier confirmed the payment
            print(cash_code)
            print("in confirm payment block")
            curr_cart = Cart.objects.filter(cash_code=cash_code).first()

            current_date = datetime.date.today()
            print(log_no)
            cashier = CashierProfile.objects.get(id = log_no)
            logo_photo_path = '{user}/photos/logo/'.format(user = "R" + str(cashier.restaurant.id))
            item_counters = MenuItemCounter.objects.filter(cart = curr_cart).all()

            email = curr_cart.email
            subject, from_email, to = _('Your Receipt'), settings.EMAIL_HOST_USER, email
            msg = EmailMultiAlternatives(subject, "Hi", from_email, [to])
            html_template = get_template("emails/receipt/receipt.html").render({
                                                        'date':current_date,
                                                        'receipt_number':curr_cart.id,
                                                        'path':cashier.restaurant.photo_path,
                                                        'order_id':curr_cart.id,
                                                        'item_counters': item_counters,
                                                        'cart': curr_cart,
                                                        'restaurant_name': cashier.restaurant.name
                                            })
            msg.attach_alternative(html_template, "text/html")
            msg.send()

            curr_cart.is_paid = True
            curr_cart.save()
            return HttpResponseRedirect('/cashier/base/{log}'.format(log = log_no))
        elif "cancel_order" in request.POST: #cashier cacelled order, we delete order object
            curr_cart = Cart.objects.filter(cash_code=cash_code).first()
            curr_cart.is_cancelled = True
            curr_cart.save()
            return HttpResponseRedirect('/cashier/base/{log}'.format(log = log_no))
    return render(request,'review_order2.html', {'cashier': CashierProfile.objects.get(id = log_no)})

def orderHistoryView(request, log_no):
    backend = CashierProfile.objects.get(id = log_no)
    logo_photo_path = backend.restaurant.photo_path

    carts = Cart.objects.filter(restaurant = backend.restaurant)
    return render(request,'order_history.html',{'carts':carts,
                                                'path':logo_photo_path,
                                                'name':backend.name,
                                                'cashier': backend,
                                                'language_code': settings.LANGUAGE_CODE})

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
            # login(request,cashier.user,backend='cashier.auth_backend.PasswordlessAuthBackend')
            # print(request.user.is_authenticated)
            #return render(request,'base2.html',{'name':cashier.name})
            cashier.is_active = True
            cashier.save()
            return HttpResponseRedirect('/cashier/base/{rid}/{id}'.format(rid = rest_id, id = cashier.id))
    return render(request,'cashier_login.html',{'form':form})

def ajax_change_order_quantity(request, log_no):
    backend = CashierProfile.objects.get(id = log_no)
    # user = backend.get_user(request.user.id)
    restaurant = backend.restaurant
    item_name = request.GET.get('item_name', None).strip(' ')
    item_counter_id = request.GET.get('item_counter_id', None)
    cash_code = request.GET.get('cash_code', None)
    indicator = request.GET.get('indicator', None) #1 if we are increasing quantity, 0 if we are decreasing
    print(item_name)
    print(cash_code)
    curr_cart = Cart.objects.filter(restaurant=restaurant).filter(cash_code=cash_code).first()
    item_counter = MenuItemCounter.objects.get(pk = item_counter_id)

    if indicator == '1':
        item_counter.quantity = item_counter.quantity + 1
        item_counter.price += item_counter.item.price
        curr_cart.total += item_counter.item.price
        curr_cart.total_with_tip += item_counter.item.price
        new_price = item_counter.price
        new_quantity = item_counter.quantity
    else:
        item_counter.quantity = item_counter.quantity - 1
        item_counter.price -= item_counter.item.price
        curr_cart.total -= item_counter.item.price
        curr_cart.total_with_tip -= item_counter.item.price
        new_price = item_counter.price
        new_quantity = item_counter.quantity
    if item_counter.quantity == 0:
        item_counter.delete()
    else:
        item_counter.save()
    curr_cart.save()
    return JsonResponse({'new_quantity':new_quantity,'new_price':new_price,
                         'new_total': curr_cart.total,'new_total_with_tip':curr_cart.total_with_tip,
                         'tip_amount':round(curr_cart.total*curr_cart.tip,2)})

def ajax_add_item(request, log_no):
    backend = CashierProfile.objects.get(id = log_no)
    # user = backend.get_user(request.user.id)
    restaurant = backend.restaurant
    item_name = request.GET.get('item_name', None).strip(' ')
    cash_code = request.GET.get('cash_code', None)
    number_items = int(request.GET.get('number_items', None))
    curr_cart = Cart.objects.filter(restaurant=restaurant).filter(cash_code=cash_code).first()
    # restaurant = restaurant = request.user.cashierprofile.restaurant
    menu_item = MenuItem.objects.filter(restaurant=restaurant).filter(name=item_name).first()
    new_item_counter = MenuItemCounter(item=menu_item, restaurant = restaurant, quantity=number_items,cart=curr_cart,
                                       price = menu_item.price*number_items)
    new_item_counter.save()
    curr_cart.total += new_item_counter.price
    curr_cart.total_with_tip += new_item_counter.price
    curr_cart.save()
    data = {'item_name':item_name,'number_items':number_items,'price':menu_item.price,
            'total':menu_item.price*number_items,'new_total':curr_cart.total,
            'new_total_with_tip':curr_cart.total_with_tip, 'item_counter_id':new_item_counter.id}
    return JsonResponse(data)

def cashier_logout(request, log_no):
    cashier.is_active = False
    cashier.save()
    return redirect('/cashier/cashier_login/' + str(log_no)) #return to login page

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
