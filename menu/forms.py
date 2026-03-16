from django import forms
from .models import Category, FoodItem

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = [
            'category', 'name', 'description', 'price', 
            'image', 'is_available', 'preparation_time', 
            'ingredients', 'allergens'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients': forms.Textarea(attrs={'rows': 3}),
        }
