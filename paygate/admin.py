from django.contrib import admin

from .models import Order, Package


class OrderAdmin(admin.ModelAdmin):
    list_display = ('profile_name', 'order_id', 'dm_amount', 'status', 'created',)

admin.site.register(Order, OrderAdmin)
admin.site.register(Package)