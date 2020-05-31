from django.shortcuts import render
from .forms import SubmitOrderCode, CashierLoginForm
from customers.models import Cart, MenuItemCounter
from .auth_backend import PasswordlessAuthBackend
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponseRedirect
import json
from django.shortcuts import redirect

# Create your views here.
def baseView(request):
    return render(request,'base2.html')

def cashPaymentView(request):
    print("we in the wrong view")
    if request.method == "POST":
        form = SubmitOrderCode(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            order_code = cd['order_code']
            curr_cart = Cart.objects.filter(cash_code=order_code).first()
            item_counters = MenuItemCounter.objects.filter(cart = curr_cart).all()
            tip_amount = round(curr_cart.tip*curr_cart.total,2)
            grand_total = tip_amount + curr_cart.total
            print(curr_cart.tip)
            context = {'cart':curr_cart,'item_counters':item_counters,
                       'tip_amount':tip_amount,'grand_total':grand_total,'cash_code':order_code}
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
        print("marked true")
        return HttpResponseRedirect('/cashier/base')
    return render(request,'review_order2.html')

def orderHistoryView(request):
    return render(request,'order_history.html')

def loginCashier(request):
    form = CashierLoginForm
    if request.method == "POST":
        form = CashierLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cashier_code = cd['cashier_code']
            backend = PasswordlessAuthBackend()
            cashier = backend.authenticate(login_number=cashier_code)
            login(request,cashier.user,backend='cashier.auth_backend.PasswordlessAuthBackend')
            return render(request,'base2.html',{'name':cashier.name})
    return render(request,'cashier_login.html',{'form':form})

def ajax_increase_order_quantity(request):
    item_name = request.GET.get('item_name', None).strip(' ')
    cash_code = request.GET.get('cash_code', None)
    print(item_name)
    print(cash_code)
    curr_cart = Cart.objects.filter(cash_code=cash_code).first()
    item_counters = MenuItemCounter.objects.filter(cart = curr_cart).all()
    for item_counter in item_counters:
        if item_counter.item.name == item_name:
            item_counter.quantity = item_counter.quantity + 1
            item_counter.save()
    return JsonResponse({})

def ajax_decrease_order_quantity(request):
    item_name = request.GET.get('item_name', None).strip(' ')
    cash_code = request.GET.get('cash_code', None)
    print(item_name)
    print(cash_code)
    curr_cart = Cart.objects.filter(cash_code=cash_code).first()
    item_counters = MenuItemCounter.objects.filter(cart = curr_cart).all()
    for item_counter in item_counters:
        if item_counter.item.name == item_name:
            item_counter.quantity = item_counter.quantity - 1
            item_counter.save()
    return JsonResponse({})
