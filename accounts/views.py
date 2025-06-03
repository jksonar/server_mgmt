from django.shortcuts import render, redirect, get_object_or_404
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
        form = CustomerProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = CustomerProfileForm(instance=request.user)
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

