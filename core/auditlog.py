import json
import threading
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from .models import AuditLog, Server, ServerUpdate, Service, HyperLink, Host, VirtualMachine, SSLCertificate
from accounts.models import Department

# Thread-local storage for request data
_thread_locals = threading.local()

def get_current_request():
    """Get the current request from thread-local storage"""
    return getattr(_thread_locals, 'request', None)

def set_current_request(request):
    """Set the current request in thread-local storage"""
    _thread_locals.request = request

def get_client_ip(request):
    """Extract client IP address from request"""
    if not request:
        return None
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_model_changes(instance, created=False):
    """Get field changes for model instance"""
    if created:
        # For new objects, return all field values
        changes = {}
        for field in instance._meta.fields:
            field_name = field.name
            field_value = getattr(instance, field_name, None)
            if field_value is not None:
                changes[field_name] = {'new': str(field_value)}
        return changes
    
    # For updates, we need to compare with database values
    # This is a simplified approach - in production you might want to use django-model-utils
    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
        changes = {}
        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(old_instance, field_name, None)
            new_value = getattr(instance, field_name, None)
            if old_value != new_value:
                changes[field_name] = {
                    'old': str(old_value) if old_value is not None else None,
                    'new': str(new_value) if new_value is not None else None
                }
        return changes
    except instance.__class__.DoesNotExist:
        return {}

def create_audit_log(user, action, instance, changes=None):
    """Create an audit log entry"""
    request = get_current_request()
    ip_address = get_client_ip(request) if request else None
    
    AuditLog.objects.create(
        user=user,
        ip_address=ip_address,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk) if hasattr(instance, 'pk') else None,
        object_repr=str(instance)[:200],
        changes=changes
    )

# Models to audit
AUDITED_MODELS = [
    Server, ServerUpdate, Service, HyperLink, Host, VirtualMachine, SSLCertificate, Department
]

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """Log model save events"""
    if sender not in AUDITED_MODELS:
        return
    
    request = get_current_request()
    user = getattr(request, 'user', None) if request else None
    
    # Skip if no user (system operations)
    if not user or not user.is_authenticated:
        return
    
    action = 'CREATE' if created else 'UPDATE'
    changes = get_model_changes(instance, created=created)
    
    create_audit_log(user, action, instance, changes)

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """Log model delete events"""
    if sender not in AUDITED_MODELS:
        return
    
    request = get_current_request()
    user = getattr(request, 'user', None) if request else None
    
    # Skip if no user (system operations)
    if not user or not user.is_authenticated:
        return
    
    create_audit_log(user, 'DELETE', instance)

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login events"""
    # Create a mock instance for login event
    class LoginEvent:
        def __init__(self, user):
            self.pk = user.pk
            self.user = user
        
        def __str__(self):
            return f"Login: {self.user.username}"
        
        class __class__:
            __name__ = 'UserLogin'
    
    login_instance = LoginEvent(user)
    ip_address = get_client_ip(request)
    
    AuditLog.objects.create(
        user=user,
        ip_address=ip_address,
        action='LOGIN',
        model_name='UserLogin',
        object_id=str(user.pk),
        object_repr=f"Login: {user.username}",
        changes=None
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout events"""
    if not user:
        return
    
    # Create a mock instance for logout event
    class LogoutEvent:
        def __init__(self, user):
            self.pk = user.pk
            self.user = user
        
        def __str__(self):
            return f"Logout: {self.user.username}"
        
        class __class__:
            __name__ = 'UserLogout'
    
    logout_instance = LogoutEvent(user)
    ip_address = get_client_ip(request)
    
    AuditLog.objects.create(
        user=user,
        ip_address=ip_address,
        action='LOGOUT',
        model_name='UserLogout',
        object_id=str(user.pk),
        object_repr=f"Logout: {user.username}",
        changes=None
    )
