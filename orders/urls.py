from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:food_item_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:food_item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/message/', views.send_order_message, name='send_order_message'),
    path('order/<int:order_id>/feedback/', views.submit_feedback, name='submit_feedback'),
]
