from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Server, ServerUpdate, Service, HyperLink, Host, VirtualMachine
from .forms import HostForm, VirtualMachineForm
from accounts.mixins import RoleBasedAccessMixin

# 🔐 Mixin to filter servers by user department and role
class ServerAccessMixin(RoleBasedAccessMixin):
    def get_queryset(self):
        user = self.request.user
        # Superuser and Admin can see all servers
        if user.is_superuser or user.is_admin():
            return Server.objects.all()
        # Manager and Viewer can only see servers in their departments
        return Server.objects.filter(department__in=user.departments.all()).distinct()


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
        context['hyperlinks'] = self.object.HyperLink.all()  # Add this line
        return context


# ➕ Add Server (Admin and Managers)
class ServerCreateView(RoleBasedAccessMixin, CreateView):
    model = Server
    fields = ['name', 'ip_address', 'os', 'cpu', 'memory', 'disk', 'location', 'department', 'owner']
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
    fields = ['name', 'ip_address', 'os', 'cpu', 'memory', 'disk', 'location', 'department', 'owner']
    template_name = "servers/server_form.html"
    success_url = reverse_lazy('core:server-list')
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can update servers

    def test_func(self):
        user = self.request.user
        server = self.get_object()
        
        # Admin and superuser can update any server
        if user.is_superuser or user.is_admin():
            return True
            
        # Manager can only update servers in their departments
        if user.is_manager() and server.department in user.departments.all():
            return True
            
        return False
    
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
        user = self.request.user
        
        # Admin and superuser can update any server
        if user.is_superuser or user.is_admin():
            return True
            
        # If server_id is in kwargs, check if user has access to this server
        if 'server_id' in self.kwargs:
            server = get_object_or_404(Server, id=self.kwargs['server_id'])
            # Manager can only update servers in their departments
            return user.is_manager() and server.department in user.departments.all()
            
        return user.is_manager()  # Will be filtered in get_form

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
        user = self.request.user
        
        # Admin and superuser can add services to any server
        if user.is_superuser or user.is_admin():
            return True
            
        # If server_id is in kwargs, check if user has access to this server
        if 'server_id' in self.kwargs:
            server = get_object_or_404(Server, id=self.kwargs['server_id'])
            # Manager can only add services to servers in their departments
            return user.is_manager() and server.department in user.departments.all()
            
        return user.is_manager()  # Will be filtered in get_form

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


class HyperLinkCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = HyperLink
    fields = ['servers', 'url', 'is_enabled']
    template_name = "servers/hyperlink_form.html"
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
            form.fields['servers'].queryset = Server.objects.filter(
                department__in=self.request.user.departments.all()
            ).distinct()
        
        # If server_id is in kwargs, pre-select the server
        if 'server_id' in self.kwargs:
            form.fields['servers'].initial = self.kwargs['server_id']
            form.fields['servers'].widget.attrs['readonly'] = True
            
        return form

    def form_valid(self, form):
        # Double-check server access permission
        if not self.request.user.is_superuser:
            if form.instance.servers.department not in self.request.user.departments.all():
                form.add_error('servers', 'You can only add URLs to servers in your departments')
                return self.form_invalid(form)
        return super().form_valid(form)


class HyperLinkDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = HyperLink
    template_name = "servers/hyperlink_detail.html"
    context_object_name = "hyperlink"
    
    def test_func(self):
        hyperlink = self.get_object()
        # Allow access if user is superuser or server's department is in user's departments
        return self.request.user.is_superuser or hyperlink.servers.department in self.request.user.departments.all()


class HyperLinkUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = HyperLink
    fields = ['url', 'is_enabled']
    template_name = "servers/hyperlink_form.html"
    success_url = reverse_lazy('core:server-list')
    
    def test_func(self):
        hyperlink = self.get_object()
        # Allow access if user is superuser or server's department is in user's departments
        return self.request.user.is_superuser or hyperlink.servers.department in self.request.user.departments.all()


class HyperLinkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = HyperLink
    template_name = "servers/hyperlink_confirm_delete.html"
    success_url = reverse_lazy('core:server-list')
    
    def test_func(self):
        hyperlink = self.get_object()
        # Allow access if user is superuser or server's department is in user's departments
        return self.request.user.is_superuser or hyperlink.servers.department in self.request.user.departments.all()

