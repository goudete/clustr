from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .forms import UserForm, RestaurantForm, MenuForm, MenuItemForm, CashierForm, KitchenForm, MenuItemFormItemPage, DatesForm, EditMenuItemForm
from django.conf import settings
from django.contrib import messages
from .models import Restaurant, Menu, MenuItem, SelectOption, AddOnGroup, AddOnItem
from urllib.parse import urljoin
import boto3
import magic
from .file_storage import FileStorage
from django.core.files import File
import os
from cashier.models import CashierProfile
from customers.models import Cart, MenuItemCounter
import stripe
import pyqrcode
import png
from django.template.loader import render_to_string
import json
from datetime import datetime
from django.utils import timezone


#  your views here.

"""this function just verifies that you are not trying to edit another restaurant's menu"""
def validate_id_number(request, menu_id):
    menu = Menu.objects.get(id = menu_id)
    print(menu.restaurant, Restaurant.objects.filter(user = request.user).first())
    if menu.restaurant == Restaurant.objects.filter(user = request.user).first():
        return True
    else:
        return False


def login_view(request):
    if request.method == 'POST':
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print('logging in')
            login(request, user)
            print('logged_in')
            return redirect('/restaurant_admin/my_menus')
        else:
            messages.info(request, _('Username or Password is incorrect'))
            return redirect('/restaurant_admin')
    #if method is not post, then render the login form
    context = {}
    return render(request, 'restaurant/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('/restaurant_admin') #return to login page

def register_view(request):
    #if method is a post, then the user submitted a registration from
    if request.method == 'POST':
        form = UserForm(request.POST)
        rest_form = RestaurantForm(request.POST)
        if form.is_valid() and rest_form.is_valid():
            user = form.save()
            restaurant = rest_form.save(commit=False)
            restaurant.user = user
            restaurant.kitchen_login_no = 'QLSTR-'+str(user.id)
            restaurant.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/restaurant_admin/my_menus')
    #if method is get, then user is filling out form
    else:
        form = UserForm()
        rest_form = RestaurantForm()
    context = {'form' : form, 'rest_form' : rest_form}
    return render(request, 'restaurant/register.html', context)


"""this method determines whether or not the admin wants us to handle their payments, it has to recieve a
POST request to change anything"""

def payment_question(request):
    me = Restaurant.objects.get(user = request.user)
    if request.method == 'POST':
        answer = request.POST['answer']
        if answer == 'no':
            me.answered_pay_question = True
            me.handle_payment = False
            me.save()
            return redirect('/restaurant_admin/my_menus')
        else:
            # stripe.api_key = settings.STRIPE_SECRET_KEY
            # stripe.Account.create(
            #   type="custom",
            #   email=me.user.email,
            #   requested_capabilities=[
            #     "card_payments",
            #     "transfers",
            #   ],
            # )
            me.answered_pay_question = True
            me.handle_payment = True
            me.save()
            # return redirect("https://connect.stripe.com/express/oauth/authorize?client_id=ca_HNkukA8zfrf8R4YkvrwLOayhitwqn2Q1&state={STATE_VALUE}&suggested_capabilities[]=transfers&stripe_user[email]={email}".format(STATE_VALUE = 'OneBeerAndThenBoom!123OunesOfC0ca1n3', email = me.user.email))
            return redirect("https://connect.stripe.com/oauth/authorize?response_type=code&client_id=ca_HNkukA8zfrf8R4YkvrwLOayhitwqn2Q1&redirect_uri=https://cluster-mvp.herokuapp.com/restaurant_admin/my_menus&state={STATE_VALUE}&scope=read_write&stripe_user[email]={email}".format(STATE_VALUE = 'OneBeerAndThenBoom!123OunesOfC0ca1n3', email = me.user.email))

"""this method recieves a GET request from stripe, and validates the response"""

def stripe_connect(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    print(request.GET)
    if request.method == 'GET':
        print('method is a GET')
        state = request.GET['state']
        #check that the state is the same
        if state != 'OneBeerAndThenBoom!123OunesOfC0ca1n3':
            return HttpResponse('Error, incorrect CSRF')
        #now check stripe code
        code = request.GET['code']
        try:
            response = stripe.OAuth.token(grant_type="authorization_code", code=code,)
        except stripe.oauth_error.OAuthError as e:
            return HttpResponse('invalid code')
        except Exception as e:
            return HttpResponse('internal server error')
        #if everything checks out, save the restaurants stripe account id and redirect to their homepage
        print('all info good')
        account_id = response['stripe_user_id']
        curr_rest = Restaurant.objects.get(user = request.user)
        curr_rest.stripe_account_id = account_id
        curr_rest.save()
        print('redirecting')
        return redirect('https://cluster-mvp.herokuapp.com/restaurant_admin/my_menus')
    else:
        return redirect('https://cluster-mvp.herokuapp.com/restaurant_admin/my_menus')


"""this method is for when a restaurant puts in their info about their restaurant
1st it checks that the method is a post request or get
if post:
2nd it checks if a logo is included -> saves it to S3
3rd it saves the tagline and about info for the restaurant
then it redirects to the my menus page

else:
2nd it renders a page for them to view/edit their about info
3rd sends a post request to this view
"""
#helper function for saving dine in vs togo
def is_dine_in(resp):
    if resp == 'yes':
        return True
    return False

def answer_about(request):
    #query restaurant
    curr_rest = Restaurant.objects.filter(user = request.user).first()
    #check request method
    if request.method == 'POST':
        #check for a logo

        logo = request.FILES.get('logo', False)
        if logo:
            doc = request.FILES['logo'] #get file
            files_dir = '{user}/photos/logo/'.format(user = "R" + str(request.user.id))
            file_storage = FileStorage()
            mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
            doc_path = os.path.join(files_dir, "logo."+mime) #set path for file to be stored in
            file_storage.save(doc_path, doc)
            curr_rest.photo_path = doc_path

        #check for a tagline
        if request.POST['tagline'] != "":
            curr_rest.info = request.POST['tagline']
        #check for about
        if request.POST['about'] != "":
            curr_rest.about = request.POST['about']
        #check for dine in vs togo only
        if is_dine_in(request.POST['dine-in']):
            curr_rest.dine_in = True
        else:
            curr_rest.dine_in = False
        #save
        curr_rest.info_input = True
        curr_rest.save()
        #redirect either way post vs get
        return redirect('/restaurant_admin/my_menus')
    #otherwise render the about page
    else:
        return render(request, 'restaurant/about_info.html', {'me': curr_rest})


def my_menus(request):
    me = Restaurant.objects.get(user = request.user)
    menus = Menu.objects.filter(restaurant =me) #query set of all menus belonging to this restaurant
    form = MenuForm()
    existing_items = MenuItem.objects.filter(restaurant = me)
    return render(request, 'restaurant/my_menus.html', {'menus': menus, 'form': form, 'me': me})


def add_menu(request):
    #if request method is a get, then the user is going to this page for the 1st time
    if request.method == 'GET':
        form = MenuForm()
        return render(request, 'restaurant/add_menu.html', {'form': form})
    #if the method is a post, then they have submitted a new menu
    else:
        menu = MenuForm(request.POST)

        photo = request.FILES.get('photo', False)
        #if file and name included
        if menu.is_valid() and photo:
            new_menu = menu.save(commit = False)
            new_menu.restaurant = Restaurant.objects.get(user = request.user)
            new_menu.save()
            #save photo to AWS
            doc = request.FILES['photo'] #get file
            files_dir = '{user}/photos/m/{menu_num}/'.format(user = "R" + str(request.user.id), menu_num = 'menu'+str(new_menu.id))
            file_storage = FileStorage()
            mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
            doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
            file_storage.save(doc_path, doc)
            new_menu.photo_path = doc_path
            new_menu.save()

        #if they didnt upload a file
        elif menu.is_valid():
            new_menu = menu.save(commit = False)
            new_menu.restaurant = Restaurant.objects.get(user = request.user)
            new_menu.save()
        #generate qr code for menu
        qr_path = '{user}/photos/m/{menu_num}/qr/'.format(user = "R" + str(request.user.id), menu_num = 'menu'+str(new_menu.id))
        qr_url = 'https://cluster-mvp.herokuapp.com/customers/{rest_id}/{men_id}'.format(rest_id = new_menu.restaurant.id, men_id = new_menu.id)
        qr_code = pyqrcode.create(qr_url)
        qr_png = qr_code.png('QR'+str(new_menu.id)+'.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xff])
        file_storage = FileStorage()
        doc_path = os.path.join(qr_path, "QR"+str(new_menu.id)+'.png') #set path for file to be stored in
        file_storage.save(doc_path, open("QR"+str(new_menu.id)+'.png', 'rb'))
        new_menu.qr_code_path = doc_path
        os.unlink('QR'+str(new_menu.id)+'.png')
        new_menu.save()
        #redirect to the edit menu so they can add new stuff to it
        return redirect('edit_menu/{menu}'.format(menu = new_menu.id))


def view_menu(request, menu_id):
    if request.method == 'GET':
        curr_menu = Menu.objects.filter(id = menu_id).first()
        curr_rest = curr_menu.restaurant
        #get all possible categories of menu
        categories = SelectOption.objects.filter(restaurant = curr_rest, menus = curr_menu)
        category_items = {}
        for category in categories:
            q_set = MenuItem.objects.filter(restaurant = curr_rest, category = category.name, menus = curr_menu)
            if len(q_set) > 0:
                category_items[category.name]  = q_set

        # print(category_items)
        return render(request, 'restaurant/menu.html', {'category_items': category_items, 'restaurant': curr_rest, 'menu': curr_menu, 'categories': categories})
    else:
        return redirect('/restaurant_admin/view_menu/{m_id}'.format(m_id = menu_id))


def remove_menu(request, menu_id):
    curr_menu = Menu.objects.filter(id = menu_id).first()
    #if the method is a get, then it sends them to a confirmation page making sure they want to delete the menu
    if request.method == 'GET':
        items = MenuItem.objects.filter(menus = curr_menu) #query all the items, show the user so they know that they'll be deleted
        return render(request, 'restaurant/confirm_remove.html', {'menu':curr_menu, 'items': items})
    #else delete the menu
    else:
        curr_menu.delete()
        return redirect('/restaurant_admin/my_menus')


# this method generates a data structure structured like this:
# {key = menu_item,
#     value = [
#         {
#             inner_key = addon_group,
#             value = <set of addon_items in the addon_group>
#         }
#     ]
# }
# a dictionary, with menu_items as the key, and a list as the value
# within each list are inner dictionaries with addon_group as the key,
# and a set of addon_items as the value

#helper method to get groups associated with a menu_item
def get_groups(item):
    return AddOnGroup.objects.filter(menu_items = item)

#helper method to get addon_items associated with an addon_group
def get_items(grp):
    return AddOnItem.objects.filter(group = grp)

def item_addon_dict(items):
    dict = {}
    for item in items:
        list = []
        addon_groups = get_groups(item)
        for addon_group in addon_groups:
            addon_items = get_items(addon_group)
            list.append({addon_group: addon_items})
        dict[item] = list
    return dict

def edit_menu(request, menu_id):
    if not validate_id_number(request, menu_id):
        return HttpResponse('you are not authorized to view this')
    curr_menu = Menu.objects.filter(id = menu_id).first()
    #check if they uploaded new photo


    photo = request.FILES.get('photo', False)
    if photo:
        # print("issue is here")
        #save photo to AWS
        doc = request.FILES['photo'] #get file
        files_dir = '{user}/photos/m/{menu_num}/'.format(user = "R" + str(request.user.id), menu_num = 'menu'+str(menu_id))
        file_storage = FileStorage()
        mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
        doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
        file_storage.save(doc_path, doc)
        curr_menu.photo_path = doc_path


    #if method is a get, then the user is looking at the menu
    if request.method == 'GET':
        items = MenuItem.objects.filter(menus = curr_menu)
        addon_dict = item_addon_dict(items)
        restaurant = Restaurant.objects.filter(user = request.user).first()
        # print('items queried')
        item_form = MenuItemForm()
        selct_options = SelectOption.objects.filter(restaurant = curr_menu.restaurant)
        print(selct_options)
        existing_items = MenuItem.objects.filter(restaurant = restaurant)
        alphabetically_sorted = sorted(existing_items, key = lambda x: x.name)
        all_grps = AddOnGroup.objects.filter(restaurant = curr_menu.restaurant)
        # print('select options queried')
        #generate pre-signed url to download the QR code

        s3 = boto3.resource('s3') #setup to get from AWS
        aws_dir = '{user}/photos/m/{menu_num}/qr/'.format(user = "R" + str(request.user.id), menu_num = 'menu'+str(curr_menu.id))
        # print('aws dir good')
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        objs = bucket.objects.filter(Prefix=aws_dir) #get folder
        url = "#"
        # print('objs queried')
        for obj in objs: #iterate over file objects in folder
             if os.path.split(obj.key)[1].split('.')[1] == 'png':
                s3Client = boto3.client('s3')
                url = s3Client.generate_presigned_url('get_object', Params = {'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': obj.key}, ExpiresIn = 3600)

        return render(request, 'restaurant/edit_menu.html', {'menu': curr_menu, 'addon_dict':addon_dict, 'item_form': item_form, 'selct_options': selct_options,
                                'url': url, 'all_addon_groups': all_grps, 'existing_items': alphabetically_sorted})
    else:
        curr_menu.name = request.POST['name']
        curr_menu.save()
        return redirect('/restaurant_admin/edit_menu/{num}'.format(num = menu_id)) #redirect back to the same page



#helper method for adding/editing an item
def new_category(request, category):
    curr_rest = Restaurant.objects.filter(user = request.user).first()
    select_options = SelectOption.objects.filter(restaurant = curr_rest) #options for what an item can be classified as
    for option in select_options:
        if option.name == category:
            return False
    return True

def add_item(request, menu_id):
    if not validate_id_number(request, menu_id):
        return HttpResponse('you are not authorized to view this')
    #if method is get, then user is filling out form for new item
    if request.method == 'GET':
        return redirect('/restaurant_admin/edit_menu/{menu}'.format(menu = menu_id))
    #otherwise the user created a new item, and it must be added to the menu
    else:
        if "existing_item_select" in request.POST:
            item_name = request.POST.get("existing_item", None)
            item = MenuItem.objects.filter(restaurant=request.user.restaurant).get(name=item_name)
            menu = Menu.objects.filter(id = menu_id).first()
            item.menus.add(menu)
            item.save()
            #check if category exists but menu didnt contain it
            if not menu_has_category(menu, item.category):
                add_existing_category(menu.restaurant, menu, item.category)
        else:
            item = MenuItemForm(request.POST).save(commit = False)
            item.restaurant = request.user.restaurant
            item.save()
            item.menus.add(Menu.objects.filter(id = menu_id).first())
            item.save()
            #check for new category
            if new_category(request, item.category):
                print('creating new category with name ', item.category)
                new_cat = SelectOption(name = item.category, restaurant = Restaurant.objects.filter(user = request.user).first(), menu=Menu.objects.filter(id = menu_id).first())
                new_cat.save()
            #check if they uploaded new photo
            photo = request.FILES.get('photo', False)
            if photo:
                # print('PHOTO HERE!!!! BADD')
                #save photo to AWS
                doc = request.FILES['photo'] #get file
                files_dir = '{user}/photos/i/{item_number}'.format(user = "R" + str(request.user.id),
                                                                            item_number = 'item'+str(item.id))
                file_storage = FileStorage()
                mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
                doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
                file_storage.save(doc_path, doc)
                item.photo_path = doc_path
                item.save()

        #redirect back to edit menu page
        return redirect('/restaurant_admin/edit_menu/{num}'.format(num = menu_id))


def remove_item(request, menu_id, origin, item_id):
    if origin == 'edit_menu': #delete request came from edit menu page
        if not validate_id_number(request, menu_id):
            return HttpResponse('you are not authorized to view this')
        curr_menu = Menu.objects.filter(id = menu_id).first()
        curr_item = MenuItem.objects.filter(id = item_id).first()
        #if the method is a get, then it sends them to a confirmation page making sure they want to delete the item
        if request.method == 'GET':
            items = MenuItem.objects.filter(menus = curr_menu) #query all the items, show the user so they know that they'll be deleted
            return render(request, 'restaurant/confirm_remove.html', {'menu':None, 'items': curr_item, 'url_id': curr_menu})
        #else delete the item
        else:
            curr_item.menus.remove(curr_menu)
            return redirect('/restaurant_admin/edit_menu/{menu}'.format(menu = menu_id))
    else: #delete request came from my_items page
        item = MenuItem.objects.get(id=item_id)
        item.delete()
        return redirect('/restaurant_admin/my_items')



def edit_item(request, item_id, origin, menu_id):
    if origin == 'edit_menu': #validate if request is coming from an edit_menu page
        if not validate_id_number(request, menu_id):
            return HttpResponse('you are not authorized to view this')
    print("origin")
    print(origin)
    item = MenuItem.objects.filter(id = item_id).first()
    #if method is get, then user is filling out form to change item
    if request.method == 'GET':
        return redirect('/restaruant_admin/edit_menu/{menu}'.format(menu=menu_id))
    else:
        item.name = request.POST['name']
        #check if they put anything for the description
        if request.POST['description'] != "":
            item.description = request.POST['description']
        #check if they put anything for category
        if request.POST['category'] != "":
            item.category = request.POST['category']
        item.price = request.POST['price']

        #code to update is_in_stock status
        if 'is_in_stock' in request.POST:
                item.is_in_stock = True
        else:
            item.is_in_stock = False
        item.save()

        #check if they uploaded new photo
        photo = request.FILES.get('photo', False)
        if photo:
            #save photo to AWS
            doc = request.FILES['photo'] #get file
            files_dir = '{user}/photos/i/{item_number}'.format(user = "R" + str(request.user.id),
                                                                        item_number = 'item'+str(item.id))
            file_storage = FileStorage()
            mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
            doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
            file_storage.save(doc_path, doc)
            item.photo_path = doc_path
            print(item.photo_path)
            item.save()

        #redirect depending on where the request came from
        if origin == 'edit_menu':
            return redirect('/restaurant_admin/edit_menu/' + str(menu_id))
        elif origin == 'my_items':
            return redirect('/restaurant_admin/my_items')


#helper function, removes a category from a menu if no items are associated with it
def check_category(category, rest, menu):
    q_set = MenuItem.objects.filter(restaurant = rest, menus = menu, category = category.name)
    print('Q_SET: ', q_set)
    if len(q_set) == 0:
        category.menus.remove(menu)
        category.save()

def ajax_edit_item(request):
    form = EditMenuItemForm(request.POST, request.FILES)
    print("request:")
    print(request.POST)
    #if form isnt valid we send the errors to the JS script in template
    if not form.is_valid():
        print("form was not valid. these are the errors")
        print(form.errors)

        return JsonResponse({
            'success': False,
            'err_code': 'invalid_form',
            'err_msg': form.errors,
        })

    #Actions if form is valid ...
    item = MenuItem.objects.get(id=request.POST['item_id'])
    old_category = SelectOption.objects.filter(name = item.category, restaurant = item.restaurant).first()
    #for every field that was filled in, we update the according attribute
    print('CATEGORY: ', request.POST['category'])
    if len(request.POST['name']) > 0:
        item.name = request.POST['name']
    if len(request.POST['category']) > 0:
        item.category = request.POST['category']
    if len(request.POST['description']) > 0:
        item.description = request.POST['description']
    if len(request.POST['price']) > 0:
        item.price = request.POST['price']
    if 'is_in_stock' in request.POST:
            item.is_in_stock = True
    else:
        item.is_in_stock = False
    item.save()
    photo = request.FILES.get('photo', False)
    if photo:
        #save photo to AWS
        doc = request.FILES['photo'] #get file
        files_dir = '{user}/photos/i/{item_number}'.format(user = "R" + str(request.user.id),
                                                                    item_number = 'item'+str(item.id))
        file_storage = FileStorage()
        mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
        doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
        file_storage.save(doc_path, doc)
        item.photo_path = doc_path

    if request.POST['origin'] == 'edit_menu':
        check_category(old_category, item.restaurant, Menu.objects.filter(id = request.POST['menu_id']).first())
        #check if category exists but menu didnt contain it
        if not menu_has_category(Menu.objects.filter(id = request.POST['menu_id']).first(), item.category):
            add_existing_category(Menu.objects.filter(id = request.POST['menu_id']).first().restaurant, Menu.objects.filter(id = request.POST['menu_id']).first(), item.category)

    if new_category(request, item.category):
        if request.POST['origin'] == 'my_items':
            new_cat = SelectOption(name = item.category, restaurant = Restaurant.objects.filter(user = request.user).first())
            new_cat.save()
        elif request.POST['origin'] == 'edit_menu':
            new_cat = SelectOption(name = item.category, restaurant = Restaurant.objects.filter(user = request.user).first())
            new_cat.save()
            new_cat.menus.add(Menu.objects.filter(id = request.POST['menu_id']).first())
            new_cat.save()

    #redirect back to edit menu page
    return JsonResponse({'success':True})
    print('redirecting')


def view_item(request, menu_id, item_id):
    if not validate_id_number(request, menu_id):
        return HttpResponse('you are not authorized to view this')
    if request.method == 'GET':
        curr_menu = Menu.objects.filter(id = menu_id).first()
        curr_rest = curr_menu.restaurant
        item = MenuItem.objects.filter(id = item_id).first()
        return render(request, 'restaurant/view_item.html', {'item': item, 'restaurant': curr_rest, 'menu': curr_menu})
    else:
        #if method is a post, then just redirect to this page as a get
        return redirect('/restaurant_admin/view_item/{m_id}/{i_id}'.format(m_id = menu_id, i_id = item_id))


"""this method is to create a new Cashier"""

def register_cashier(request):
    #if method is a post, then the user submitted a registration from
    if request.method == 'POST':
        # form = UserForm(request.POST)
        cashier_form = CashierForm(request.POST)
        if cashier_form.login_number(request.POST['login_number'], Restaurant.objects.filter(user = request.user).first().id):
            cashier = cashier_form.save(commit=False)
            cashier.restaurant = Restaurant.objects.filter(user = request.user).first()
            cashier.save()
            return redirect('/restaurant_admin/cashiers')
        context = {'form' : cashier_form, 'me': Restaurant.objects.filter(user = request.user).first(), 'cashiers': CashierProfile.objects.filter(restaurant = Restaurant.objects.filter(user = request.user).first())}
        return render(request, 'restaurant/cashiers.html', context)
    #if method is get, then user is filling out form
    else:
        form = CashierForm()
        cashiers = CashierProfile.objects.filter(restaurant = Restaurant.objects.filter(user = request.user).first())
        context = {'form' : form, 'me': Restaurant.objects.filter(user = request.user).first(), 'cashiers': cashiers}
        return render(request, 'restaurant/cashiers.html', context)



"""for seeing/changing kitchen login"""
def kitchen_no(request):
    #if method is a post, then the user submitted a registration from
    if request.method == 'POST':
        curr_rest = Restaurant.objects.filter(user = request.user).first()
        if Restaurant.objects.filter(kitchen_login_no = request.POST['login_no']).exists():
            messages.info(request, _('Login Not Available'))
        else:
            curr_rest.kitchen_login_no = request.POST['login_no']
            curr_rest.save()
        return redirect('/restaurant_admin/kitchen')
    #if method is get, then user is filling out form
    else:
        curr_rest = Restaurant.objects.filter(user = request.user).first()
        return render(request, 'restaurant/kitchen.html', {'restaurant':curr_rest})

def my_items(request):
    curr_rest = Restaurant.objects.get(user = request.user)
    url_parameter = request.GET.get("q") #this parameter is either NONE or a string which we will use to search MenuItem objects
    categories = MenuItem.objects.filter(restaurant=curr_rest).values_list('category', flat=True).distinct()
    category_items = {}
    if url_parameter:
        print("we here")
        for cat in categories:
            category_items[cat]  = MenuItem.objects.filter(restaurant=curr_rest).filter(category = cat).filter(name__icontains=url_parameter)
    else:
        for cat in categories:
            category_items[cat]  = MenuItem.objects.filter(restaurant=curr_rest).filter(category = cat)
    form = MenuItemForm()
    # edit_form = EditMenuItemForm()

    #get all possible categories of menu
    # print("categories length")
    # print(len(categories))
    # print(category_items)

    if request.is_ajax(): #this is for search
        print("ajax")
        html = render_to_string(
            template_name="restaurant/replaceable_content.html",
            context={"menus": [],'item_form':form,'me':curr_rest,'category_items':category_items}
        )

        data_dict = {"html_from_view": html}

        return JsonResponse(data=data_dict, safe=False)
    selct_options = SelectOption.objects.filter(restaurant = curr_rest)
    print(selct_options)

    # 'item_form': form
    # 'edit_form':edit_form
    # 'menus': []
    return render(request, 'restaurant/my_items.html', {'me': curr_rest,'category_items':category_items, 'selct_options':selct_options, 'item_form': form})

def add_item_no_menu(request):
    #if method is get, then user is filling out form for new item
    if request.method == 'GET':
        return redirect('/restaurant_admin/edit_menu/{menu}'.format(menu = menu_id))
    #otherwise the user created a new item, and it must be added to the menu
    else:
        item_form = MenuItemForm(request.POST)
        if form.is_valid():
            item.restaurant = request.user.restaurant

            photo = request.FILES.get('photo', False)
            if photo:
                #save photo to AWS
                doc = request.FILES['photo'] #get file
                files_dir = '{user}/photos/i/{item_number}'.format(user = "R" + str(request.user.id),
                                                                            item_number = 'item'+str(item.id))
                file_storage = FileStorage()
                mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
                doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
                file_storage.save(doc_path, doc)
                item.photo_path = doc_path
                item.save()

            #item.menu = None
            item.save()
            print('redirecting')
            #redirect back to edit menu page
            return redirect('/restaurant_admin/my_items')
        else:
            pass

#function that adds an existing category to a menu
def menu_has_category(menu, category):
    select_option_set = SelectOption.objects.filter(name = category)
    for option in select_option_set:
        if menu in option.menus.all():
            return True
    return False

#function that adds and existing category to a menu
def add_existing_category(rest, menu, category):
    option = SelectOption.objects.filter(restaurant = rest, name = category).first()
    option.menus.add(menu)
    option.save()

def ajax_add_item(request):
    curr_rest = request.user.restaurant
    form = MenuItemForm(request.POST, request.FILES)
    form.restaurant_id = curr_rest.id
    print("current")
    print(curr_rest.id)
    print("origin:")
    print(request.POST['origin'])
    #if form isnt valid we send the errors to the JS script in template
    if not form.is_valid():
        print("form was not valid. these are the errors")
        print(form.errors)

        return JsonResponse({
            'success': False,
            'err_code': 'invalid_form',
            'err_msg': form.errors,
        })

    #Actions if form is valid ...
    item = MenuItemForm(request.POST)
    item.restaurant_id = curr_rest.id
    item = item.save(commit = False)
    item.restaurant = curr_rest

    photo = request.FILES.get('photo', False)
    print("files")
    print(request.FILES)
    if photo:
        #save photo to AWS
        doc = request.FILES['photo'] #get file
        files_dir = '{user}/photos/i/{item_number}'.format(user = "R" + str(request.user.id),
                                                                    item_number = 'item'+str(item.id))
        file_storage = FileStorage()
        mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
        doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
        file_storage.save(doc_path, doc)
        item.photo_path = doc_path
        #item.save()

    item.save()
    if request.POST['origin'] == 'edit_menu': #if from edit menu page add to menu
        print("yp we here")
        menu = Menu.objects.get(id=request.POST['menu_id'])
        print(menu)
        item.menus.add(menu)
        #check if category existed but not in menu previously
        if not new_category(request, item.category) and not menu_has_category(menu, item.category):
            add_existing_category(curr_rest, menu, item.category)

    item.save()
    #check for new category
    if new_category(request, item.category):
        if request.POST['origin'] == 'my_items':
            new_cat = SelectOption(name = item.category, restaurant = curr_rest)
            new_cat.save()
        elif request.POST['origin'] == 'edit_menu':
            new_cat = SelectOption(name = item.category, restaurant = curr_rest)
            new_cat.save()
            new_cat.menus.add(Menu.objects.filter(id = request.POST['menu_id']).first())
            new_cat.save()


    elif request.POST['origin'] == 'edit_menu': #category was an existing one
        existing_cat = SelectOption.objects.filter(restaurant=curr_rest).filter(name=item.category).first()
        existing_cat.menus.add(Menu.objects.filter(id = request.POST['menu_id']).first())

    print("here")
    categories = MenuItem.objects.filter(restaurant=curr_rest).values_list('category', flat=True).distinct()
    category_items = {}
    for cat in categories:
        category_items[cat]  = MenuItem.objects.filter(restaurant=curr_rest).filter(category = cat)
    form = MenuItemForm()
    selct_options = SelectOption.objects.filter(restaurant = curr_rest)

    context = {'me': curr_rest,'category_items': category_items,'item_form': form,'selct_options':selct_options}
    # return redirect('/restaurant_admin/my_items').render()
    return render(request, 'restaurant/my_items.html', context)
    # return JsonResponse({'success':True})
    print('redirecting')
    #redirect back to edit menu page
    return redirect('/restaurant_admin/my_items')

def receipt_page(request):
    if request.method == 'GET':

        return render(request, 'restaurant/receipt.html')

    else:
        return redirect('restaurant/receipt.html')

queue = []
def ajax_receipt(request):
    ''' Two parts, one adds to the queue (the ones coming from order_confirmation)
        And the other dequeues (the one coming from receipt.html)'''

    if request.method == 'POST':
        cart_id = request.POST.get('cart_id', None)
        queue.append(cart_id)
        print(queue)
        receipt_html = request.POST.get('receipt_html', None)
        curr_cart = Cart.objects.filter(id = cart_id).first()
        curr_cart.receipt_html = receipt_html
        curr_cart.save()

        data = {
            'receipt_html': receipt_html,
            'cart_id': cart_id,
        }
        return JsonResponse(data)
    else:
        if queue:
            print('QUEUE pre-pop: ', queue)
            cart_id = queue.pop(0)
            print('QUEUE post-pop: ', queue)
            curr_cart = Cart.objects.filter(id = cart_id).first()
            receipt_html = curr_cart.receipt_html

            data = {
                'receipt_html': receipt_html,
            }
            return JsonResponse(data)
        else:
            data = {
                'receipt_html': None
            }
            return JsonResponse(data)


def create_addon_group(request, menu_id, item_id):
    if request.method == 'POST':
        group = AddOnGroup(name = request.POST['addon_group_name'])
        group.restaurant = Menu.objects.filter(id = menu_id).first().restaurant
        group.save()
        group.menu_items.add(MenuItem.objects.filter(id = item_id).first())
        group.save()
    return redirect('/restaurant_admin/edit_menu/{menu}'.format(menu = menu_id))


def create_addon_item(request, menu_id, group_id):
    if request.method == 'POST':
        curr_group = AddOnGroup.objects.filter(id = group_id).first()
        addon_item = AddOnItem(name = request.POST['addon_item_name'], price = request.POST['addon_item_price'])
        addon_item.group = curr_group
        addon_item.save()
    return redirect('/restaurant_admin/edit_menu/{menu}'.format(menu = menu_id))

def edit_addon_item(request, menu_id, addon_item_id):
    if request.method == 'POST':
        addon_item = AddOnItem.objects.filter(id = addon_item_id).first()
        addon_item.name = request.POST['addon_item_name']
        addon_item.price = request.POST['addon_item_price']
        addon_item.save()
    return redirect('/restaurant_admin/edit_menu/{menu}'.format(menu = menu_id))

def add_existing_addon_group(request, menu_id, item_id, addon_group_id):
    if request.method == 'POST':
        addon_group = AddOnGroup.objects.filter(id = addon_group_id).first()
        addon_group.menu_items.add(MenuItem.objects.filter(id = item_id).first())
        addon_group.save()
    return redirect('/restaurant_admin/edit_menu/{menu}'.format(menu = menu_id))

def sales(request):
    restaurant = Restaurant.objects.get(user = request.user)
    print("method is:")
    print(request.method)
    if request.method == "POST":
        print("here")
        form = DatesForm(request.POST)
        if form.is_valid():
            """This block of code gets data like the total sales, total cash/card sales etc."""
            cd = form.cleaned_data
            print(cd['start_date'] + cd['start_time'])
            start_datetime_str = datetime.strptime(cd['start_date'] + " " + cd['start_time'],
                                "%Y-%m-%d %I:00 %p")
            print(start_datetime_str)
            start_datetime_str = start_datetime_str.replace(tzinfo = timezone.utc)
            end_datetime_str = datetime.strptime(cd['end_date'] + cd['end_time'],
                                "%Y-%m-%d%I:00 %p")
            carts = Cart.objects.filter(restaurant=restaurant).filter(created_at__range=(start_datetime_str,end_datetime_str))
            total_sales = sum([cart.total for cart in carts])
            total_sales_with_tip = sum([cart.total_with_tip for cart in carts])
            total_tip = total_sales_with_tip - total_sales
            total_items = 0
            item_scores = {item : [0,0] for item in MenuItem.objects.filter(restaurant=restaurant)} #item : (sales,quantity)
            for cart in carts:
                print("total items:")
                print(total_items)
                cart_counters = MenuItemCounter.objects.filter(cart=cart)
                total_items += sum([counter.quantity for counter in cart_counters])
                for counter in cart_counters:
                    item_scores[counter.item][0] += counter.price
                    item_scores[counter.item][1] += counter.quantity
            top5_sales = sorted(item_scores.items(),key=lambda item: item[1][0], reverse=True)[:5]
            top5_sales = [(i+1,tup[0].name,tup[1][0]) for i,tup in enumerate(top5_sales)]
            top5_quantity = sorted(item_scores.items(),key=lambda item: item[1][1], reverse=True)[:5]
            top5_quantity = [(i+1,tup[0].name,tup[1][1]) for i,tup in enumerate(top5_quantity)]
            total_cash = sum([cart.total for cart in carts if cart.cash_code  != None])
            total_card = sum([cart.total for cart in carts if cart.cash_code == None])
            form = DatesForm()
            #hanlde division by zero for percentages
            if total_cash == 0:
                cash_percentage = 'N/A'
            else:
                cash_percentage = round(100*total_cash/total_sales,2)
            if total_card == 0:
                card_percentage = 'N/A'
            else:
                card_percentage = round(100*total_card/total_sales,2)
            if total_tip == 0:
                tip_percentage = 'N/A'
            else:
                tip_percentage = round(100*total_tip/total_sales,2)
            """This block ranks items by sales/quantity sold"""

            context = {'form':form, 'total_cash':total_cash, 'total_sales':total_sales, 'total_card':total_card,
                        'cash_percentage':cash_percentage, 'card_percentage': card_percentage,
                        'total_items': total_items, 'total_tip':total_tip,
                        'tip_percentage': tip_percentage,'period_start':start_datetime_str,'period_end':end_datetime_str,
                        'top5_sales':top5_sales,'top5_quantity':top5_quantity}
            return render(request, 'restaurant/sales_extended.html',context)


    restaurant = Restaurant.objects.get(user = request.user)
    form = DatesForm
    context = {'form':form}
    return render(request,'restaurant/sales.html',context)
