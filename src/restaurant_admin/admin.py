from django.contrib import admin
from .models import Restaurant, Menu, MenuItem

# Register your models here.
admin.site.register(Restaurant)
admin.site.register(Menu)

class MenuItemAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(MenuItem, MenuItemAdmin)
