from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_cart),
    # path('view_menu/<int:cart_id>/<int:restaurant_id>/<int:menu_id>', views.view_menu),
    path('view_menu/<int:restaurant_id>/<int:menu_id>', views.view_menu),
    path('view_item', views.view_item),
    path('view_cart', views.view_cart),
    path('payment', views.payment),
    path('order_confirmation', views.order_confirmation),

]
