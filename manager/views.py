from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.contrib import messages
from accounts.decorators import role_required, owner_required
from orders.models import Order, OrderItem
from menu.models import FoodItem, Category
from menu.forms import FoodItemForm, CategoryForm
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
import datetime

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def dashboard(request):
    today = timezone.now().date()
    today_orders = Order.objects.filter(created_at__date=today, is_archived=False)
    
    total_orders_today = today_orders.count()
    revenue_today = today_orders.exclude(status='cancelled').aggregate(Sum('total_price'))['total_price__sum'] or 0
    pending_orders_count = Order.objects.filter(status='pending', is_archived=False).count()
    cancelled_today = today_orders.filter(status='cancelled').count()
    
    # Monthly Revenue calculation (including archived orders)
    first_day_of_month = today.replace(day=1)
    monthly_orders = Order.objects.filter(
        created_at__date__gte=first_day_of_month,
        created_at__date__lte=today
    ).exclude(status='cancelled')
    revenue_month = monthly_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Status breakdown
    status_counts = Order.objects.filter(created_at__date=today, is_archived=False).values('status').annotate(total=Count('status'))
    
    # Top 5 items
    top_items = OrderItem.objects.all().values('food_item__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:5]
    
    recent_orders = Order.objects.filter(is_archived=False).order_by('-created_at')[:10]
    
    context = {
        'total_orders_today': total_orders_today,
        'revenue_today': revenue_today,
        'revenue_month': revenue_month,
        'pending_orders_count': pending_orders_count,
        'cancelled_today': cancelled_today,
        'status_counts': status_counts,
        'top_items': top_items,
        'recent_orders': recent_orders,
    }
    return render(request, 'manager/dashboard.html', context)

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def order_list(request):
    query = request.GET.get('q')
    orders = Order.objects.all().select_related('customer').order_by('-created_at')
    
    if query:
        orders = orders.filter(
            Q(id__icontains=query) | 
            Q(customer__username__icontains=query) | 
            Q(room_number__icontains=query) |
            Q(status__icontains=query)
        )
        
    return render(request, 'manager/orders.html', {'orders': orders, 'query': query})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'manager/order_detail.html', {'order': order})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def menu_list(request):
    query = request.GET.get('q')
    items = FoodItem.objects.all().select_related('category').order_by('category')
    
    if query:
        items = items.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        
    categories = Category.objects.all()
    return render(request, 'manager/menu.html', {'items': items, 'categories': categories, 'query': query})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def food_item_add(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Food item added successfully.")
            return redirect('manager:menu_list')
    else:
        form = FoodItemForm()
    return render(request, 'manager/menu_form.html', {'form': form, 'title': 'Add Food Item'})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def food_item_edit(request, pk):
    item = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"{item.name} updated successfully.")
            return redirect('manager:menu_list')
    else:
        form = FoodItemForm(instance=item)
    return render(request, 'manager/menu_form.html', {'form': form, 'item': item, 'title': 'Edit Food Item'})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def food_item_delete(request, pk):
    item = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Food item deleted.")
        return redirect('manager:menu_list')
    return render(request, 'manager/confirm_delete.html', {'item': item, 'type': 'Food Item'})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'manager/category_list.html', {'categories': categories})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect('manager:category_list')
    else:
        form = CategoryForm()
    return render(request, 'manager/menu_form.html', {'form': form, 'title': 'Add Category'})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"{category.name} updated successfully.")
            return redirect('manager:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'manager/menu_form.html', {'form': form, 'title': 'Edit Category'})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f"{category.name} deleted.")
        return redirect('manager:category_list')
    return render(request, 'manager/confirm_delete.html', {'item': category, 'type': 'Category'})

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def staff_list(request):
    # Managers can see the staff list but only the owner can manage all users
    staff_users = User.objects.filter(profile__role__in=['staff', 'manager', 'owner']).select_related('profile')
    return render(request, 'manager/staff_list.html', {'staff_users': staff_users})

@login_required
@role_required(allowed_roles=['owner'])
def user_list(request):
    # This is for the Owner to see everyone (Customers, Staff, Managers)
    users_qs = User.objects.all().select_related('profile').order_by('-date_joined')
    
    # Internal check to fix any missing profiles on the fly
    for u in users_qs:
        try:
            profile = u.profile
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=u)
            
    return render(request, 'manager/user_list.html', {'users': users_qs})

@login_required
@owner_required
def staff_add(request):
    from .forms import StaffUserForm
    if request.method == 'POST':
        form = StaffUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.username} created successfully.")
            return redirect('manager:user_list')
    else:
        form = StaffUserForm()
    return render(request, 'manager/staff_form.html', {'form': form, 'title': 'Create New User'})

@login_required
@owner_required
def staff_edit(request, pk):
    from .forms import StaffUserForm
    user_to_edit = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = StaffUserForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Profile for {user_to_edit.username} updated.")
            return redirect('manager:user_list')
    else:
        form = StaffUserForm(instance=user_to_edit)
    return render(request, 'manager/staff_form.html', {'form': form, 'staff': user_to_edit, 'title': 'Edit User Profile'})

@login_required
@owner_required
def staff_delete(request, pk):
    staff = get_object_or_404(User, pk=pk)
    if staff == request.user:
        messages.error(request, "You cannot delete yourself.")
        return redirect('manager:staff_list')
    if request.method == 'POST':
        staff.delete()
        messages.success(request, "Staff account deleted.")
        return redirect('manager:staff_list')
    return render(request, 'manager/confirm_delete.html', {'item': staff, 'type': 'Staff User'})

@login_required
@role_required(allowed_roles=['owner'])
def reports(request):
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    # Monthly Revenue calculation
    monthly_orders = Order.objects.filter(
        created_at__date__gte=first_day_of_month,
        created_at__date__lte=today
    ).exclude(status='cancelled')
    
    revenue_month = monthly_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders_month = monthly_orders.count()
    
    context = {
        'revenue_month': revenue_month,
        'total_orders_month': total_orders_month,
        'current_month': today.strftime('%B %Y')
    }
    return render(request, 'manager/reports.html', context)

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def order_archive(request):
    date_query = request.GET.get('date')
    if date_query:
        orders = Order.objects.filter(is_archived=True, created_at__date=date_query).order_by('-created_at')
    else:
        orders = Order.objects.filter(is_archived=True).order_by('-created_at')
        
    return render(request, 'manager/order_archive.html', {
        'orders': orders, 
        'date_query': date_query,
    })

@login_required
@role_required(allowed_roles=['owner', 'manager'])
def reset_daily_orders(request):
    if request.method == 'POST':
        # Archive ALL unarchived orders to ensure the dashboard is fully cleared for a new session
        archived_count = Order.objects.filter(
            is_archived=False
        ).update(is_archived=True)
        
        messages.success(request, f"Successfully cleared dashboard and archived {archived_count} orders.")
        return redirect('manager:dashboard')
    return redirect('manager:dashboard')
