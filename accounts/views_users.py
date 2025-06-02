from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from .models import User
from .forms import AdminUserCreationForm, AdminUserEditForm

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    
    def test_func(self):
        # Only admins can view the user list
        return self.request.user.is_superuser or self.request.user.is_admin()

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = AdminUserCreationForm
    template_name = 'accounts/user_add.html'
    success_url = reverse_lazy('accounts:user-list')
    
    def test_func(self):
        # Only admins can create users
        return self.request.user.is_superuser or self.request.user.is_admin()
    
    def form_valid(self, form):
        messages.success(self.request, 'User created successfully!')
        return super().form_valid(form)

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = AdminUserEditForm
    template_name = 'accounts/user_edit.html'
    success_url = reverse_lazy('accounts:user-list')
    
    def test_func(self):
        # Only admins can update users
        return self.request.user.is_superuser or self.request.user.is_admin()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        print(f"Form kwargs: {kwargs}")
        return kwargs
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        print(f"Form fields: {form.fields.keys()}")
        print(f"Form is bound: {form.is_bound}")
        return form
    
    def form_valid(self, form):
        # Ensure we don't change the current user's session
        current_user = self.request.user
        response = super().form_valid(form)
        # If the form submission somehow affected the current user's session,
        # restore it to the original user
        if self.request.user != current_user:
            from django.contrib.auth import login
            login(self.request, current_user)
        messages.success(self.request, 'User updated successfully!')
        return response

class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'  # Use user_obj to avoid conflict with request.user
    
    def test_func(self):
        # Only admins can view user details
        return self.request.user.is_superuser or self.request.user.is_admin()