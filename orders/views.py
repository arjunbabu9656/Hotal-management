from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from menu.models import FoodItem
from .models import Order, OrderItem, OrderMessage
from .cart import Cart
from accounts.decorators import role_required
from django.contrib.auth.models import User
from django.db.models import Count, Q

def assign_order_to_role(order, role):
    """
    Assigns an order to the staff member of a specific role with the least active orders.
    """
    staff_member = User.objects.filter(
        profile__role='staff', 
        profile__staff_role=role,
        is_active=True
    ).annotate(
        active_orders_count=Count('assigned_orders', filter=~Q(assigned_orders__status__in=['delivered', 'cancelled']))
    ).order_by('active_orders_count').first()
    
    # FALLBACK: If no one with the specific role is found, pick ANY active staff with role='staff'
    if not staff_member:
        staff_member = User.objects.filter(
            profile__role='staff',
            is_active=True
        ).annotate(
            active_orders_count=Count('assigned_orders', filter=~Q(assigned_orders__status__in=['delivered', 'cancelled']))
        ).order_by('active_orders_count').first()
    
    if staff_member:
        order.assigned_to = staff_member
        order.save()
        return True
    return False

@require_POST
def cart_add(request, food_item_id):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.urls import reverse
            return JsonResponse({'redirect': reverse('accounts:register'), 'message': 'Please signup to order food.'}, status=401)
        messages.info(request, "Please signup to order food.")
        return redirect('accounts:register')
        
    cart = Cart(request)
    food_item = get_object_or_404(FoodItem, id=food_item_id)
    quantity = int(request.POST.get('quantity', 1))
    instructions = request.POST.get('instructions', '')
    cart.add(food_item=food_item, quantity=quantity, instructions=instructions)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': len(cart), 'item_name': food_item.name})

    messages.success(request, f"Added {food_item.name} to cart.")
    return redirect('menu:menu_list')

def cart_remove(request, food_item_id):
    cart = Cart(request)
    food_item = get_object_or_404(FoodItem, id=food_item_id)
    cart.remove(food_item)
    messages.info(request, f"Removed {food_item.name} from cart.")
    return redirect('orders:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})

@role_required(allowed_roles=['customer', 'staff', 'manager', 'owner'])
def checkout(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please signup to place your order.")
        return redirect('accounts:register')
    cart = Cart(request)
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('menu:menu_list')
    
    if request.method == 'POST':
        order_type = request.POST.get('order_type', 'delivery')
        payment_method = request.POST.get('payment_method', 'cash')
        room_number = request.POST.get('room_number')
        special_note = request.POST.get('special_note')
        
        if order_type == 'delivery' and not room_number:
            messages.error(request, "Room number is required for room delivery.")
            return redirect('orders:cart_detail')
        
        order = Order.objects.create(
            customer=request.user,
            room_number=room_number if order_type == 'delivery' else None,
            order_type=order_type,
            payment_method=payment_method,
            special_note=special_note,
            total_price=cart.get_total_price(),
        )
        # Initial assignment to computer staff
        assign_order_to_role(order, 'computer')
        
        for item in cart:
            OrderItem.objects.create(
                order=order,
                food_item=item['food_item'],
                quantity=item['quantity'],
                instructions=item['instructions']
            )
        
        cart.clear()
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('orders:order_detail', order_id=order.id)
    
    return render(request, 'orders/cart.html', {'cart': cart})

@login_required
@role_required(allowed_roles=['customer', 'staff', 'manager', 'owner'])
def order_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
@role_required(allowed_roles=['customer', 'staff', 'manager', 'owner'])
def order_detail(request, order_id):
    if request.user.profile.role in ['staff', 'manager', 'owner']:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
@role_required(allowed_roles=['customer'])
def submit_feedback(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        if order.status == 'delivered':
            rating = request.POST.get('rating')
            feedback = request.POST.get('feedback')
            if rating:
                order.rating = int(rating)
                order.feedback = feedback
                order.save()
                messages.success(request, "Thank you for your feedback!")
        return redirect('orders:order_detail', order_id=order_id)
    return redirect('orders:order_list')

@login_required
@role_required(allowed_roles=['customer', 'staff', 'manager', 'owner'])
@require_POST
def cancel_order(request, order_id):
    # If admin role, can cancel any order. If customer, only their own.
    if request.user.profile.role in ['manager', 'owner']:
        order = get_object_or_404(Order, id=order_id)
        order.status = 'cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled by Owner.")
    else:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            messages.success(request, f"Order #{order.id} has been cancelled.")
        else:
            messages.error(request, "Only pending orders can be cancelled.")
    
    if request.user.profile.role in ['manager', 'owner']:
        return redirect('manager:order_list')
    return redirect('orders:order_list')

