from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Server, ServerUpdate, Service

# 🔐 Mixin to filter servers by user department
class ServerAccessMixin(LoginRequiredMixin):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Server.objects.all()
        # Filter servers by user's departments
        return Server.objects.filter(department__in=self.request.user.departments.all()).distinct()


# 📊 Dashboard View (Optional)
class DashboardView(LoginRequiredMixin, ListView):
    model = Server
    template_name = "dashboard.html"
    context_object_name = "servers"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Server.objects.all()
        # Filter servers by user's departments
        return Server.objects.filter(department__in=self.request.user.departments.all()).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates_count'] = ServerUpdate.objects.count()
        context['services_count'] = Service.objects.count()
        return context


# 🖥️ Server List
class ServerListView(ServerAccessMixin, ListView):
    model = Server
    template_name = "servers/server_list.html"
    context_object_name = "servers"


# 🔍 Server Detail
class ServerDetailView(ServerAccessMixin, DetailView):
    model = Server
    template_name = "servers/server_detail.html"
    context_object_name = "server"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = self.object.updates.all()
        context['services'] = self.object.services.all()
        return context


# ➕ Add Server (Admin and department managers)
class ServerCreateView(LoginRequiredMixin, CreateView):
    model = Server
    fields = ['name', 'ip_address', 'os', 'cpu', 'memory', 'disk', 'location', 'department', 'owner']
    template_name = "servers/server_form.html"
    success_url = reverse_lazy('core:server-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit department choices to user's departments unless superuser
        if not self.request.user.is_superuser:
            form.fields['department'].queryset = self.request.user.departments.all()
        return form

    def form_valid(self, form):
        # Ensure user can only create servers for their departments
        if not self.request.user.is_superuser:
            if form.instance.department not in self.request.user.departments.all():
                form.add_error('department', 'You can only create servers for your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# ✏️ Update Server (Admin and department managers)
class ServerUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Server
    fields = ['name', 'ip_address', 'os', 'cpu', 'memory', 'disk', 'location', 'department', 'owner']
    template_name = "servers/server_form.html"
    success_url = reverse_lazy('core:server-list')

    def test_func(self):
        # Allow access if user is superuser or server's department is in user's departments
        server = self.get_object()
        return self.request.user.is_superuser or server.department in self.request.user.departments.all()
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit department choices to user's departments unless superuser
        if not self.request.user.is_superuser:
            form.fields['department'].queryset = self.request.user.departments.all()
        return form

    def form_valid(self, form):
        # Ensure user can only update servers to their departments
        if not self.request.user.is_superuser:
            if form.instance.department not in self.request.user.departments.all():
                form.add_error('department', 'You can only assign servers to your departments')
                return self.form_invalid(form)
        return super().form_valid(form)


# ➕ Add Update Entry
class ServerUpdateCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ServerUpdate
    fields = ['server', 'update_type', 'notes', 'attachment']
    template_name = "servers/update_form.html"
    success_url = reverse_lazy('core:server-list')

    def test_func(self):
        # If server_id is in kwargs, check if user has access to this server
        if 'server_id' in self.kwargs:
            server = get_object_or_404(Server, id=self.kwargs['server_id'])
            return self.request.user.is_superuser or server.department in self.request.user.departments.all()
        return True  # Will be filtered in get_form

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit server choices to user's accessible servers
        if not self.request.user.is_superuser:
            form.fields['server'].queryset = Server.objects.filter(
                department__in=self.request.user.departments.all()
            ).distinct()
        
        # If server_id is in kwargs, pre-select the server
        if 'server_id' in self.kwargs:
            form.fields['server'].initial = self.kwargs['server_id']
            form.fields['server'].widget.attrs['readonly'] = True
            
        return form

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        # Double-check server access permission
        if not self.request.user.is_superuser:
            if form.instance.server.department not in self.request.user.departments.all():
                form.add_error('server', 'You can only update servers in your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# ➕ Add Service
class ServiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Service
    fields = ['server', 'name', 'port', 'status', 'last_restart']
    template_name = "servers/service_form.html"
    success_url = reverse_lazy('core:server-list')

    def test_func(self):
        # If server_id is in kwargs, check if user has access to this server
        if 'server_id' in self.kwargs:
            server = get_object_or_404(Server, id=self.kwargs['server_id'])
            return self.request.user.is_superuser or server.department in self.request.user.departments.all()
        return True  # Will be filtered in get_form

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit server choices to user's accessible servers
        if not self.request.user.is_superuser:
            form.fields['server'].queryset = Server.objects.filter(
                department__in=self.request.user.departments.all()
            ).distinct()
        
        # If server_id is in kwargs, pre-select the server
        if 'server_id' in self.kwargs:
            form.fields['server'].initial = self.kwargs['server_id']
            form.fields['server'].widget.attrs['readonly'] = True
            
        return form

    def form_valid(self, form):
        # Double-check server access permission
        if not self.request.user.is_superuser:
            if form.instance.server.department not in self.request.user.departments.all():
                form.add_error('server', 'You can only add services to servers in your departments')
                return self.form_invalid(form)
        return super().form_valid(form)
