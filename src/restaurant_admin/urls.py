from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view),
    path('logout', views.logout_view),
    path('register', views.register_view),
    path('my_menus', views.my_menus),
    path('kitchen', views.kitchen_no),
    path('cashiers', views.register_cashier),
    path('connect', views.stripe_connect),
    path('answer_question', views.payment_question),
    path('answer_about', views.answer_about),
    path('add_menu', views.add_menu),
    path('view_menu/<int:menu_id>', views.view_menu),
    path('edit_menu/<int:menu_id>', views.edit_menu),
    path('remove_menu/<int:menu_id>', views.remove_menu),
    path('add_item/<int:menu_id>', views.add_item),
    path('remove_item/<int:menu_id>/<int:item_id>', views.remove_item),
    path('view_item/<int:menu_id>/<int:item_id>', views.view_item),
    path('edit_item/<int:menu_id>/<int:item_id>', views.edit_item),
    path('my_items',views.my_items),
    path('add_item_no_menu', views.add_item_no_menu),
]
