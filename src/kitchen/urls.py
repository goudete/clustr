from django.urls import path
from . import views

urlpatterns = [
    path('', views.kitchen_login),
    path('<int:restaurant_id>', views.see_orders),
    path('<int:restaurant_id>/<int:tracker_id>', views.mark_order_done),
    path('ajax/check_new_orders', views.check_new_orders, name = "check_new_orders")
]
