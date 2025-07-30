from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Department

def register_view(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('core:DashboardView') 
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('core:DashboardView') 
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('core:DashboardView')  

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = CustomerProfileForm(instance=request.user, user=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

class DepartmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Department
    template_name = 'accounts/department_list.html'
    context_object_name = 'departments'
    
    def test_func(self):
        return self.request.user.is_superuser

class DepartmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Department
    template_name = 'accounts/department_form.html'
    fields = ['name']
    success_url = reverse_lazy('accounts:department-list')
    
    def test_func(self):
        return self.request.user.is_superuser

class DepartmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Department
    template_name = 'accounts/department_form.html'
    fields = ['name']
    success_url = reverse_lazy('accounts:department-list')
    
    def test_func(self):
        return self.request.user.is_superuser

class DepartmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Department
    template_name = 'accounts/department_confirm_delete.html'
    success_url = reverse_lazy('accounts:department-list')
    
    def test_func(self):
        return self.request.user.is_superuser

def custom_permission_denied(request, exception=None):
    """
    Custom view for handling 403 (Permission Denied) errors with a user-friendly message.
    """
    return render(request, '403.html', status=403)


@login_required
def impersonate_user(request, user_id):
    if not request.user.is_admin():
        messages.error(request, "You do not have permission to impersonate users.")
        return redirect('accounts:user-list')

    try:
        user_to_impersonate = User.objects.get(id=user_id)
        
        if user_to_impersonate.is_superuser or user_to_impersonate.is_admin():
            messages.error(request, "You cannot impersonate another administrator or superuser.")
            return redirect('accounts:user-detail', pk=user_id)

        # Set session variables. The middleware will handle the user switch.
        request.session['impersonator_id'] = request.user.id
        request.session['impersonating_id'] = user_to_impersonate.id
        
        messages.success(request, f"You are now impersonating {user_to_impersonate.username}.")
        return redirect('core:DashboardView')

    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('accounts:user-list')

@login_required
def stop_impersonating(request):
    impersonator_id = request.session.get('impersonator_id')
    if not impersonator_id:
        messages.error(request, "You are not impersonating anyone.")
        return redirect('accounts:user-list')

    try:
        original_user = User.objects.get(id=impersonator_id)
        original_user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, original_user)
        request.session.pop('impersonator_id', None)
        request.session.pop('impersonating_id', None)
        messages.success(request, "Stopped impersonating.")
    except User.DoesNotExist:
        messages.error(request, "Could not revert to original user. Please log out and log back in.")
        return redirect('accounts:logout')
    
    return redirect('accounts:user-list')

