from django.urls import path
from . import views

urlpatterns = [
    path('<int:rest_id>', views.kitchen_login),
    path('see_orders/<int:restaurant_id>', views.see_orders),
    path('<int:restaurant_id>/<int:tracker_id>', views.mark_order_done),
    path('ajax/check_new_orders', views.check_new_orders, name = "check_new_orders")
]
