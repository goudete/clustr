from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from restaurant_admin.models import Restaurant, Menu, MenuItem
from .models import Cart, MenuItemCounter, Customer, ShippingInfo, OrderTracker
from restaurant_admin.models import Restaurant, SelectOption, AddOnGroup, AddOnItem
from .forms import CustomOrderForm, EmailForm, FeedbackForm, PhoneForm, NameForm, ShippingInfoForm
import stripe
import os
from decimal import Decimal
from django.contrib import messages
from django.core import serializers
import phonenumbers
import datetime
from django.utils.translation import gettext as _
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from django.utils import translation
from comms.email_handlers import send_order_email
from .helpers import assignToCashier, calculate_shipping
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
        cart.save()
        #redirect to view menu page
        response = HttpResponseRedirect('/customers/view_item/{c_id}/{r_id}/{m_id}/{i_id}'.format(c_id = cart.id, r_id = restaurant_id, m_id = menu_id, i_id = item_id))
        set_language(response, Restaurant.objects.filter(id = restaurant_id).first().language)
        return response
    #otherwise it sends you to the page w/ all the menus
    else:
        return redirect('/customers/{r_id}'.format(r_id = restaurant_id))

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
            # addon_price = 0
            if addons:
                # add addon_objects to model
                order.addon_items.add(*addon_objects)
                #get addon items price
                # for addon in addon_objects:
                #     addon_price += addon.price

            order.price = order.quantity*order.item.price
            order.save()
            curr_cart.total += order.price
            curr_cart.save()
            return redirect('/customers/view_menu/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))

        #else same item already exists in cart
        else:
            item_counter = item_counters.first()

            # if addonitems, save addonitems to the modelitemcounter model
            # addon_price = 0
            if addons:
                # add addon_objects to model
                item_counter.addon_items.add(*addon_objects)
                #get addon items price
                # for addon in addon_objects:
                #     addon_price += addon.price

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

''' When plus icon is pressed on view_cart, ajax sends cart_id and MenuItem_id to this view. Then,
    MenuItemCounter.quantity is increased by 1. Sends JSON response back to client'''
def ajax_increase_quantity(request):
    cart_id = request.GET.get('cart_id', None)
    menu_item_name = request.GET.get('menu_item', None)
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

            curr_cart.total = old_total + item_counter.price
            curr_cart.save()
            cart_total = curr_cart.total

    data = {
        'quantity': quantity,
        'price': price,
        'cart_total': cart_total,
    }
    return JsonResponse(data)

def ajax_decrease_quantity(request):
    cart_id = request.GET.get('cart_id', None)
    menu_item_name = request.GET.get('menu_item', None)
    item_counters = MenuItemCounter.objects.filter(cart = cart_id).all()
    curr_cart = Cart.objects.filter(id = cart_id).first()

    for item_counter in item_counters:
        if item_counter.item.name == menu_item_name:
            old_total = curr_cart.total - item_counter.price
            if item_counter.quantity - 1 == 0:
                item_counter.quantity = 0
                item_counter.price = 0
                item_counter.save()
                quantity = 0
                price = 0
            else:
                item_counter.quantity -= 1
                item_counter.price = round(item_counter.quantity * item_counter.item.price, 2)
                item_counter.save()
                quantity = item_counter.quantity
                price = item_counter.price

            curr_cart.total = old_total + item_counter.price
            curr_cart.save()
            cart_total = curr_cart.total
            print('cart_total:', cart_total)
    data = {
        'quantity': quantity,
        'price': price,
        'cart_total': cart_total,
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
        if curr_cart.total - remove_price == 0:
            curr_cart.total = 0
            curr_cart.save()
            item_remove.delete()
        else:
            curr_cart.total -= remove_price
            curr_cart.save()
            item_remove.delete()

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
                amount=int(cart.total*100),
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
        if not all_in_stock(cart):
            return redirect('/customers/view_cart/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))

        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()
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
                  amount=int((cart.total*100)),
                  currency='mxn',
                  setup_future_usage='off_session',
                  customer = new_customer.stripe_id,
                  stripe_account=curr_rest.stripe_account_id,
                )
            elif card_stored:
                intent = stripe.PaymentIntent.create(
                  payment_method_types=['card'],
                  amount=int((cart.total*100)),
                  currency='mxn',
                  setup_future_usage='off_session',
                  customer = existing_customer.stripe_id,
                  stripe_account=curr_rest.stripe_account_id,
                )
            else:
                intent = stripe.PaymentIntent.create(
                  payment_method_types=['card'],
                  amount=int((cart.total*100)),
                  currency='mxn',
                  stripe_account=curr_rest.stripe_account_id,
                )
            cart.stripe_order_id = intent.id
            publishable = settings.STRIPE_PUBLISHABLE_KEY
            item_counters = MenuItemCounter.objects.filter(cart = cart)
            number_of_items = sum([counter.quantity for counter in item_counters])
            shipping_cost = calculate_shipping(cart)
            cart.total += shipping_cost
            cart.save()
            return render(request, 'customers/payment.html', {'client_secret':intent.client_secret, 'cart': cart, 'number_of_items':number_of_items,
                                                              'restaurant': curr_rest, 'menu': curr_menu, 'publishable': publishable,
                                                              'card_stored':card_stored, 'last4':last4, 'item_counters':item_counters, 'shipping_cost':shipping_cost})





#helper method to get all menuitem counter associated w a cart
def get_mics(c):
    return MenuItemCounter.objects.filter(cart = c)

#helper method to get all addon items associated w menu item counter
def get_addon_items(mic):
    # return AddOnItem.objects.filter(MenuItemCounter = mic)
    return MenuItemCounter.objects.get(id = mic.id).addon_items.all()


#helper method that checks if a cart is ordering too much of any item (ie not enough in stock)
def all_in_stock(crt):
    mics = get_mics(crt)
    for m in mics:
        addons = get_addon_items(m)
        for a in addons:
            if m.quantity > a.quantity:
                return False
    return True

#helper method that decreases the quantity of addon items
def decr_quantity(crt):
    mics = get_mics(crt)
    for m in mics:
        addons = get_addon_items(m)
        for a in addons:
            a.quantity -= m.quantity
            a.save()

#helper function to know pick_up_or_delivery response
def is_pickup(resp):
    if resp == 'pickup':
        return True
    return False

def pick_up_or_delivery(request, cart_id, restaurant_id, menu_id):
    if request.method == 'GET':
        form = ShippingInfoForm()
        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_rest = Restaurant.objects.filter(id = restaurant_id).first()
        curr_menu = Menu.objects.filter(id = menu_id).first()

        if not OrderTracker.objects.filter(cart = curr_cart).exists():
            tracker = OrderTracker(restaurant = curr_cart.restaurant, cart = curr_cart, is_complete = False)
            tracker.save()

        #if we have their info, prepopulate all the fields
        if request.user.is_authenticated:
            if Customer.objects.filter(user = request.user).exists():
                customer = Customer.objects.get(user = request.user)
                if customer.shipping_info_stored:
                    for key in form.fields:
                        form.fields[key].widget.attrs.update({'value': getattr(customer.shipping_info,key)})

        return render(request, 'customers/pick_up_or_delivery.html', {'cart': curr_cart, 'restaurant': curr_rest, 'menu': curr_menu,'form':form})
    else:
        print("POST data")
        print(request.POST)
        curr_cart = Cart.objects.filter(id = cart_id).first()

        dic = request.POST
        # shipping_info = ShippingInfo.objects.create(full_name = dic['full_name'], email = dic['email'], city_name = dic['placeName'],
        #                                             tel = dic['tel'], address = dic['address'], city_id = dic['placeID'], postcode = dic['postcode'])
        form = ShippingInfoForm(request.POST)
        if form.is_valid():
            shipping_info = form.save()
            curr_cart.shipping_info = shipping_info
            if request.user.is_authenticated:
                if Customer.objects.filter(user = request.user).exists():
                    customer = Customer.objects.get(user = request.user)
                    customer.shipping_info = shipping_info
                    customer.shipping_info_stored = True
                    customer.save()
                else:
                    new_customer = Customer.objects.create(user=request.user, shipping_info=shipping_info,
                                                           shipping_info_stored = True)
                    new_customer.save()

            curr_cart.save()
            shipping_info.save()
        return redirect('/customers/payment/{c_id}/{r_id}/{m_id}'.format(c_id = cart_id, r_id = restaurant_id, m_id = menu_id))


def ajax_cash_payment(request):
    cart_id = request.GET.get('cart_id', None)
    curr_cart = Cart.objects.filter(id = cart_id).first()
    curr_cart.cash_payment = True
    curr_cart.save()
    data = {}

    return JsonResponse(data)


def ajax_confirm_cash_payment(request):
    cart_id = request.GET.get('cart_id', None)
    curr_cart = Cart.objects.filter(id = cart_id).first()
    is_paid = curr_cart.is_paid

    data = {
        'is_paid': is_paid
    }

    return JsonResponse(data)

'''This method changes cart.is_paid to true and renders the confirmation page'''
def order_confirmation(request, cart_id):
    #if this method is a get, then they're seeing the confirmation page
    if request.method == 'GET':
        cart = Cart.objects.filter(id = cart_id).first()
        # Decrease addon quantity here
        decr_quantity(cart)
        curr_rest = cart.restaurant
        cart.is_paid = True
        # assignToCashier(cart,curr_rest)
        cart.paid_at = timezone.now()
        cart.save()
        if curr_rest.order_stream:
            send_order_email(from_email = settings.EMAIL_HOST_USER, to = curr_rest.order_stream_email, order = cart)
        # print('time: ', cart.paid_at)
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

def logout_view(request,cart_id, restaurant_id, menu_id):
    print(request.get_full_path())
    logout(request)
    return redirect('/customers/pick_up_or_delivery/{c_id}/{r_id}/{m_id}'.format(r_id=restaurant_id,c_id=cart_id,m_id=menu_id)) #return to login page
