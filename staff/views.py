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
    # Focus strictly on Guest orders for maximum kitchen efficiency
    orders = Order.objects.filter(
        status__in=['pending', 'preparing', 'ready', 'delivering'], 
        is_archived=False
    ).order_by('created_at')
    
    return render(request, 'staff/dashboard.html', {
        'orders': orders,
    })

@login_required
@role_required(allowed_roles=['staff', 'owner'])
def take_order(request, order_id):
    from django.contrib import messages
    order = get_object_or_404(Order, id=order_id, is_archived=False)
    
    if not order.assigned_to:
        order.assigned_to = request.user
        # When taken, auto-move to preparing if it was pending
        if order.status == 'pending':
            order.status = 'preparing'
        order.save()
        messages.success(request, f"Order #{order.id} successfully taken by you!")
    else:
        messages.error(request, f"This order was already taken by {order.assigned_to.username}.")
        
    return redirect('staff:dashboard')

@login_required
@role_required(allowed_roles=['staff', 'owner'])
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
