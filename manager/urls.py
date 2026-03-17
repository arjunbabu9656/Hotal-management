from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Menu CRUD
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/add/', views.food_item_add, name='food_item_add'),
    path('menu/edit/<int:pk>/', views.food_item_edit, name='food_item_edit'),
    path('menu/delete/<int:pk>/', views.food_item_delete, name='food_item_delete'),
    
    # Category CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_add, name='staff_add'),
    path('staff/edit/<int:pk>/', views.staff_edit, name='staff_edit'),
    path('staff/delete/<int:pk>/', views.staff_delete, name='staff_delete'),
    path('users/', views.user_list, name='user_list'),
    path('reports/', views.reports, name='reports'),
    path('archive/', views.order_archive, name='order_archive'),
    path('reset-day/', views.reset_daily_orders, name='reset_daily_orders'),
]
