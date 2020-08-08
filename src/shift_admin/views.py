from django.shortcuts import render, redirect
from restaurant_admin.models import Restaurant
from customers.models import Cart
from datetime import date
# Create your views here.

def is_correct(request):
    if request.method != 'POST':
        return False
    passw = request.POST['pass']
    bald = request.POST['bald']
    mari = request.POST['maricon']
    goon = request.POST['goon']
    cool = request.POST['cool']

    if passw != 'OneB33R@ndB00m!0unce0fc0caine' or bald != 'Mook':
        return False
    elif mari != 'Kike' or goon != 'Luisillo':
        return False
    elif cool != 'Rowan':
        return False
    else:
        return True

def login_admin(request):
    if request.method == 'GET':
        return render(request, 'shift_admin/login.html')
    else:
        if is_correct(request):
            return redirect('/shift_admin/home/11168/41816')
        return redirect('/shift_admin')

def logout_admin(request):
    return redirect('/shift_admin')


"""this is the main method
it displays:
1) how many restaurants we have
    -> how much these restaurants are selling
    -> how many users they've accumulated
    -> how many users they've acumulated today
2) total sales
3) total users"""
def home_page(request, bday, vir):
    if not val_nums(bday, vir):
        return redirect('/shift_admin')
    elif request.method == 'POST':
        return redirect('/shift_admin')
    else:
        #get the restaurant, list dict
        dict = get_res_list_dict()
        #get the total sales
        sales = get_amt(dict, 0)
        #get total users
        users = get_amt(dict, 2) + len(dict)
        return render(request, 'shift_admin/home.html', {'dict': dict, 'sales': sales, 'users': users})

def val_nums(b, v):
    if b != 11168 or v != 41816:
        return False
    return True

#helper method, returns a dictionary w structure {restaurant: [total sales, sales today, total customers, customers today]}
def get_res_list_dict():
    ans = {}
    rests = Restaurant.objects.all()
    for rest in rests:
        ans[rest] = [sum_sales(rest), sales_today(rest), sum_customers(rest), customers_today(rest)]
    return ans

def sum_sales(rest):
    sum = 0
    for cart in Cart.objects.filter(restaurant = rest).filter(is_paid = True):
        sum += cart.total_with_tip
    return sum

def sales_today(rest):
    sum = 0
    for cart in Cart.objects.filter(restaurant = rest).filter(is_paid = True).filter(paid_at__date = date.today()):
        sum += cart.total_with_tip
    return sum

def sum_customers(rest):
    return len(Cart.objects.filter(restaurant = rest))

def customers_today(rest):
    return len(Cart.objects.filter(restaurant = rest).filter(created_at__date = date.today()))

def get_amt(dict, idx):
    ans = 0
    for key in dict.keys():
        ans += dict[key][idx]
    return ans
