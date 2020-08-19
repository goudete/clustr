from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from restaurant_admin.models import Restaurant, Menu, MenuItem
from .models import Cart, MenuItemCounter, Customer
from restaurant_admin.models import Restaurant, SelectOption, AddOnGroup, AddOnItem
from .forms import CustomOrderForm, CustomTipForm, EmailForm, FeedbackForm, PhoneForm
import stripe
import os
from decimal import Decimal
from django.contrib import messages
from django.core import serializers
from kitchen.models import OrderTracker
import phonenumbers
import datetime
from django.utils.translation import gettext as _
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from django.utils import translation
from cashier.email_handlers import send_order_email
from .helpers import assignToCashier
from django.contrib.auth import logout


#this method is only for development, it shows all the menus you have on your local db
def show_all_menus(request, cart_id, restaurant_id):
    curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
    active_menus = Menu.objects.filter(restaurant = curr_rest, displaying = True)
    return render(request, 'customers/all_menus.html', {'menus': active_menus, 'restaurant': curr_rest, 'c_id': cart_id})

#sets the language of the menu based on the restaurant admin
def set_language(response, language):
    translation.activate(language)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    return response

def create_cart(request, restaurant_id):
    if request.method == 'GET':
        cart = Cart()
        cart.restaurant = Restaurant.objects.filter(id = restaurant_id).first()
        cart.total = 0
        cart.total_with_tip = 0
        cart.save()
        #redirect to view menu page
        response = HttpResponseRedirect('/customers/menus/{c_id}/{r_id}'.format(c_id = cart.id, r_id = restaurant_id))
        set_language(response, Restaurant.objects.filter(id = restaurant_id).first().language)
        return response
    #otherwise it sends you to the page w/ all the menus
    else:
        return redirect('/customers/{r_id}'.format(r_id = restaurant_id))

def cart_to_item(request, restaurant_id, menu_id, item_id):
    if request.method == 'GET':
        cart = Cart()
        cart.restaurant = Restaurant.objects.filter(id = restaurant_id).first()
        cart.total = 0
        cart.total_with_tip = 0
        cart.save()
        #redirect to view menu page
        response = HttpResponseRedirect('/customers/view_item/{c_id}/{r_id}/{m_id}/{i_id}'.format(c_id = cart.id, r_id = restaurant_id, m_id = menu_id, i_id = item_id))
        set_language(response, Restaurant.objects.filter(id = restaurant_id).first().language)
        return response
    #otherwise it sends you to the page w/ all the menus
    else:
        return redirect('/customers/{r_id}'.format(r_id = restaurant_id))

def check_time(rest):
    if (not rest.opening_time) or (not rest.closing_time):
        return True
    curr_time = datetime.datetime.now().time()
    if curr_time < rest.opening_time:
        return False
    elif curr_time > rest.closing_time:
        return False
    return True

#helper function that checks if any category is empty
def empty_categories(curr_rest, curr_menu):
    #gets categories that are empty (in the case all items were disabled)
    empty_cats = []
    categories = SelectOption.objects.filter(restaurant = curr_rest, menus = curr_menu)
    for category in categories:
        q_set = MenuItem.objects.filter(restaurant = curr_rest, category = category.name, menus = curr_menu, is_in_stock = True)
        if len(q_set) == 0:
            empty_cats.append(category.name)
    return empty_cats


'''Displays restaurant's menu'''
def view_menu(request, cart_id, restaurant_id, menu_id):
    if request.method == 'GET':
        curr_cart = Cart.objects.get(id = cart_id)
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        if not check_time(curr_rest):
            return render(request, 'customers/closed.html', {'restaurant': curr_rest})

        #get empty categories, if any exist
        empty_cats = empty_categories(curr_rest, curr_menu)
        if empty_cats:
            categories = SelectOption.objects.filter(restaurant = curr_rest, menus = curr_menu).exclude(name__in = empty_cats)
        else:
            #get all possible categories of menu
            categories = SelectOption.objects.filter(restaurant = curr_rest, menus = curr_menu)

        category_items = {}
        for category in categories:
            q_set = MenuItem.objects.filter(restaurant = curr_rest, category = category.name, menus = curr_menu, is_in_stock = True)
            if len(q_set) > 0:
                category_items[category] = q_set

        return render(request, 'customers/menu.html', {'category_items': category_items, 'restaurant': curr_rest, 'cart': curr_cart, 'menu': curr_menu, 'categories': categories})
    else:
        return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))


