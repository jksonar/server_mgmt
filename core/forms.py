from django import forms
from .models import Server, ServerUpdate, Service, HyperLink, Host, VirtualMachine

class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'ip_address', 'os', 'cpu_cores', 'server_type', 'server_kind', 'cpu', 'memory', 'disk', 'location', 'department']

class ServerUpdateForm(forms.ModelForm):
    class Meta:
        model = ServerUpdate
        fields = ['server', 'update_type', 'notes', 'attachment']

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service 
        fields = ['server', 'name', 'port', 'status', 'last_restart']

class HyperLinkForm(forms.ModelForm):
    class Meta:
        model = HyperLink
        fields = ['servers', 'url', 'is_enabled']

class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ['hostname', 'ip_address', 'status', 'total_cpu', 'total_ram', 
                 'hyperv_version', 'department', 'owner']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class VirtualMachineForm(forms.ModelForm):
    class Meta:
        model = VirtualMachine
        fields = ['host', 'name', 'vm_id', 'guest_os', 'status', 
                 'assigned_cpu', 'assigned_ram', 'ip_address']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'