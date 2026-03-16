from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, FoodItem

def menu_list(request):
    categories = Category.objects.filter(is_active=True)
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    
    food_items = FoodItem.objects.filter(is_available=True)
    
    if query:
        food_items = food_items.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    if category_id:
        food_items = food_items.filter(category_id=category_id)
        
    context = {
        'categories': categories,
        'food_items': food_items,
        'current_category': int(category_id) if category_id else None,
        'query': query,
    }
    return render(request, 'menu/menu_list.html', context)

def dish_detail(request, pk):
    food_item = get_object_or_404(FoodItem, pk=pk)
    context = {
        'item': food_item
    }
    return render(request, 'menu/dish_detail.html', context)
