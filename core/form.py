from django import forms
from .models import Server, ServerUpdate, Service, AuditLog

class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'ip_address', 'os', 'cpu', 'memory', 'disk', 'location', 'department']

class ServerUpdateForm(forms.ModelForm):
    class Meta:
        model = ServerUpdate
        fields = ['server', 'update_type', 'notes', 'attachment']

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service 
        fields = ['server', 'name', 'port', 'status', 'last_restart']