class HyperLinkListView(LoginRequiredMixin, ListView):
    model = HyperLink
    template_name = "servers/hyperlink_list.html"
    context_object_name = "hyperlinks"
    
    def get_queryset(self):
        # Get all hyperlinks the user has access to
        if self.request.user.is_superuser:
            return HyperLink.objects.all()
        # Filter hyperlinks by user's departments
        return HyperLink.objects.filter(
            servers__department__in=self.request.user.departments.all()
        ).distinct()
    
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
class HostAccessMixin(LoginRequiredMixin):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Host.objects.all()
        # Filter hosts by user's departments
        return Host.objects.filter(department__in=self.request.user.departments.all()).distinct()

# 🖥️ Host List with VMs
class HostVMListView(HostAccessMixin, ListView):
    model = Host
    template_name = "servers/host_vm_list.html"
    context_object_name = "hosts"
    
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
        context['virtual_machines'] = self.object.virtual_machines.all()
        return context

# ➕ Add Host
class HostCreateView(LoginRequiredMixin, CreateView):
    model = Host
    form_class = HostForm
    template_name = "servers/host_form.html"
    success_url = reverse_lazy('core:host-vm-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit department choices to user's departments unless superuser
        if not self.request.user.is_superuser:
            form.fields['department'].queryset = self.request.user.departments.all()
        return form

    def form_valid(self, form):
        # Ensure user can only create hosts for their departments
        if not self.request.user.is_superuser:
            if form.instance.department not in self.request.user.departments.all():
                form.add_error('department', 'You can only create hosts for your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# ✏️ Update Host
class HostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Host
    form_class = HostForm
    template_name = "servers/host_form.html"
    success_url = reverse_lazy('core:host-vm-list')

    def test_func(self):
        # Allow access if user is superuser or host's department is in user's departments
        host = self.get_object()
        return self.request.user.is_superuser or host.department in self.request.user.departments.all()
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit department choices to user's departments unless superuser
        if not self.request.user.is_superuser:
            form.fields['department'].queryset = self.request.user.departments.all()
        return form

    def form_valid(self, form):
        # Ensure user can only update hosts to their departments
        if not self.request.user.is_superuser:
            if form.instance.department not in self.request.user.departments.all():
                form.add_error('department', 'You can only assign hosts to your departments')
                return self.form_invalid(form)
        return super().form_valid(form)

# ➕ Add VM
class VMCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = VirtualMachine
    form_class = VirtualMachineForm
    template_name = "servers/vm_form.html"
    success_url = reverse_lazy('core:host-vm-list')

    def test_func(self):
        # If host_id is in kwargs, check if user has access to this host
        if 'host_id' in self.kwargs:
            host = get_object_or_404(Host, id=self.kwargs['host_id'])
            return self.request.user.is_superuser or host.department in self.request.user.departments.all()
        return True  # Will be filtered in get_form

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
class VMDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = VirtualMachine
    template_name = "servers/vm_detail.html"
    context_object_name = "vm"
    
    def test_func(self):
        vm = self.get_object()
        # Allow access if user is superuser or host's department is in user's departments
        return self.request.user.is_superuser or vm.host.department in self.request.user.departments.all()

# ✏️ Update VM
class VMUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = VirtualMachine
    form_class = VirtualMachineForm
    template_name = "servers/vm_form.html"
    success_url = reverse_lazy('core:host-vm-list')

    def test_func(self):
        # Allow access if user is superuser or VM's host department is in user's departments
        vm = self.get_object()
        return self.request.user.is_superuser or vm.host.department in self.request.user.departments.all()
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit host choices to user's accessible hosts
        if not self.request.user.is_superuser:
            form.fields['host'].queryset = Host.objects.filter(
                department__in=self.request.user.departments.all()
            ).distinct()
        return form

    def form_valid(self, form):
        # Double-check host access permission
        if not self.request.user.is_superuser:
            if form.instance.host.department not in self.request.user.departments.all():
                form.add_error('host', 'You can only assign VMs to hosts in your departments')
                return self.form_invalid(form)
        return super().form_valid(form)