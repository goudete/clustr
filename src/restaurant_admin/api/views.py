from rest_framework.generics import ListAPIView, RetrieveAPIView
from restaurant_admin.models import MenuItem
from .serializers import MenuItemSerializer

class MenuItemListView(ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class MenuItemDetailView(RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
