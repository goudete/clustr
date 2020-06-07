from django.urls import path
from . import views

urlpatterns = [
    path('', views.kitchen_login),
    path('<int:restaurant_id>', views.see_orders),
    path('<int:restaurant_id>/<int:tracker_id>', views.mark_order_done)
]
