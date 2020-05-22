from django.shortcuts import render
from .forms import SubmitOrderCode
# Create your views here.
def baseView(request):
    return render(request,'base.html')

def cashPaymentView(request):
    form = SubmitOrderCode()
    return render(request,'cash_payment.html',{'form':form})
