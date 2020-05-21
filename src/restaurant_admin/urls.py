from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view),
    path('logout', views.logout_view),
    path('register', views.register_view),
    path('my_menus', views.my_menus),
    path('add_menu', views.add_menu),
    path('<int:menu_id>/view_menu', views.view_menu),
    path('<int:menu_id>/edit_menu', views.edit_menu),
    path('<int:menu_id>/remove_menu', views.remove_menu),
    path('<int:menu_id>/add_item', views.add_item),
    path('<int:menu_id>/<int:item_id>/remove_item', views.remove_item),
    path('<int:menu_id>/<int:item_id>/view_item', views.view_item),
    path('<int:menu_id>/<int:item_id>/edit_item', views.edit_item),
]
