from django.urls import path

from .views import (
    MenuItemListView,
    MenuItemDetailView,
)

urlpatterns = [
    path('', MenuItemListView.as_view()),
    path('<pk>', MenuItemDetailView.as_view()),
    # path('<pk>/update/', ArticleUpdateView.as_view()),
    # path('<pk>/delete/', ArticleDeleteView.as_view())
]