'''Renders About page for restaurants'''
def about_page(request, cart_id, restaurant_id, menu_id):
    if request.method == 'GET':
        curr_cart = Cart.objects.get(id = cart_id)
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        return render(request, 'customers/about.html', {'restaurant': curr_rest, 'cart': curr_cart, 'menu': curr_menu})
    else:
        return redirect('/customers/about/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))

''' Helper Function to get groups associated with a MenuItem '''
def get_groups(item):
    return AddOnGroup.objects.filter(menu_items = item)

'''helper method to get addon_items associated with an addon_group'''
def get_items(grp):
    return AddOnItem.objects.filter(group = grp)

'''this method generates a dictionary like this:

     dict = {
             key = addon_group,
             value = <set of addon_items in the addon_group>
    }

    where the key is the addon_group and the value is its related addon_items'''

def item_addon_dict(item):
    dict = {}
    # list = []
    addon_groups = get_groups(item)
    for addon_group in addon_groups:
        addon_items = get_items(addon_group)
        dict[addon_group] = addon_items
        # list.append({addon_group: addon_items})
    # dict[item] = list
    # print(dict)
    return dict


""" for this template, make sure the item has a button to add to the cart, with a specified quantity,
send the item and specified quantity to the add_item url"""
def view_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'GET':
        form = CustomOrderForm()
        item = MenuItem.objects.filter(id = item_id).first()
        curr_cart = Cart.objects.get(id = cart_id)
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()

        addon_dict = item_addon_dict(item)

        return render(request, 'customers/view_item.html', {'item': item, 'cart': curr_cart, 'restaurant': curr_rest, 'menu': curr_menu, 'form':form, 'addon_dict': addon_dict})
    else:
        #if method is a post, then just redirect to this page as a get
        return redirect('/customers/view_item/{c_id}/{r_id}/{m_id}/{i_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id, i_id = item_id))

'''Gets ids of selected addon items when a new item is added to cart'''
def get_selected_addons_ids(request):
    addons = []
    for key, values in request.POST.items():
        if key.startswith('radio_addon_'):
            if values != -1:
                addons.append(values)
    return addons

''' Gets  AddOnItem objects with given ids'''
def get_addon_objects(addons):
    addon_objects = []
    for a in addons:
        addon_ob = AddOnItem.objects.filter(id = a).first()
        if addon_ob:
            addon_objects.append(addon_ob)
    return addon_objects

""" this method will add a new item to a cart if the cart didnt already contain the item,
otherwise it will increase/decrease the quantity of an item in a cart
this method expects a POST request to contain the quantity of the item being added to the cart
it also changes the total price of a cart accordingly"""
def add_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'POST':
        addons = get_selected_addons_ids(request)
        if addons:
            addon_objects = get_addon_objects(addons)


        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_item = MenuItem.objects.filter(id = item_id).first()

        if request.POST['custom_instructions'] == '':
            item_counters = MenuItemCounter.objects.filter(cart = curr_cart).filter(item = MenuItem.objects.filter(id = item_id).first()).filter(custom_instructions = None)

        else:
            item_counters = MenuItemCounter.objects.filter(cart = curr_cart).filter(item = MenuItem.objects.filter(id = item_id).first()).filter(custom_instructions = request.POST['custom_instructions'])

        #check if the item is in the cart or not
        if len(item_counters) == 0:
            form = CustomOrderForm(request.POST)
            order = form.save(commit = False)
            order.cart = curr_cart
            order.item = curr_item
            order.restaurant = Restaurant.objects.filter(id = restaurant_id).first()
            order.save()
            # if addonitems, save addonitems to the modelitemcounter model and get addon items price
            addon_price = 0
            if addons:
                # add addon_objects to model
                order.addon_items.add(*addon_objects)
                #get addon items price
                for addon in addon_objects:
                    addon_price += addon.price

            #handle tip
            if curr_cart.tip != 0:
                if curr_cart.custom_tip:
                    order.price = order.quantity*order.item.price
                    order.save()
                    curr_cart.total += order.price + addon_price
                    curr_cart.total_with_tip += order.price + addon_price
                    curr_cart.save()
                else:
                    tip_percent = round(curr_cart.tip / curr_cart.total, 2) #calculate tip percentage
                    order.price = order.quantity*order.item.price
                    order.save()
                    curr_cart.total += order.price + addon_price
                    curr_cart.tip = round(curr_cart.total * tip_percent, 2)
                    curr_cart.total_with_tip = curr_cart.total + curr_cart.tip
                    curr_cart.save()
            #no tip
            else:
                order.price = order.quantity*order.item.price
                order.save()
                curr_cart.total += order.price + addon_price
                curr_cart.save()
            return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))

        #else same item already exists in cart
        else:
            item_counter = item_counters.first()

            # if addonitems, save addonitems to the modelitemcounter model
            addon_price = 0
            if addons:
                # add addon_objects to model
                item_counter.addon_items.add(*addon_objects)
                #get addon items price
                for addon in addon_objects:
                    addon_price += addon.price

            #handle tip
            if curr_cart.tip != 0:
                if curr_cart.custom_tip:
                    old_total = curr_cart.total - item_counter.price
                    #change itemcounter
                    item_counter.quantity += int(request.POST['quantity'])
                    item_counter.price = item_counter.quantity*item_counter.item.price
                    item_counter.save()
                    #update cart total price
                    curr_cart.total = old_total + item_counter.price + addon_price
                    curr_cart.total_with_tip = item_counter.price + curr_cart.tip + addon_price
                    curr_cart.save()
                else:
                    tip_percent = round(curr_cart.tip / curr_cart.total, 2) #calculate tip percentage
                    #get the old total price of the cart - total price of item
                    old_total = curr_cart.total - item_counter.price
                    #change itemcounter
                    item_counter.quantity += int(request.POST['quantity'])
                    item_counter.price = item_counter.quantity*item_counter.item.price
                    item_counter.save()
                    #update cart total price
                    curr_cart.total = old_total + item_counter.price + addon_price
                    curr_cart.tip = round(curr_cart.total * tip_percent, 2)
                    curr_cart.total_with_tip = curr_cart.total + curr_cart.tip
                    curr_cart.save()
            else:
                #get the old total price of the cart - total price of item
                old_total = curr_cart.total - item_counter.price
                #change itemcounter
                item_counter.quantity += int(request.POST['quantity'])
                item_counter.price = item_counter.quantity*item_counter.item.price
                item_counter.save()
                #update cart total price
                curr_cart.total = old_total + item_counter.price + addon_price
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

