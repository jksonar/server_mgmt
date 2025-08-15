from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Server, ServerUpdate, Service, HyperLink, Host, VirtualMachine
from .forms import HostForm, VirtualMachineForm
from accounts.mixins import RoleBasedAccessMixin

# 🔐 Mixin to filter servers by user department and role
class ServerAccessMixin(RoleBasedAccessMixin):
    model = Server
    allowed_roles = ['admin', 'manager', 'viewer']  # All roles can access servers (with appropriate permissions)


# 📊 Dashboard View (Optional)
class DashboardView(LoginRequiredMixin, ListView):
    model = Server
    template_name = "dashboard.html"
    context_object_name = "servers"

    def get_queryset(self):
        user = self.request.user
        # Superusers and Admins can see all servers
        if user.is_superuser or user.is_admin():
            return Server.objects.all()
        # Managers and Viewers can only see servers in their departments
        return Server.objects.filter(department__in=user.departments.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Count updates and services based on user's access level
        if user.is_superuser or user.is_admin():
            context['updates_count'] = ServerUpdate.objects.count()
            context['services_count'] = Service.objects.count()
        else:
            # Filter counts by user's departments
            context['updates_count'] = ServerUpdate.objects.filter(
                server__department__in=user.departments.all()
            ).distinct().count()
            context['services_count'] = Service.objects.filter(
                server__department__in=user.departments.all()
            ).distinct().count()
        return context


# 📋 List all servers
class ServerListView(ServerAccessMixin, ListView):
    model = Server
    template_name = "servers/server_list.html"
    context_object_name = "servers"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        # Get the paginate_by value from the query parameters.
        paginate_by_str = self.request.GET.get('paginate_by')

        # If a valid value is provided, update the session.
        if paginate_by_str and paginate_by_str in ['10', '25', '50', '100']:
            self.request.session['paginate_by'] = int(paginate_by_str)

        # Return the value from the session, or the default.
        return self.request.session.get('paginate_by', self.paginate_by)

    def get_queryset(self):
        user = self.request.user
        # Superusers and Admins can see all servers
        if user.is_superuser or user.is_admin():
            return Server.objects.all()
        # Managers and Viewers can only see servers in their departments
        return Server.objects.filter(department__in=user.departments.all()).distinct()


# 🔍 View server details
class ServerDetailView(ServerAccessMixin, DetailView):
    model = Server
    template_name = "servers/server_detail.html"
    context_object_name = "server"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = self.object.updates.all()
        context['services'] = self.object.services.all()
        context['hyperlinks'] = self.object.hyperlinks.all()
        return context


# ➕ Add Server (Admin and Managers)
class ServerCreateView(RoleBasedAccessMixin, CreateView):
    model = Server
    fields = ['name', 'ip_address', 'os', 'cpu_cores', 'server_type', 'server_kind', 'cpu', 'memory', 'disk', 'location', 'department', 'owner']
    template_name = "servers/server_form.html"
    success_url = reverse_lazy('core:server-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can create servers
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        # Limit department choices to user's departments unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            form.fields['department'].queryset = user.departments.all()
        return form

    def form_valid(self, form):
        user = self.request.user
        # Ensure user can only create servers for their departments unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            if form.instance.department not in user.departments.all():
                form.add_error('department', 'You can only create servers for your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# ✏️ Update Server (Admin and Managers)
class ServerUpdateView(RoleBasedAccessMixin, UpdateView):
    model = Server
    fields = ['name', 'ip_address', 'os', 'cpu_cores', 'server_type', 'server_kind', 'cpu', 'memory', 'disk', 'location', 'department', 'owner']
    template_name = "servers/server_form.html"
    success_url = reverse_lazy('core:server-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can update servers

    def test_func(self):
        # The RoleBasedAccessMixin now handles the core role and department checks.
        # We only need to ensure the user has the allowed role.
        return super().test_func()
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        # Limit department choices to user's departments unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            form.fields['department'].queryset = user.departments.all()
        return form

    def form_valid(self, form):
        user = self.request.user
        # Ensure user can only update servers to their departments unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            if form.instance.department not in user.departments.all():
                form.add_error('department', 'You can only assign servers to your departments')
                return self.form_invalid(form)
        return super().form_valid(form)


# ➕ Add Update Entry
class ServerUpdateCreateView(RoleBasedAccessMixin, CreateView):
    model = ServerUpdate
    fields = ['server', 'update_type', 'notes', 'attachment']
    template_name = "servers/update_form.html"
    success_url = reverse_lazy('core:server-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can add update entries

    def test_func(self):
        # The RoleBasedAccessMixin now handles the core role and department checks.
        # We only need to ensure the user has the allowed role.
        # For creation, we also need to check if a server_id is provided in kwargs
        # and if the user has access to that specific server.
        if 'server_id' in self.kwargs:
            server = get_object_or_404(Server, id=self.kwargs['server_id'])
            self.object = server  # Set object for RoleBasedAccessMixin to check department
        return super().test_func()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Limit server choices to user's accessible servers unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            form.fields['server'].queryset = Server.objects.filter(
                department__in=user.departments.all()
            ).distinct()
        
        # If server_id is in kwargs, pre-select the server
        if 'server_id' in self.kwargs:
            form.fields['server'].initial = self.kwargs['server_id']
            form.fields['server'].widget.attrs['readonly'] = True
            
        return form

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        user = self.request.user
        
        # Double-check server access permission unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            if form.instance.server.department not in user.departments.all():
                form.add_error('server', 'You can only update servers in your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# ➕ Add Service
class ServiceCreateView(RoleBasedAccessMixin, CreateView):
    model = Service
    fields = ['server', 'name', 'port', 'status', 'last_restart']
    template_name = "servers/service_form.html"
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can add services
    success_url = reverse_lazy('core:server-list')

    def test_func(self):
        # The RoleBasedAccessMixin now handles the core role and department checks.
        # We only need to ensure the user has the allowed role.
        # For creation, we also need to check if a server_id is provided in kwargs
        # and if the user has access to that specific server.
        if 'server_id' in self.kwargs:
            server = get_object_or_404(Server, id=self.kwargs['server_id'])
            self.object = server  # Set object for RoleBasedAccessMixin to check department
        return super().test_func()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Limit server choices to user's accessible servers unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            form.fields['server'].queryset = Server.objects.filter(
                department__in=user.departments.all()
            ).distinct()
        
        # If server_id is in kwargs, pre-select the server
        if 'server_id' in self.kwargs:
            form.fields['server'].initial = self.kwargs['server_id']
            form.fields['server'].widget.attrs['readonly'] = True
            
        return form

    def form_valid(self, form):
        user = self.request.user
        
        # Double-check server access permission unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            if form.instance.server.department not in user.departments.all():
                form.add_error('server', 'You can only add services to servers in your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# ✏️ Edit Service
class ServiceUpdateView(RoleBasedAccessMixin, UpdateView):
    model = Service
    fields = ['server', 'name', 'port', 'status', 'last_restart']
    template_name = "servers/service_update_form.html"
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can edit services
    
    def get_success_url(self):
        return reverse_lazy('core:server-detail', kwargs={'pk': self.object.server.pk})
    
    def test_func(self):
        # The RoleBasedAccessMixin now handles the core role and department checks.
        # We only need to ensure the user has the allowed role.
        return super().test_func()
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Limit server choices to user's accessible servers unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            form.fields['server'].queryset = Server.objects.filter(
                department__in=user.departments.all()
            ).distinct()
            
        return form

# 🗑️ Delete Service
class ServiceDeleteView(RoleBasedAccessMixin, DeleteView):
    model = Service
    template_name = "servers/service_confirm_delete.html"
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can delete services
    
    def get_success_url(self):
        return reverse_lazy('core:server-detail', kwargs={'pk': self.object.server.pk})
    
    def test_func(self):
        # The RoleBasedAccessMixin now handles the core role and department checks.
        # We only need to ensure the user has the allowed role.
        return super().test_func()


# 📋 List all services
class ServiceListView(RoleBasedAccessMixin, ListView):
    model = Service
    template_name = "servers/service_list.html"
    context_object_name = "services"
    allowed_roles = ['admin', 'manager', 'viewer']  # All roles can view services
    
    def get_queryset(self):
        user = self.request.user
        # Superuser and Admin can see all services
        if user.is_superuser or user.is_admin():
            return Service.objects.all()
        # Manager and Viewer can only see services on servers in their departments
        return Service.objects.filter(server__department__in=user.departments.all()).distinct()


# 🔍 View service details
class ServiceDetailView(RoleBasedAccessMixin, DetailView):
    model = Service
    template_name = "servers/service_detail.html"
    context_object_name = "service"
    allowed_roles = ['admin', 'manager', 'viewer']  # All roles can view service details





class HyperLinkCreateView(RoleBasedAccessMixin, CreateView):
    model = HyperLink
    fields = ['servers', 'url', 'is_enabled']
    template_name = "servers/hyperlink_form.html"
    success_url = reverse_lazy('core:server-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can create URLs
    
    def test_func(self):
        # The RoleBasedAccessMixin now handles the core role and department checks.
        # We only need to ensure the user has the allowed role.
        # For creation, we also need to check if a server_id is provided in kwargs
        # and if the user has access to that specific server.
        if 'server_id' in self.kwargs:
            server = get_object_or_404(Server, id=self.kwargs['server_id'])
            self.object = server  # Set object for RoleBasedAccessMixin to check department
        return super().test_func()
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit server choices to user's accessible servers
        if not self.request.user.is_superuser:
            form.fields['servers'].queryset = Server.objects.filter(
                department__in=self.request.user.departments.all()
            ).distinct()
        
        # Get server_id from kwargs or query parameters
        server_id = self.kwargs.get('server_id') or self.request.GET.get('server_id')
        
        # If server_id exists, pre-select the server
        if server_id:
            form.fields['servers'].initial = server_id
            form.fields['servers'].widget.attrs['readonly'] = True
            
        return form

    def form_valid(self, form):
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        
        # Double-check server access permission
        if not self.request.user.is_superuser:
            if form.instance.servers.department not in self.request.user.departments.all():
                form.add_error('servers', 'You can only add URLs to servers in your departments')
                return self.form_invalid(form)
        
        # Get the server_id from the request to set success_url to return to server detail page
        server_id = self.kwargs.get('server_id') or self.request.GET.get('server_id')
        if server_id:
            self.success_url = reverse_lazy('core:server-detail', kwargs={'pk': server_id})
            
        return super().form_valid(form)


class HyperLinkDetailView(RoleBasedAccessMixin, DetailView):
    model = HyperLink
    template_name = "servers/hyperlink_detail.html"
    context_object_name = "hyperlink"
    allowed_roles = ['admin', 'manager', 'viewer']  # All roles can view URLs


class HyperLinkUpdateView(RoleBasedAccessMixin, UpdateView):
    model = HyperLink
    fields = ['url', 'is_enabled']
    template_name = "servers/hyperlink_form.html"
    success_url = reverse_lazy('core:server-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can update URLs
    
    def get_success_url(self):
        # Redirect back to the server detail page
        return reverse_lazy('core:server-detail', kwargs={'pk': self.object.servers.id})


class HyperLinkDeleteView(RoleBasedAccessMixin, DeleteView):
    model = HyperLink
    template_name = "servers/hyperlink_confirm_delete.html"
    success_url = reverse_lazy('core:server-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can delete URLs
    
    def get_success_url(self):
        # Store the server ID before deletion
        server_id = self.object.servers.id
        # Redirect back to the server detail page
        return reverse_lazy('core:server-detail', kwargs={'pk': server_id})

class HyperLinkListView(RoleBasedAccessMixin, ListView):
    model = HyperLink
    template_name = "servers/hyperlink_list.html"
    context_object_name = "hyperlinks"
    allowed_roles = ['admin', 'manager', 'viewer']  # All roles can view URL list
    
    def get_queryset(self):
        user = self.request.user
        # Superusers and Admins can see all hyperlinks
        if user.is_superuser or user.is_admin():
            return HyperLink.objects.all()
        # Managers and Viewers can only see hyperlinks for servers in their departments
        return HyperLink.objects.filter(servers__department__in=user.departments.all()).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group hyperlinks by server
        servers_with_links = {}
        
        for hyperlink in self.get_queryset():
            if hyperlink.servers not in servers_with_links:
                servers_with_links[hyperlink.servers] = []
            servers_with_links[hyperlink.servers].append(hyperlink)
        
        context['servers_with_links'] = servers_with_links
        return context

# 🔐 Mixin to filter hosts by user department
class HostAccessMixin(RoleBasedAccessMixin):
    model = Host
    allowed_roles = ['admin', 'manager', 'viewer']  # All roles can access hosts (with appropriate permissions)

# 📋 List all hosts and VMs
class HostVMListView(HostAccessMixin, ListView):
    model = Host
    template_name = "servers/host_vm_list.html"
    context_object_name = "hosts"
    
    def get_queryset(self):
        user = self.request.user
        # Superusers and Admins can see all hosts
        if user.is_superuser or user.is_admin():
            return Host.objects.all()
        # Managers and Viewers can only see hosts in their departments
        return Host.objects.filter(department__in=user.departments.all()).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Include VMs for each host
        hosts_with_vms = {}
        
        for host in self.get_queryset():
            hosts_with_vms[host] = host.virtual_machines.all()
        
        context['hosts_with_vms'] = hosts_with_vms
        return context

# 🔍 Host Detail
class HostDetailView(HostAccessMixin, DetailView):
    model = Host
    template_name = "servers/host_detail.html"
    context_object_name = "host"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vms'] = self.object.virtual_machines.all()
        return context

# ➕ Add Host
class HostCreateView(RoleBasedAccessMixin, CreateView):
    model = Host
    form_class = HostForm
    template_name = "servers/host_form.html"
    success_url = reverse_lazy('core:host-vm-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can create hosts
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        # Limit department choices to user's departments unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            form.fields['department'].queryset = user.departments.all()
        return form

    def form_valid(self, form):
        user = self.request.user
        # Ensure user can only create hosts for their departments unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            if form.instance.department not in user.departments.all():
                form.add_error('department', 'You can only create hosts for your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# ✏️ Update Host
class HostUpdateView(RoleBasedAccessMixin, UpdateView):
    model = Host
    form_class = HostForm
    template_name = "servers/host_form.html"
    success_url = reverse_lazy('core:host-vm-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can update hosts
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        # Limit department choices to user's departments unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            form.fields['department'].queryset = user.departments.all()
        return form

    def form_valid(self, form):
        user = self.request.user
        # Ensure user can only update hosts to their departments unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            if form.instance.department not in user.departments.all():
                form.add_error('department', 'You can only assign hosts to your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# ➕ Add VM
class VMCreateView(RoleBasedAccessMixin, CreateView):
    model = VirtualMachine
    form_class = VirtualMachineForm
    template_name = "servers/vm_form.html"
    success_url = reverse_lazy('core:host-vm-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can create VMs
    
    def test_func(self):
        # The RoleBasedAccessMixin now handles the core role and department checks.
        # We only need to ensure the user has the allowed role.
        # For creation, we also need to check if a host_id is provided in kwargs
        # and if the user has access to that specific host.
        if 'host_id' in self.kwargs:
            host = get_object_or_404(Host, id=self.kwargs['host_id'])
            self.object = host  # Set object for RoleBasedAccessMixin to check department
        return super().test_func()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit host choices to user's accessible hosts
        if not self.request.user.is_superuser:
            form.fields['host'].queryset = Host.objects.filter(
                department__in=self.request.user.departments.all()
            ).distinct()
        
        # If host_id is in kwargs, pre-select the host
        if 'host_id' in self.kwargs:
            form.fields['host'].initial = self.kwargs['host_id']
            form.fields['host'].widget.attrs['readonly'] = True
            
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add host to context if host_id is in kwargs
        if 'host_id' in self.kwargs:
            context['host'] = get_object_or_404(Host, id=self.kwargs['host_id'])
        return context

    def form_valid(self, form):
        # Double-check host access permission
        if not self.request.user.is_superuser:
            if form.instance.host.department not in self.request.user.departments.all():
                form.add_error('host', 'You can only add VMs to hosts in your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# 🔍 VM Detail
class VMDetailView(RoleBasedAccessMixin, DetailView):
    model = VirtualMachine
    template_name = "servers/vm_detail.html"
    context_object_name = "vm"
    allowed_roles = ['admin', 'manager', 'viewer']  # All roles can view VMs

# ✏️ Update VM
class VMUpdateView(RoleBasedAccessMixin, UpdateView):
    model = VirtualMachine
    form_class = VirtualMachineForm
    template_name = "servers/vm_form.html"
    success_url = reverse_lazy('core:host-vm-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can update VMs
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        # Limit host choices to user's accessible hosts unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            form.fields['host'].queryset = Host.objects.filter(
                department__in=user.departments.all()
            ).distinct()
        return form

    def form_valid(self, form):
        user = self.request.user
        # Double-check host access permission unless admin or superuser
        if not (user.is_superuser or user.is_admin()):
            if form.instance.host.department not in user.departments.all():
                form.add_error('host', 'You can only assign VMs to hosts in your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# 🗑️ Delete VM
class VMDeleteView(RoleBasedAccessMixin, DeleteView):
    model = VirtualMachine
    template_name = "servers/vm_confirm_delete.html"
    success_url = reverse_lazy('core:host-vm-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can delete VMs