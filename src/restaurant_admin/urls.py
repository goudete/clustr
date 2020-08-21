from django.urls import path
from . import views
from django.views.i18n import JavaScriptCatalog
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path('', views.login_view, name = 'login'),
    path('logout', views.logout_view),
    path('register', views.register_view, name = 'register'),
    path('my_menus', views.my_menus),
    path('kitchen', views.kitchen_no),
    path('cashiers', views.register_cashier),
    path('connect', views.stripe_connect),
    path('answer_question', views.payment_question, name = 'answer_question'),
    path('toggle_payments', views.toggle_payments),
    path('answer_about', views.answer_about),
    path('add_menu', views.add_menu, name = 'add_menu'),
    path('view_menu/<int:menu_id>', views.view_menu),
    path('edit_menu/<int:menu_id>', views.edit_menu),
    path('remove_menu/<int:menu_id>', views.remove_menu, name = 'remove_menu'),
    path('add_item/<int:menu_id>', views.add_item),
    path('remove_item/<int:menu_id>/<str:origin>/<int:item_id>', views.remove_item),
    path('view_item/<int:menu_id>/<int:item_id>', views.view_item),
    path('edit_item/<int:item_id>/<str:origin>/<int:menu_id>', views.edit_item),
    path('my_items',views.my_items, name = 'my_items'),
    path('add_item_no_menu', views.add_item_no_menu),
    path('receipt_page', views.receipt_page, name = 'receipt_page'),
    path('create_addon_group/<int:menu_id>/<int:item_id>', views.create_addon_group),
    path('create_addon_item/<int:menu_id>/<int:group_id>', views.create_addon_item),
    path('edit_addon_item/<int:menu_id>/<int:addon_item_id>', views.edit_addon_item),
    path('add_existing_group/<int:menu_id>/<int:item_id>/<int:addon_group_id>', views.add_existing_addon_group),
    path('sales', views.sales, name = 'sales'),
    path('ajax/ajax_add_item',views.ajax_add_item, name="ajax_add_item"),
    path('ajax/ajax_edit_item',views.ajax_edit_item, name="ajax_edit_item"),
    path('set_language/<str:language>', views.set_language),
    path('toggle_menu_display_status/<int:menu_id>', views.toggle_menu_display_status),
    path('ajax/ajax_remove_addon/<int:add_on_id>', views.ajax_remove_addon, name ="ajax_remove_addon"),
    path('ajax/ajax_remove_addon_group/<int:addon_group_id>/<int:item_id>', views.ajax_remove_addon_group, name ="ajax_remove_addon_group"),
    path('ajax/ajax_add_addon/<str:name>/<str:price>/<int:group_id>', views.ajax_add_addon, name ="ajax_add_addon"),
    path('set_addon_groups/<int:item_id>', views.set_addon_groups, name = 'set_addon_group'),
    path('ajax/ajax_create_addon_group/<str:group_name>/<int:item_id>', views.ajax_create_addon_group, name ="ajax_create_addon_group"),
]
