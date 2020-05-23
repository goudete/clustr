from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from restaurant_admin.models import Restaurant, Menu, MenuItem
from .models import Cart

# Create your views here.
def create_cart(request, restaurant_id, menu_id):
    cart = Cart()
    cart.save()
    #redirect to view menu page
    return redirect('/customers/view_menu/{cart_id}/{rest_id}/{m_id}'.format(cart_id = cart.id, rest_id = restaurant_id, m_id = menu_id))

def view_menu(request, cart_id, restaurant_id, menu_id):
    if request.method == 'GET':
        curr_cart = Cart.objects.get(id = cart_id)
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        items = MenuItem.objects.filter(menu = curr_menu)
        return render(request, 'customers/menu.html', {'items': items, 'restaurant': curr_rest, 'cart': curr_cart, 'menu': curr_menu})
    else:
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))

def view_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'GET':
        item = MenuItem.objects.filter(id = item_id).first()
        return redirect(request, 'customers/view_item.html', {'item': item})
    else:
        #if method is a post, then just redirect to this page as a get
        return redirect('/customers/view_item/{c_id}/{r_id}/{m_id}/{i_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id, i_id = item_id))

def add_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'POST':
        cart = Cart.objects.filter(id = cart_id).first()
        cart.menu_items.add(MenuItem.objects.filter(id = item_id).first())
        cart.save()
        #redirect to menu
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))
    #if method isn't a post, just redirect to menu
    else:
        #redirect to menu
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))

def remove_item(request, cart_id, restaurant_id, menu_id, item_id):
    return HttpResponse('remove this shitc')

def view_cart(request, cart_id):
    if request.method == 'GET':
        cart = Cart.objects.filter(id = cart_id).first()
        items = cart.menu_items.all()
        return render(request, 'customers/view_cart.html', {'cart': cart, 'items': items})
    else:
        #if method is post, just redirect back to page
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))

def payment(request, cart_id):
    #this needs to be a post!!! cannot risk someone accidentally getting here from a get request
    if request.method == 'POST':
        #stripe API stuff here
        cart = Cart.objects.filter(id = cart_id).first()
        cart.is_paid = True
        cart.save()
        #print cart items to kitchen printer
        return HttpResponse('Thank you for your business!')
    else:
        #if method is a get, then they're inputting payment info
        return render('customers/payment.html')

def order_confirmation(request, cart_id):
    #if this method is a get, then theyre seeing the confirmation page
    if request.method == 'GET':
        cart = Cart.objects.filter(id = cart_id).first()
        items = cart.menu_items.all()
        return render(request, 'customers/order_confirmation.html', {'cart': cart, 'items': items})
        # return render(request, 'customers/order_confirmation.html')
    else:
        #if this is a post, just send back to the view cart page
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))
