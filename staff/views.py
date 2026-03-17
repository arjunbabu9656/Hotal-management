from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from accounts.decorators import role_required, owner_required
from orders.models import Order, OrderMessage
from menu.models import FoodItem, Category
from orders.views import assign_order_to_role

@login_required
@role_required(allowed_roles=['staff', 'owner'])
def dashboard(request):
    # ONLY see orders strictly assigned to the user, and EXCLUDE orders placed by managers
    active_orders = Order.objects.filter(
        status__in=['pending', 'preparing', 'ready', 'delivering'], 
        is_archived=False
    ).order_by('created_at')
    
    return render(request, 'staff/dashboard.html', {
        'orders': active_orders,
    })

@login_required
@owner_required
def update_order_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id)
    
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        if new_status in ['preparing', 'delivering', 'delivered']:
            order.processed_by = request.user
        
        # HANDOVER LOGIC: Pass the order to the next role
        if new_status == 'preparing':
            # Pass to a Cooker
            assign_order_to_role(order, 'cooker')
            
            # AUTOMATED MESSAGE: Notify Guest
            OrderMessage.objects.create(
                order=order,
                sender=request.user,
                content="Your order has been confirmed and is now being prepared! 🍳",
                is_staff_message=True
            )
        elif new_status == 'ready' and order.order_type == 'delivery':
            # Pass to a Delivery Boy
            assign_order_to_role(order, 'delivery')
        
        order.save()
        return JsonResponse({'success': True, 'status': order.get_status_display()})
    return JsonResponse({'success': False}, status=400)

@login_required
@role_required(allowed_roles=['staff', 'owner'])
def menu_availability(request):
    categories = Category.objects.filter(is_active=True).prefetch_related('items')
    return render(request, 'staff/menu_availability.html', {'categories': categories})

@login_required
@owner_required
def toggle_availability(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    item.is_available = not item.is_available
    item.save()
    return JsonResponse({'success': True, 'is_available': item.is_available})
