from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'room_number', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'room_number')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'food_item', 'quantity')
    list_filter = ('order__status',)