''' When plus icon is pressed on view_cart, ajax sends cart_id and MenuItem_id to this view. Then,
    MenuItemCounter.quantity is increased by 1. Depending on whether the cart has tip, it calculates
    new totals and sends JSON response back to client'''
def ajax_increase_quantity(request):
    cart_id = request.GET.get('cart_id', None)
    menu_item_name = request.GET.get('menu_item', None)
    # print('cart_id:', cart_id)
    # print('menu_item:', menu_item_name)
    item_counters = MenuItemCounter.objects.filter(cart = cart_id).all()
    curr_cart = Cart.objects.filter(id = cart_id).first()

    for item_counter in item_counters:
        if item_counter.item.name == menu_item_name:
            old_total = curr_cart.total - item_counter.price
            item_counter.quantity += 1
            item_counter.price = round(item_counter.quantity * item_counter.item.price, 2)
            item_counter.save()
            quantity = item_counter.quantity
            price = item_counter.price
            #take into account tip
            if curr_cart.tip != 0:
                if curr_cart.custom_tip:
                    curr_cart.total = old_total + item_counter.price
                    curr_cart.total_with_tip += item_counter.item.price
                    curr_cart.save()
                    cart_total = curr_cart.total
                    cart_tip = curr_cart.tip
                    cart_total_with_tip = curr_cart.total_with_tip
                else:
                    tip_percent = round(curr_cart.tip / curr_cart.total, 2)
                    curr_cart.total = old_total + item_counter.price
                    curr_cart.tip = round(curr_cart.total * tip_percent, 2)
                    curr_cart.total_with_tip = curr_cart.total + curr_cart.tip
                    curr_cart.save()
                    cart_total = curr_cart.total
                    cart_tip = curr_cart.tip
                    cart_total_with_tip = curr_cart.total_with_tip
            #no tip included so far
            else:
                curr_cart.total = old_total + item_counter.price
                curr_cart.save()
                cart_total = curr_cart.total
                cart_tip = 0
                cart_total_with_tip = 0

    data = {
        'quantity': quantity,
        'price': price,
        'cart_total': cart_total,
        'cart_tip': cart_tip,
        'cart_total_with_tip': cart_total_with_tip
    }
    return JsonResponse(data)

