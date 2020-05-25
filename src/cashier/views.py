from django.shortcuts import render
from .forms import SubmitOrderCode
from customers.models import Cart, MenuItemCounter
# Create your views here.
def baseView(request):
    return render(request,'base.html')

def cashPaymentView(request):
    if request.method == "POST":
        form = SubmitOrderCode(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            order_code = cd['order_code']
            curr_cart = Cart.objects.filter(cash_code=order_code).first()
            item_counters = MenuItemCounter.objects.filter(cart = curr_cart).all()
            context = {'cart':curr_cart,'item_counters':item_counters}
            return render(request,'review_order2.html',context)
        else:
            print("here")
            return render(request,'cash_payment.html',{'form':form})
    form = SubmitOrderCode()
    return render(request,'cash_payment.html',{'form':form})

def reviewOrderView(request):
    return render(request,'review_order2.html')
