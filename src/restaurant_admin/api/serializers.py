from rest_framework import serializers
from restaurant_admin.models import MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('name','category','description','price','photo_path')