def ajax_decrease_quantity(request):
    cart_id = request.GET.get('cart_id', None)
    menu_item_name = request.GET.get('menu_item', None)
    # print('cart_id:', cart_id)
    # print('menu_item:', menu_item_name)
    item_counters = MenuItemCounter.objects.filter(cart = cart_id).all()
    curr_cart = Cart.objects.filter(id = cart_id).first()

    for item_counter in item_counters:
        if item_counter.item.name == menu_item_name:
            old_total = curr_cart.total - item_counter.price
            item_counter.quantity -= 1
            item_counter.price = round(item_counter.quantity * item_counter.item.price, 2)
            item_counter.save()
            quantity = item_counter.quantity
            price = item_counter.price
            #take tip into account
            if curr_cart.tip != 0:
                if curr_cart.custom_tip:
                    curr_cart.total = old_total + item_counter.price
                    curr_cart.total_with_tip -= item_counter.item.price
                    curr_cart.save()
                    cart_total = curr_cart.total
                    cart_tip = curr_cart.tip
                    cart_total_with_tip = curr_cart.total_with_tip
                else:
                    tip_percent = round(curr_cart.tip / curr_cart.total, 2)
                    curr_cart.total = old_total + item_counter.price
                    curr_cart.tip = round(curr_cart.total * tip_percent, 2)
                    curr_cart.total_with_tip = curr_cart.total + curr_cart.tip
                    curr_cart.save()
                    cart_total = curr_cart.total
                    cart_tip = curr_cart.tip
                    cart_total_with_tip = curr_cart.total_with_tip
            #no tip included so far
            else:
                curr_cart.total = old_total + item_counter.price
                curr_cart.save()
                cart_total = curr_cart.total
                cart_tip = 0
                cart_total_with_tip = 0

    data = {
        'quantity': quantity,
        'price': price,
        'cart_total': cart_total,
        'cart_tip': cart_tip,
        'cart_total_with_tip': cart_total_with_tip
    }
    return JsonResponse(data)

