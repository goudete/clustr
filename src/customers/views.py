from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from restaurant_admin.models import Restaurant, Menu, MenuItem
from .models import Cart, MenuItemCounter
from .forms import CustomOrderForm
import stripe
import os

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
        return render(request, 'customers/menu.html', {'items': items, 'restaurant': curr_rest, 'cart': curr_cart, 'menu': curr_menu})
    else:
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))


""" for this template, make sure the item has a button to add to the cart, with a specified quantity,
send the item and specified quantity to the add_item url"""
def view_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'GET':
        form = CustomOrderForm()
        item = MenuItem.objects.filter(id = item_id).first()
        curr_cart = Cart.objects.get(id = cart_id)
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        return render(request, 'customers/view_item.html', {'item': item, 'cart': curr_cart, 'restaurant': curr_rest, 'menu': curr_menu, 'form':form})
    else:
        #if method is a post, then just redirect to this page as a get
        return redirect('/customers/view_item/{c_id}/{r_id}/{m_id}/{i_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id, i_id = item_id))


""" Created form that contains custom order and quantity
    Form references ModelItemCounter model
    View_item template
    """

""" this method will add a new item to a cart if the cart didnt already contain the item,
otherwise it will increase/decrease the quantity of an item in a cart
this method expects a POST request to contain the quantity of the item being added to the cart
it also changes the total price of a cart accordingly"""
def add_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'POST':
        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_item = MenuItem.objects.filter(id = item_id).first()
        print('instructions: ', request.POST['custom_instructions'])
        if request.POST['custom_instructions'] == '':
            item_counters = MenuItemCounter.objects.filter(cart = curr_cart).filter(item = MenuItem.objects.filter(id = item_id).first()).filter(custom_instructions = None)
        else:
            item_counters = MenuItemCounter.objects.filter(cart = curr_cart).filter(item = MenuItem.objects.filter(id = item_id).first()).filter(custom_instructions = request.POST['custom_instructions'])
        print(item_counters)
        #check if the item is in the cart or not
        if len(item_counters) == 0:
            form = CustomOrderForm(request.POST)
            order = form.save(commit = False)
            order.cart = curr_cart
            order.item = curr_item
            order.price = order.quantity*order.item.price
            order.save()
            curr_cart.total += order.price
            curr_cart.save()
            return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))
        #else update current itemcounter
        else:
            item_counter = item_counters.first()
            #get the old total price of the cart - total price of item
            old_total = curr_cart.total - item_counter.price
            #change itemcounter
            item_counter.quantity += int(request.POST['quantity'])
            item_counter.price = item_counter.quantity*item_counter.item.price
            item_counter.save()
            #update cart total price
            curr_cart.total = old_total + item_counter.price
            curr_cart.save()
        #redirect to menu
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))
    #if method isn't a post, just redirect to menu
    else:
        #redirect to menu
        form = CustomOrderForm()
        # context = {'form': form}
        return render(request, 'customers/view_item.html', context)
        # return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))


"""this method gets a cart item, and decreases the quantity, it also needs a MenuItemCounter id number from a post request"""
def decrease_quantity(request, cart_id):
    if request.method == 'POST':
        item_counter = MenuItemCounter.objects.filter(id = request.POST['item_counter_id'])
        item_counter.quantity -= 1
        item_counter.save()
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))
    else:
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))


"""this method gets a menuitemcounter, and changes the instructions, it NEEDS A NEW SET OF INSTRUCTIONS FROM A POST REQUEST AND A MENUITEMCOUNTER ID"""
def change_instructions(request, cart_id):
    if request.method == 'POST':
        item_counter = MenuItemCounter.objects.filter(id = request.POST['item_counter_id'])
        item_counter.instructions = request.POST['custom_instructions']
        item_counter.save()
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))
    else:
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))


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
        items = MenuItemCounter.objects.filter(cart = curr_cart).all()
        #the objects inside items are MenuItemCounters, to reference the actual MenuItem associated with a MenuItemCounter
        #in jinja, do {{MenuItemCounter.item}}
        print(curr_cart.total)
        return render(request, 'customers/view_cart.html', {'cart': curr_cart, 'items': items})
    else:
        #if method is post, just redirect back to page
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))


""" this method handles the stripe API process,
if the method recieves a GET, then it displays the page to put in payment info
otherwise the payment info has been sent to stripe, so the status of the cart gets updated
to paid"""
def payment(request, cart_id):
    #1st check if this bill has already been paid, someone could accidentally come here and pay something that they're not meant to
    cart = Cart.objects.filter(id = cart_id).first()
    if cart.is_paid == True:
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))
    #this needs to be a post!!! cannot risk someone accidentally getting here from a get request
    if request.method == 'POST':
        cart = Cart.objects.filter(id = cart_id).first()
        cart.is_paid = True
        cart.save()
        # stripe.api_key = settings.STRIPE_SECRET_KEY
        # intent = stripe.PaymentIntent.create(
        #   amount=cart.total,
        #   currency='usd',
        #    # Verify your integration in this guide by including this parameter
        #   metadata={'integration_check': 'accept_a_payment'},
        # )
        #print cart items to kitchen printer
        return HttpResponse('Thank you for your business!')
    else:
        cart = Cart.objects.filter(id = cart_id).first()
        #stripe API stuff here
        print(cart.total)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
          amount=int((cart.total*100)),
          currency='usd',
           # Verify your integration in this guide by including this parameter
          metadata={'integration_check': 'accept_a_payment'},
        )
        #if method is a get, then they're inputting payment info
        return render(request, 'customers/payment.html', {'client_secret':intent.client_secret})
        # return render(request, 'customers/payment.html')


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
