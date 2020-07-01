from django.urls import path
from . import views
from restaurant_admin.views import ajax_receipt, receipt_page

urlpatterns = [
    path('', views.show_all_menus), #this one is for showing all menus in your db
    path('<int:restaurant_id>/<int:menu_id>', views.create_cart),
    path('view_menu/<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.view_menu),
    path('about/<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.about_page),
    path('view_item/<int:cart_id>/<int:restaurant_id>/<int:menu_id>/<int:item_id>', views.view_item),
    path('add_item/<int:cart_id>/<int:restaurant_id>/<int:menu_id>/<int:item_id>', views.add_item), #for adding item to cart
    path('remove_item/<int:cart_id>/<int:restaurant_id>/<int:menu_id>/<int:item_id>', views.remove_item), #for removing item from cart
    path('view_cart/<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.view_cart),
    # path('decrease_quantity<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.decrease_quantity),
    path('change_instructions/<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.change_instructions),
    path('payment/<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.payment),
    path('order_confirmation/<int:cart_id>', views.order_confirmation),
    path('calculate_tip/<int:cart_id>/<int:restaurant_id>/<int:menu_id>/<int:tip>', views.calculate_tip),
    path('card_email_receipt/<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.card_email_receipt),
    path('cash_email_receipt/<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.cash_email_receipt),
    path('cash_code/<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.cash_payment_code),
    path('feedback/<int:cart_id>', views.feedback),
    path('ajax/ajax_increase_quantity', views.ajax_increase_quantity, name='increase_quantity'),
    path('ajax/ajax_decrease_quantity', views.ajax_decrease_quantity, name='decrease_quantity'),
    path('ajax/ajax_confirm_cash_payment', views.ajax_confirm_cash_payment, name='confirm_cash_payment'),
    path('ajax/ajax_receipt', ajax_receipt, name = 'ajax_receipt'),
    path('ajax/receipt_page', receipt_page, name = 'receipt_page'),
    path('ajax/dine_in_option', views.dine_in_option, name = 'dine_in_option'),
]