"""this method gets a menuitemcounter, and changes the instructions, it NEEDS A NEW SET OF INSTRUCTIONS FROM A POST REQUEST AND A MENUITEMCOUNTER ID"""
def change_instructions(request, cart_id, restaurant_id, menu_id):
    if request.method == 'POST':
        item_counter = MenuItemCounter.objects.filter(id = request.POST['item_counter_id'])
        item_counter.instructions = request.POST['custom_instructions']
        item_counter.save()
        return redirect('/customers/view_cart/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))
    else:
        return redirect('/customers/view_cart/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))


"""this method gets called when item_quantity == 0. It totally removes item from cart, and changes the price of the cart accordingly"""
def remove_item(request, cart_id, restaurant_id, menu_id, item_id):
    if request.method == 'POST':
        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        items = MenuItemCounter.objects.filter(cart = curr_cart).all()
        item_remove = MenuItemCounter.objects.filter(cart = curr_cart).filter(id = item_id).first()
        remove_price = item_remove.price

        if curr_cart.tip != 0:
            if curr_cart.custom_tip:
                curr_cart.total -= remove_price
                curr_cart.total_with_tip -= remove_price
                item_remove.delete()
                curr_cart.save()
            else:
                tip_percent = round(curr_cart.tip / curr_cart.total, 2) #calculate tip percentage
                curr_cart.total -= remove_price
                curr_cart.tip = round(curr_cart.total * tip_percent, 2)
                curr_cart.total_with_tip = curr_cart.total + curr_cart.tip
                item_remove.delete()
                curr_cart.save()
        else:
            curr_cart.total -= remove_price
            item_remove.delete()
            curr_cart.save()

        return HttpResponse(status=200)
        #return redirect('/customers/view_cart/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))
    else:
        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        items = MenuItemCounter.objects.filter(cart = curr_cart).all()
        return render(request, 'customers/view_cart.html', {'cart': curr_cart, 'items': items, 'restaurant': curr_rest, 'menu': curr_menu})

#this method displays the overview of a customers cart
def view_cart(request, cart_id, restaurant_id, menu_id):
    if request.method == 'GET':
        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        items = MenuItemCounter.objects.filter(cart = curr_cart).all()

        return render(request, 'customers/view_cart.html', {'cart': curr_cart, 'items': items, 'restaurant': curr_rest, 'menu': curr_menu})
    else:
        #if method is post, just redirect back to page
        return redirect('/customers/view_cart/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))

"""Calculates tip depending on what button is pressed. If custom tip, it is passed with POST method in form"""
def calculate_tip(request, cart_id, restaurant_id, menu_id, tip):
    if request.method == 'POST':
        curr_cart = Cart.objects.filter(id = cart_id).first()
        form = CustomTipForm(request.POST)

        if form.is_valid():
            curr_cart.custom_tip = True
            custom_tip = form.cleaned_data['tip']
            # print("custom_tip", custom_tip)
            curr_cart.tip = custom_tip
            curr_cart.total_with_tip = curr_cart.total + custom_tip
            curr_cart.save()
        return redirect('/customers/view_cart/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))
    else:
        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        items = MenuItemCounter.objects.filter(cart = curr_cart).all()
        tip_amount = round(curr_cart.total * Decimal((tip / 100)), 2)
        curr_cart.custom_tip = False
        curr_cart.tip = tip_amount
        curr_cart.total_with_tip = curr_cart.total + tip_amount
        curr_cart.save()
        return render(request, 'customers/view_cart.html', {'cart': curr_cart, 'items': items, 'restaurant': curr_rest, 'menu': curr_menu})

'''If a restaurant is offering the option of Dine In, this view receives a POST request from
    a form in view_cart. Handles User's choice of Dine In vs To Go'''
def is_dine_in(resp):
    if resp == 'DINEIN':
        return True
    return False

def dine_in_option(request):
    cart_id = request.POST.get('cart_id', None)
    radio_selection = request.POST.get('checked', None)

    if is_dine_in(radio_selection):
        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_cart.dine_in = True
        curr_cart.save()
    # print('SUCCESS: ')

    data = {}
    return JsonResponse(data)



""" This method creates a PaymentIntent (Stripe API), saves the paymentintent id to the cart model and renders
    payment.html. All Stripe stuff is handled in the JS scripts in the payment template. If the cart is
    already paid, it redirects to order_confirmation
"""
def payment(request, cart_id, restaurant_id, menu_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    #1st check if this bill has already been paid, someone could accidentally come here and pay something that they're not meant to
    cart = Cart.objects.filter(id = cart_id).first()
    if cart.is_paid == True:
        ''' If payed, just redirect to order confirmation'''
        return redirect('/customers/order_confirmation/{c_id}'.format(c_id = cart_id))

    user = request.user
    authenticated = user.is_authenticated
    #if they have a stored customer stripe id, give option of paying with previous card.
    card_stored = False
    last4 = '****' #arbitrary. if they have a stored card, we update this later
    if authenticated:
        if Customer.objects.filter(user=user).exists():
            existing_customer = Customer.objects.get(user=user)
            if Customer.objects.get(user=request.user).stripe_id != None:
                card_stored = True
                #get their card info
                payment_methods = stripe.PaymentMethod.list(
                                      customer=existing_customer.stripe_id,
                                      type="card",
                                    )
                payment_method_id = payment_methods['data'][0]['id']
                last4 = payment_methods['data'][0]['card']['last4'] #last four digits in credit card number

    if request.method == 'POST':
        #check whether customer paid with saved card.
        if "previous_card_submit" in request.POST:
            try:
                stripe.PaymentIntent.create(
                amount=int(cart.total_with_tip*100),
                currency='mxn',
                customer=existing_customer.stripe_id,
                payment_method=payment_method_id,
                off_session=True,
                confirm=True,
              )
            except stripe.error.CardError as e:
              err = e.error
              # Error code will be authentication_required if authentication is needed
              print("Code is: %s" % err.code)
              payment_intent_id = err.payment_intent['id']
              payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        else:
            if card_stored:
                payment_methods = stripe.PaymentMethod.list(
                                      customer=existing_customer.stripe_id,
                                      type="card",
                                    )
                stripe.Customer.delete_source(
                  existing_customer.id,
                  payment_methods['data'][1]['id'],
                )

        return redirect('/customers/order_confirmation/{c_id}'.format(c_id = cart_id))
    else:
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        if cart.total_with_tip == 0:
            cart.total_with_tip = cart.total
            cart.save()
        #stripe API stuff here
        #added to save card details if customer authenticated and paying for the first time
        if curr_rest.handle_payment:
            if authenticated and not(card_stored):
                # Create a Customer (stripe API object):
                new_customer = stripe.Customer.create()
                #create customer object we will save to db
                db_customer = Customer(
                    user = user,
                    stripe_id = new_customer.id
                )
                db_customer.save()

                intent = stripe.PaymentIntent.create(
                  payment_method_types=['card'],
                  amount=int((cart.total_with_tip*100)),
                  currency='mxn',
                  setup_future_usage='off_session',
                  customer = new_customer.stripe_id
                  # stripe_account=curr_rest.stripe_account_id,
                )
            elif card_stored:
                intent = stripe.PaymentIntent.create(
                  payment_method_types=['card'],
                  amount=int((cart.total_with_tip*100)),
                  currency='mxn',
                  setup_future_usage='off_session',
                  customer = existing_customer.stripe_id
                  # stripe_account=curr_rest.stripe_account_id,
                )
            else:
                intent = stripe.PaymentIntent.create(
                  payment_method_types=['card'],
                  amount=int((cart.total_with_tip*100)),
                  currency='mxn'
                  # stripe_account=curr_rest.stripe_account_id,
                )
            cart.stripe_order_id = intent.id
            cart.save()
            publishable = settings.STRIPE_PUBLISHABLE_KEY
            return render(request, 'customers/payment.html', {'client_secret':intent.client_secret, 'cart': cart,
                                                              'restaurant': curr_rest, 'menu': curr_menu, 'publishable': publishable,
                                                              'card_stored':card_stored, 'last4':last4})

''' This is an intermediary step between payment and order confirmation. Email and Phone form'''
def card_email_receipt(request, cart_id, restaurant_id, menu_id):
    form = EmailForm()
    phone_form = PhoneForm()
    if request.method == 'GET':
        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
        #If Customer was going to pay cash but changed their mind, mark cash code false
        if curr_cart.cash_payment != None:
             curr_cart.cash_payment = False
             curr_cart.save()
        #create new order tracker if one DNE
        if OrderTracker.objects.filter(cart = curr_cart).exists() == False:
            tracker = OrderTracker(restaurant = curr_cart.restaurant, cart = curr_cart, is_complete = False, phone_number = None)
            tracker.save()
        return render(request, 'customers/card_email_receipt.html', {'cart': curr_cart, 'restaurant': curr_rest, 'menu': curr_menu, 'form': form, 'phone':phone_form})
    else:
        curr_cart = Cart.objects.filter(id = cart_id).first()
        # curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        # curr_menu = Menu.objects.filter(id = menu_id).first()

        form = EmailForm(request.POST)
        if form.is_valid():
            curr_user_email = form.cleaned_data['email_input']
            curr_cart.email = curr_user_email
            curr_cart.save()
            if curr_user_email != None:
                current_date = datetime.date.today()
                logo_photo_path = '{user}/photos/logo/'.format(user = "R" + str(curr_cart.restaurant.id))
                item_counters = MenuItemCounter.objects.filter(cart = curr_cart).all()

                subject, from_email, to = _('Your Receipt'), settings.EMAIL_HOST_USER, curr_user_email
                msg = EmailMultiAlternatives(subject, "Hi", from_email, [to])
                html_template = get_template("emails/receipt/receipt.html").render({
                                                            'date':current_date,
                                                            'receipt_number':curr_cart.id,
                                                            'path':curr_cart.restaurant.photo_path,
                                                            'order_id':curr_cart.id,
                                                            'item_counters': item_counters,
                                                            'cart': curr_cart
                                                })
                msg.attach_alternative(html_template, "text/html")
                msg.send()

        phone_num = PhoneForm(request.POST)
        if request.POST['phone_number'] != ""  and phone_num.is_valid():
            tracker = OrderTracker.objects.filter(cart = curr_cart).first()
            number = request.POST['phone_number']
            tracker.phone_number = number
            tracker.save()
            return redirect('/customers/order_confirmation/{c_id}'.format(c_id = cart_id))
        # else:
        #     return render(request, 'customers/card_email_receipt.html', {'cart': curr_cart, 'restaurant': curr_rest, 'menu': curr_menu, 'form': form, 'phone':phone_form})

        return redirect('/customers/order_confirmation/{c_id}'.format(c_id = cart_id))


def cash_email_receipt(request, cart_id, restaurant_id, menu_id):
    '''Notify cashier that customer is paying cash'''
    form = EmailForm()
    phone_form = PhoneForm()
    curr_cart = Cart.objects.filter(id = cart_id).first()
    curr_cart.is_paid = True
    curr_cart.save()
    curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
    curr_menu = Menu.objects.filter(id = menu_id).first()
    if request.method == 'GET':
        #Mark cash payment
        curr_cart.cash_payment = True
        curr_cart.save()
        #create new order tracker if one DNE
        if OrderTracker.objects.filter(cart = curr_cart).exists() == False:
            tracker = OrderTracker(restaurant = curr_cart.restaurant, cart = curr_cart, is_complete = False, phone_number = None)
            tracker.save()
        return render(request, 'customers/cash_email_receipt.html', {'cart': curr_cart, 'restaurant': curr_rest, 'menu': curr_menu, 'form': form, 'phone':phone_form})
    else:
        curr_cart = Cart.objects.filter(id = cart_id).first()
        form = EmailForm(request.POST)
        if form.is_valid():
            curr_user_email = form.cleaned_data['email_input']
            curr_cart.email = curr_user_email
            curr_cart.save()

        phone_num = PhoneForm(request.POST)
        if request.POST['phone_number'] != "" and phone_num.is_valid():
            tracker = OrderTracker.objects.filter(cart = curr_cart).first()
            number = request.POST['phone_number']
            tracker.phone_number = number
            tracker.save()
            return redirect('/customers/order_confirmation/{c_id}'.format(c_id = cart_id))

        return redirect('/customers/order_confirmation/{c_id}'.format(c_id = cart_id))

def ajax_confirm_cash_payment(request):
    cart_id = request.GET.get('cart_id', None)
    curr_cart = Cart.objects.filter(id = cart_id).first()
    is_paid = curr_cart.is_paid

    data = {
        'is_paid': is_paid
    }

    return JsonResponse(data)

'''This method sends order to kitchen, changes cart.is_paid to true and renders the confirmation page'''
def order_confirmation(request, cart_id):
    #if this method is a get, then theyre seeing the confirmation page
    '''Send order to kitchen to print'''
    if request.method == 'GET':
        cart = Cart.objects.filter(id = cart_id).first()
        curr_rest = cart.restaurant
        cart.is_paid = True
        # assignToCashier(cart,curr_rest)
        cart.paid_at = timezone.now()
        cart.save()
        if curr_rest.order_stream:
            print("passed if statement")
            send_order_email(from_email = settings.EMAIL_HOST_USER, to = curr_rest.order_stream_email, order = cart)
        print('time: ', cart.paid_at)
        items = MenuItemCounter.objects.filter(cart = cart_id)

        return render(request, 'customers/order_confirmation.html', {'cart': cart, 'items': items})
    else:
        #if this is a post, just send back to the view cart page
        return redirect('/customers/view_cart/{c_id}'.format(c_id = cart_id))


'''Handles Feedback form in order_confirmation. '''
def feedback(request, cart_id):
    form = FeedbackForm()
    if request.method == 'POST':
        #handle feedback form
        cart = Cart.objects.filter(id = cart_id).first()
        form = FeedbackForm(request.POST)
        feedback = form.save(commit = False)
        feedback.cart = cart
        feedback.save()
        messages.info(request, "Thank you for your feedback!")
        return redirect('/customers/order_confirmation/{c_id}'.format(c_id = cart_id))
    else:
        cart = Cart.objects.filter(id = cart_id).first()
        return render(request, 'customers/order_confirmation.html', {'cart': cart, 'form': form})

def logout_view(request, restaurant_id):
    logout(request)
    return redirect('/customers/{r_id}'.format(r_id=restaurant_id)) #return to login page
