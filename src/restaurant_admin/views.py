from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .forms import UserForm, RestaurantForm
from django.contrib import messages
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
    return HttpResponse('MENUS GO HERE')

def add_menu(request):
    return HttpResponse('filler')

def view_menu(request):
    return HttpResponse('filler')

def edit_menu(request):
    return HttpResponse('filler')

def add_item(request):
    return HttpResponse('filler')

def remove_item(request):
    return HttpResponse('filler')
