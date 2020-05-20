from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view),
    path('logout', views.logout_view),
    path('register', views.register_view),
    path('my_menus', views.my_menus),
    path('add_menu', views.add_menu),
    path('view_menu', views.view_menu),
    path('edit_menu', views.edit_menu),
    path('add_item', views.add_item),
    path('remove_item', views.remove_item),
]
