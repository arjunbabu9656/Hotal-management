from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('dish/<int:pk>/', views.dish_detail, name='dish_detail'),
]
