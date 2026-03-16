from django.contrib import admin
from .models import Category, FoodItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'preparation_time')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
