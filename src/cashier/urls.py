"""qr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('base/<int:log_no>',views.baseView),
    path('cash_payment/<int:log_no>',views.cashPaymentView, name = 'cash_payment'),
    path('review_order/<int:log_no>',views.reviewOrderView, name = 'review_order'),
    path('cashier_login/<int:rest_id>',views.loginCashier, name = 'cashier_login'),
    path('order_history/<int:log_no>',views.orderHistoryView, name = 'order_history'),
    path('ajax/ajax_change_order_quantity/<int:log_no>', views.ajax_change_order_quantity, name = 'change_order_quantity'),
    path('ajax/ajax_add_item/<int:log_no>',views.ajax_add_item, name = 'add_item'),
    path('logout/<int:log_no>', views.cashier_logout, name='logout'),
    path('receipt', TemplateView.as_view(template_name="emails/receipt/receipt.html")),
]
