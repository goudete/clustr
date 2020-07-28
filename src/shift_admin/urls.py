from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_admin),
    path('logout', views.logout_admin),
    path('home/<int:bday>/<int:vir>', views.home_page),
]
