from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from restaurant_admin.models import Restaurant, Menu, MenuItem

# Create your views here.
def create_cart(request):

    return HttpResponse('filler')

def view_menu(request, restaurant_id, menu_id):
    # curr_cart = Cart.objects.get(id = cart_id)
    curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
    curr_menu = Menu.objects.filter(id = menu_id).first()

    if request.method == 'GET':
        items = MenuItem.objects.filter(menu = curr_menu)
        return render(request, 'customers/menu.html', {'items': items, 'restaurant': curr_rest})

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
