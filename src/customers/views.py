from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from restaurant_admin.models import Restaurant, Menu, MenuItem
from .models import Cart, MenuItemCounter

# Create your views here.


#this method is only for development, it shows all the menus you have on your local db
def show_all_menus(request):
    menus = Menu.objects.all()
    return render(request, 'customers/all_menus.html', {'menus': menus})


#this method just creates a cart object and then redirects to the menu
#method needs to be a post, otherwise someone could accidentally create 2 carts
def create_cart(request, restaurant_id, menu_id):
    if request.method == 'POST':
        cart = Cart()
        cart.total = 0
        cart.save()
        #redirect to view menu page
        return redirect('/customers/view_menu/{cart_id}/{rest_id}/{m_id}'.format(cart_id = cart.id, rest_id = restaurant_id, m_id = menu_id))
    #otherwise it sends you to the page w/ all the menus
    else:
        return redirect('/customers')

def view_menu(request, cart_id, restaurant_id, menu_id):
    if request.method == 'GET':
        curr_cart = Cart.objects.get(id = cart_id)
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        items = MenuItem.objects.filter(menu = curr_menu)
        return render(request, 'customers/menu.html', {'items': items, 'restaurant': curr_rest})
    else:
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))


""" for this template, make sure the item has a button to add to the cart, with a specified quantity,
send the item and specified quantity to the add_item url"""
def view_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'GET':
        item = MenuItem.objects.filter(id = item_id).first()
        return redirect(request, 'customers/view_item.html', {'item': item})
    else:
        #if method is a post, then just redirect to this page as a get
        return redirect('/customers/view_item/{c_id}/{r_id}/{m_id}/{i_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id, i_id = item_id))


""" this method will add a new item to a cart if the cart didnt already contain the item,
otherwise it will increase/decrease the quantity of an item in a cart
this method expects a POST request to contain the quantity of the item being added to the cart
it also changes the total price of a cart accordingly"""
def add_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'POST':
        curr_cart = Cart.objects.filter(id = cart_id).first()
        item_counters = MenuItemCounter.objects.filter(cart = curr_cart).filter(item = MenuItem.objects.filter(id = item_id).first())
        #check if the item is in the cart or not
        if len(item_counters) == 0:
            #if the length of the query set is 0, then create a new MenuItemCounter
            item_counter = MenuItemCounter(MenuItem.objects.filter(id = item_id).first(), request.POST['quantity'], curr_cart)
            item_counter.save()
            curr_cart.total += (item_counter.item.price*item_counter.quantity)
        #else update current itemcounter
        else:
            item_counter = item_counters.first()
            #get the old total price of the cart - total price of item
            old_total = curr_cart.total - (item_counter.item.price*item_counter.quantity)
            #change itemcounter
            item_counter.quantity = request.POST['quantity']
            item_counter.save()
            #update cart total price
            curr_cart.total = old_total + (item_counter.item.price*item_counter.quantity)
            curr_cart.save()
        #redirect to menu
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))
    #if method isn't a post, just redirect to menu
    else:
        #redirect to menu
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))


"""this method gets an item, and totally removes it from a cart, and changes the price of the cart accordingly
the request type has to be a POST, otherwise someone could accidentally type the url and
remove an item"""
def remove_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'POST':
        curr_cart = Cart.objects.filter(id = cart_id).first()
        item_counter = MenuItemCounter.objects.filter(cart = curr_cart).filter(item = MenuItem.objects.filter(id = item_id).first()).first()
        #get the total cost from the item getting removed
        item_counter_price = item_counter.item.price*item_counter.quantity
        #remove the itemcounter
        item_counter.delete()
        #update cart total price
        curr_cart.total -= item_counter_price
        curr_cart.save()
        #redirect to view cart
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))
    #if this is a get, they're accidentally here so just redirect to viewing cart
    else:
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))


#this method displays the overview of a customers cart
def view_cart(request, cart_id):
    if request.method == 'GET':
        curr_cart = Cart.objects.filter(id = cart_id).first()
        items = MenuItemCounter.objects.filter(cart = curr_cart)
        #the objects inside items are MenuItemCounters, to reference the actual MenuItem associated with a MenuItemCounter
        #in jinja, do {{MenuItemCounter.item}}
        return render(request, 'customers/view_cart.html', {'cart': cart, 'items': items})
    else:
        #if method is post, just redirect back to page
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))


""" this method handles the stripe API process,
if the method recieves a GET, then it displays the page to put in payment info
otherwise the payment info has been sent to stripe, so the status of the cart gets updated
to paid"""
def payment(request, cart_id):
    #this needs to be a post!!! cannot risk someone accidentally getting here from a get request
    if request.method == 'POST':
        cart = Cart.objects.filter(id = cart_id).first()
        cart.is_paid = True
        cart.save()
        #print cart items to kitchen printer
        return HttpResponse('Thank you for your business!')
    else:
        #stripe API stuff here
        #if method is a get, then they're inputting payment info
        return render('customers/payment.html')


#this method displays the total order before the customer pays
def order_confirmation(request, cart_id):
    #if this method is a get, then theyre seeing the confirmation page
    if request.method == 'GET':
        cart = Cart.objects.filter(id = cart_id).first()
        items = MenuItemCounter.objects.filter(cart = curr_cart)
        #the objects inside items are MenuItemCounters, to reference the actual MenuItem associated with a MenuItemCounter
        #in jinja, do {{MenuItemCounter.item}}
        return render(request, 'customers/order_confirmation.html', {'cart': cart, 'items': items})
        # return render(request, 'customers/order_confirmation.html')
    else:
        #if this is a post, just send back to the view cart page
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))
