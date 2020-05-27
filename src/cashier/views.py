from django.shortcuts import render
from .forms import SubmitOrderCode
from customers.models import Cart, MenuItemCounter
# Create your views here.
def baseView(request):
    return render(request,'base2.html')

def cashPaymentView(request):
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
            context = {'cart':curr_cart,'item_counters':item_counters,'tip_amount':tip_amount,'grand_total':grand_total}
            return render(request,'review_order2.html',context)
        else:
            print("here")
            return render(request,'cash_payment.html',{'form':form})
    form = SubmitOrderCode()
    return render(request,'cash_payment.html',{'form':form})

def reviewOrderView(request):
    return render(request,'review_order2.html')
