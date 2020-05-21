from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
def menu(request):
    if request.method == 'GET':

        return render(request, 'customers/menu.html')

def view_item(request):
    if request.method == 'POST':

        return HttpResponse('filler')
        # return redirect(request, 'customers/view_item.html')

def view_cart(request):
    if request.method == 'POST':

        return HttpResponse('filler')
        # return redirect(request, 'customers/view_cart.html')

def payment(request):
    if request.method == 'POST':

        return HttpResponse('filler')
        # return redirect(request, 'customers/payment.html')

def order_confirmation(request):
    if request.method == 'GET':

        return HttpResponse('filler')
        # return render(request, 'customers/order_confirmation.html')
