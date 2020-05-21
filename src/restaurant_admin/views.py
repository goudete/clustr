from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .forms import UserForm, RestaurantForm, MenuForm, MenuItemForm
from django.conf import settings
from django.contrib import messages
from .models import Restaurant, Menu, MenuItem
from urllib.parse import urljoin
import boto3
import magic
from .file_storage import FileStorage
from django.core.files import File
import os
#  your views here.

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

def my_menus(request):
    menus = Menu.objects.filter(restaurant = Restaurant.objects.get(user = request.user)) #query set of all menus belonging to this restaurant
    return render(request, 'restaurant/my_menus.html', {'menus': menus})

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
            files_dir = '{user}/photos/{menu_num}/'.format(user = "R" + str(request.user.id), menu_num = 'menu'+str(new_menu.id))
            file_storage = FileStorage()
            mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
            doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
            file_storage.save(doc_path, doc)
            new_menu.photo_path = doc_path
            new_menu.save()
        #if they didnt upload a file
        elif menu.is_valid():
            new_menu = menu.save()
        #redirect to the edit menu so they can add new stuff to it
        return redirect('{menu}/edit_menu'.format(menu = new_menu.id))

def view_menu(request):
    return HttpResponse('filler')

def remove_menu(request, menu_id):
    curr_menu = Menu.objects.filter(id = menu_id).first()
    #if the method is a get, then it sends them to a confirmation page making sure they want to delete the menu
    if request.method == 'GET':
        items = MenuItem.objects.filter(menu = curr_menu) #query all the items, show the user so they know that they'll be deleted
        return render(request, 'restaurant/confirm_remove.html', {'menu':curr_menu, 'items': items})
    #else delete the menu
    else:
        curr_menu.delete()
        return redirect('/restaurant_admin/my_menus')


def edit_menu(request, menu_id):
    curr_menu = Menu.objects.filter(id = menu_id).first()
    #check if they uploaded new photo
    photo = request.FILES.get('photo', False)
    if photo:
        #save photo to AWS
        doc = request.FILES['photo'] #get file
        files_dir = '{user}/photos/{menu_num}/'.format(user = "R" + str(request.user.id), menu_num = 'menu'+str(menu_id))
        file_storage = FileStorage()
        mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
        doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
        file_storage.save(doc_path, doc)
        curr_menu.photo_path = doc_path
    #if method is a get, then the user is looking at the menu
    if request.method == 'GET':
        items = MenuItem.objects.filter(menu = curr_menu)
        return render(request, 'restaurant/edit_menu.html', {'menu': curr_menu, 'items': items})
    else:
        curr_menu.name = request.POST['name']
        curr_menu.save()
        return redirect('/restaurant_admin/{num}/edit_menu'.format(num = menu_id)) #redirect back to the same page


def add_item(request, menu_id):
    #if method is get, then user is filling out form for new item
    if request.method == 'GET':
        form = MenuItemForm()
        return render(request, 'restaurant/add_item.html', {'form': form, 'id': menu_id}) #add menu_id for the canel button
    #otherwise the user created a new item, and it must be added to the menu
    else:
        item = MenuItemForm(request.POST).save(commit = False)
        item.menu = Menu.objects.filter(id = menu_id).first()
        item.save()
        #check if they uploaded new photo
        photo = request.FILES.get('photo', False)
        if photo:
            #save photo to AWS
            doc = request.FILES['photo'] #get file
            files_dir = '{user}/photos/{menu_num}/{item_number}'.format(user = "R" + str(request.user.id),
                                                                        menu_num = 'menu'+str(menu_id),
                                                                        item_number = 'item'+str(item.id))
            file_storage = FileStorage()
            mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
            doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
            file_storage.save(doc_path, doc)
            item.photo_path = doc_path
            item.save()
        #redirect back to edit menu page
        return redirect('/restaurant_admin/{num}/edit_menu'.format(num = menu_id))

def remove_item(request, menu_id, item_id):
    curr_menu = Menu.objects.filter(id = menu_id).first()
    curr_item = MenuItem.objects.filter(id = item_id).first()
    #if the method is a get, then it sends them to a confirmation page making sure they want to delete the item
    if request.method == 'GET':
        items = MenuItem.objects.filter(menu = curr_menu) #query all the items, show the user so they know that they'll be deleted
        return render(request, 'restaurant/confirm_remove.html', {'menu':None, 'items': curr_item})
    #else delete the item
    else:
        curr_item.delete()
        return redirect('/restaurant_admin/{menu}/edit_menu'.format(menu = menu_id))

def edit_item(request, menu_id, item_id):
    item = MenuItem.objects.filter(id = item_id).first()
    #if method is get, then user is filling out form to change item
    if request.method == 'GET':
        return render(request, 'restaurant/edit_item.html', {'item': item})
    else:
        item.name = request.POST['name']
        item.description = request.POST['description']
        item.course = request.POST['course']
        item.price = request.POST['price']
        item.save()
        #check if they uploaded new photo
        photo = request.FILES.get('photo', False)
        if photo:
            #save photo to AWS
            doc = request.FILES['photo'] #get file
            files_dir = '{user}/photos/{menu_num}/{item_number}'.format(user = "R" + str(request.user.id),
                                                                        menu_num = 'menu'+str(menu_id),
                                                                        item_number = 'item'+str(item.id))
            file_storage = FileStorage()
            mime = magic.from_buffer(doc.read(), mime=True).split("/")[1]
            doc_path = os.path.join(files_dir, "photo."+mime) #set path for file to be stored in
            file_storage.save(doc_path, doc)
            item.photo_path = doc_path
            print(item.photo_path)
            item.save()
        #redirect
        return redirect('/restaurant_admin/{menu}/edit_menu'.format(menu = menu_id))

def view_item(request):
    return HttpResponse('filler')
