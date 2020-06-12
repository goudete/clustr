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


# Create your views here.
def baseView(request):
    backend = PasswordlessAuthBackend()
    user = backend.get_user(request.user.id)
    return render(request,'base2.html',{'name':user.cashierprofile.name})

def cashPaymentView(request):
    print("we in the wrong view")
    if request.method == "POST":
        form = SubmitOrderCode(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            order_code = cd['order_code']
            print('order_code')
            curr_cart = Cart.objects.filter(cash_code=order_code).first()
            item_counters = MenuItemCounter.objects.filter(cart = curr_cart).all()
            # tip_amount = round((curr_cart.tip/10)*curr_cart.total,2)
            # grand_total = tip_amount + curr_cart.total
            backend = PasswordlessAuthBackend()
            user = backend.get_user(request.user.id)
            restaurant = user.cashierprofile.restaurant
            menus = Menu.objects.filter(restaurant=restaurant)
            items = []
            for menu in menus:
                items += list(MenuItem.objects.filter(menu=menu))
            alphabetically_sorted = sorted(items, key = lambda x: x.name)
            context = {'cart':curr_cart,'item_counters':item_counters, 'cash_code':order_code,'items':alphabetically_sorted}
            return render(request,'review_order2.html',context)
        else:
            print("here")
            return render(request,'cash_payment.html',{'form':form})
    form = SubmitOrderCode()
    return render(request,'cash_payment.html',{'form':form})

def reviewOrderView(request):
    if request.method == "POST":
        jdp = json.dumps(request.POST) #get request into json form
        jsn = json.loads(jdp)
        jsn.pop("csrfmiddlewaretoken")
        cash_code = jsn['cash_code']
        print(cash_code)
        curr_cart = Cart.objects.filter(cash_code=cash_code).first()
        curr_cart.is_paid = True
        curr_cart.save()
        print('is_paid = TRUE')
        print("marked true")

        email = 'luis.costa.laveron@googlemail.com'
        subject, from_email, to = 'Test', settings.EMAIL_HOST_USER, email
        msg = EmailMultiAlternatives(subject, "Hi", from_email, [to])
        msg.send()

        #create new order tracker if one DNE
        if OrderTracker.objects.filter(cart = curr_cart).exists() == False:
            tracker = OrderTracker(restaurant = curr_cart.restaurant, cart = curr_cart, is_complete = False, phone_number = None)
            tracker.save()

        return HttpResponseRedirect('/cashier/base')
    return render(request,'review_order2.html')

def orderHistoryView(request):
    carts = Cart.objects.filter(restaurant = request.user.cashierprofile.restaurant)
    return render(request,'order_history.html',{'carts':carts})

def loginCashier(request):
    form = CashierLoginForm
    if request.method == "POST":
        form = CashierLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cashier_code = cd['cashier_code']
            backend = PasswordlessAuthBackend()
            cashier = backend.authenticate(request,login_number=cashier_code)
            login(request,cashier.user,backend='cashier.auth_backend.PasswordlessAuthBackend')
            print(request.user.is_authenticated)
            #return render(request,'base2.html',{'name':cashier.name})
            return HttpResponseRedirect('/cashier/base')
    return render(request,'cashier_login.html',{'form':form})

def ajax_change_order_quantity(request):
    item_name = request.GET.get('item_name', None).strip(' ')
    cash_code = request.GET.get('cash_code', None)
    indicator = request.GET.get('indicator', None) #1 if we are increasing quantity, 0 if we are decreasing
    print(item_name)
    print(cash_code)
    curr_cart = Cart.objects.filter(cash_code=cash_code).first()
    item_counters = MenuItemCounter.objects.filter(cart = curr_cart).all()
    for item_counter in item_counters:
        if item_counter.item.name == item_name:
            if indicator == '1':
                item_counter.quantity = item_counter.quantity + 1
                item_counter.price += item_counter.item.price
                curr_cart.total += item_counter.item.price
            else:
                item_counter.quantity = item_counter.quantity - 1
                item_counter.price -= item_counter.item.price
                curr_cart.total -= item_counter.item.price
            if item_counter.quantity == 0:
                item_counter.delete()
            else:
                item_counter.save()
            curr_cart.total_with_tip = round(curr_cart.total*(1+curr_cart.tip),2)
            curr_cart.save()
    return JsonResponse({'new_quantity':item_counter.quantity,'new_price':round(item_counter.price,2),
                         'new_total': curr_cart.total,'new_total_with_tip':curr_cart.total_with_tip,
                         'tip_amount':round(curr_cart.total*curr_cart.tip,2)})

def ajax_add_item(request):
    item_name = request.GET.get('item_name', None).strip(' ')
    cash_code = request.GET.get('cash_code', None)
    number_items = int(request.GET.get('number_items', None))
    curr_cart = Cart.objects.filter(cash_code=cash_code).first()
    restaurant = restaurant = request.user.cashierprofile.restaurant
    print(restaurant)

    menus = Menu.objects.filter(restaurant=restaurant)
    for menu in menus:
        if len(MenuItem.objects.filter(menu=menu,name=item_name)) > 0:
            menu_item = MenuItem.objects.filter(menu=menu,name=item_name).first()

    new_item_counter = MenuItemCounter(item=menu_item, quantity=number_items,cart=curr_cart,
                                       price = menu_item.price*number_items)
    new_item_counter.save()
    curr_cart.total += new_item_counter.price
    curr_cart.save()
    data = {'item_name':item_name,'number_items':number_items,'price':menu_item.price,
            'total':menu_item.price*number_items}
    return JsonResponse(data)

def cashier_logout(request):
    logout(request)
    return redirect('/cashier/cashier_login') #return to login page
