from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu),
    path('view_item', views.view_item),
    path('view_cart', views.view_cart),
    path('payment', views.payment),
    path('order_confirmation', views.order_confirmation),

]
