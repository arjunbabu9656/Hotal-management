from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserProfile

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            profile = user.profile
            profile.role = 'customer'
            profile.phone = form.cleaned_data.get('phone')
            profile.room_number = form.cleaned_data.get('room_number')
            profile.save()
            
            auth_login(request, user)
            messages.success(request, "Registration successful. Welcome guest!")
            return redirect('menu:menu_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'Guest'})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                role = user.profile.role
                if role == 'manager':
                    return redirect('manager:dashboard')
                elif role == 'staff':
                    return redirect('staff:dashboard')
                else:
                    return redirect('menu:menu_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')

def access_denied(request):
    return render(request, 'accounts/403.html', status=403)

def index(request):
    if request.user.is_authenticated:
        role = request.user.profile.role
        if role in ['manager', 'owner']:
            return redirect('manager:dashboard')
        elif role == 'staff':
            return redirect('staff:dashboard')
    
    # Defaults to menu for guests and customers
    return redirect('menu:menu_list')
