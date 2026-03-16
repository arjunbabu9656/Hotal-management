from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('order/<int:order_id>/status/<str:new_status>/', views.update_order_status, name='update_status'),
    path('menu-availability/', views.menu_availability, name='menu_availability'),
    path('menu-availability/toggle/<int:item_id>/', views.toggle_availability, name='toggle_availability'),
]
