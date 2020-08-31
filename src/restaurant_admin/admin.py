from django.contrib import admin
from .models import Restaurant, Menu, MenuItem, SelectOption, AddOnGroup, AddOnItem, ShippingZone

# Register your models here.
admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(SelectOption)
admin.site.register(AddOnGroup)
admin.site.register(AddOnItem)
admin.site.register(ShippingZone)

class MenuItemAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(MenuItem, MenuItemAdmin)
