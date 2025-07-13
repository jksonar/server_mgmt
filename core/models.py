from django.db import models
from django.conf import settings
from accounts.models import Department
from datetime import datetime, timedelta
from auditlog.registry import auditlog

class Server(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    os = models.CharField(max_length=100)
    cpu = models.CharField(max_length=100, blank=True)
    memory = models.CharField(max_length=50, blank=True)
    disk = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    # Replace department field with ForeignKey to Department
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='servers')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_servers')
    # Remove the commented out groups field as we'll use departments instead

    def __str__(self):
        return f"{self.name} ({self.ip_address})"


class ServerUpdate(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='updates')
    update_type = models.CharField(max_length=100)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='updates_performed')
    update_time = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='update_logs/', blank=True, null=True)

    def __str__(self):
        return f"{self.server.name} - {self.update_type} at {self.update_time}"


class Service(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    port = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('running', 'Running'), ('stopped', 'Stopped')])
    last_restart = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} on {self.server.name}"


class HyperLink(models.Model):
    servers = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='hyperlinks')
    url = models.CharField(max_length=100)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='HyperLink_created_by')
    created_at = models.DateTimeField(auto_now_add=True)
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.url} on {self.servers.name}"

# Host-VM Models
class Host(models.Model):
    hostname = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    status = models.CharField(max_length=20, choices=[('online', 'Online'), ('offline', 'Offline')])
    total_cpu = models.CharField(max_length=100, blank=True)
    total_ram = models.CharField(max_length=50, blank=True)
    hyperv_version = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='hosts')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_hosts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"

class VirtualMachine(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='virtual_machines')
    name = models.CharField(max_length=100)
    vm_id = models.CharField(max_length=100, blank=True)
    guest_os = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[('running', 'Running'), ('stopped', 'Stopped')])
    assigned_cpu = models.CharField(max_length=100, blank=True)
    assigned_ram = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} on {self.host.hostname}"

# SSL Certificate Expiry Model
class SSLCertificate(models.Model):
    NOTIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('notified', 'Notified'),
        ('expired', 'Expired'),
    ]
    
    hyperlink = models.OneToOneField(HyperLink, on_delete=models.CASCADE, related_name='ssl_certificate')
    expiry_date = models.DateTimeField(null=True, blank=True)
    last_checked = models.DateTimeField(auto_now=True)
    notification_status = models.CharField(max_length=20, choices=NOTIFICATION_STATUS_CHOICES, default='pending')
    issuer = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    is_valid = models.BooleanField(default=True)
    
    def __str__(self):
        return f"SSL for {self.hyperlink.url} (Expires: {self.expiry_date})"
    
    @property
    def days_to_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - datetime.now().replace(tzinfo=self.expiry_date.tzinfo)).days
    
    @property
    def status(self):
        if not self.expiry_date:
            return "Unknown"
        days = self.days_to_expiry
        if days is None:
            return "Unknown"
        elif days < 0:
            return "Expired"
        elif days < 7:
            return "Critical"
        elif days < 30:
            return "Warning"
        else:
            return "Valid"
    
    @property
    def status_color(self):
        status = self.status
        if status == "Expired":
            return "danger"
        elif status == "Critical":
            return "danger"
        elif status == "Warning":
            return "warning"
        elif status == "Valid":
            return "success"
        else:
            return "secondary"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('VIEW', 'View'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    object_repr = models.CharField(max_length=200, null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} at {self.timestamp}"

