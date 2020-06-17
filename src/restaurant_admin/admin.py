from django.contrib import admin
from .models import Restaurant, Menu, MenuItem, SelectOption

# Register your models here.
admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(SelectOption)

class MenuItemAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(MenuItem, MenuItemAdmin)
