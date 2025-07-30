from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from accounts.models import User
from accounts.forms import AdminUserCreationForm, AdminUserEditForm
from accounts.mixins import ImpersonationRequiredMixin

User = get_user_model()


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_admin()


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user'

    def test_func(self):
        return self.request.user.is_admin()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_obj'] = self.get_object()
        return context


class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, ImpersonationRequiredMixin, CreateView):
    model = User
    template_name = 'accounts/user_add.html'
    form_class = AdminUserCreationForm
    success_url = reverse_lazy('accounts:user-list')

    def test_func(self):
        return self.request.user.is_admin()


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, ImpersonationRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/user_edit.html'
    form_class = AdminUserEditForm
    success_url = reverse_lazy('accounts:user-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def test_func(self):
        return self.request.user.is_admin()


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user-list')

    def test_func(self):
        return self.request.user.is_admin()

@login_required
def impersonate_user(request, user_id):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to impersonate users.")
        return redirect('accounts:user-list')

    try:
        user_to_impersonate = get_object_or_404(User, id=user_id)
        
        if user_to_impersonate.is_superuser or user_to_impersonate.is_admin:
            messages.error(request, "You cannot impersonate another administrator or superuser.")
            return redirect('accounts:user-detail', user_id=user_id)

        if 'original_user_id' not in request.session:
            request.session['original_user_id'] = request.user.id

        logout(request)
        user_to_impersonate.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user_to_impersonate)
        
        messages.success(request, f"You are now impersonating {user_to_impersonate.username}.")
        return redirect('core:DashboardView')

    except User.DoesNotExist:
        messages.error(request, "User to impersonate not found.")
        return redirect('accounts:user-list')

@login_required
def stop_impersonating(request):
    original_user_id = request.session.get('original_user_id')
    
    if not original_user_id:
        messages.error(request, "You are not currently impersonating anyone.")
        return redirect('core:DashboardView')

    try:
        original_user = get_object_or_404(User, id=original_user_id)
        
        logout(request)
        original_user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, original_user)
        
        del request.session['original_user_id']
        
        messages.success(request, "Stopped impersonating. You are now logged in as your original user.")
        return redirect('core:DashboardView')

    except User.DoesNotExist:
        messages.error(request, "Original user not found. Please log out and log back in.")
        # Clear the session to be safe
        request.session.flush()
        return redirect('accounts:login')