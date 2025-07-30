from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Server, Service, HyperLink, Host, VirtualMachine, SSLCertificate
from accounts.models import User, Department

def create_user_groups():
    """
    Create the three user groups with appropriate permissions:
    - Admin: Full access to add, edit, delete, and view all servers
    - Manager: Edit and view only assigned servers
    - Viewer: View-only access
    """
    # Get content types for our models
    server_ct = ContentType.objects.get_for_model(Server)
    service_ct = ContentType.objects.get_for_model(Service)
    hyperlink_ct = ContentType.objects.get_for_model(HyperLink)
    host_ct = ContentType.objects.get_for_model(Host)
    vm_ct = ContentType.objects.get_for_model(VirtualMachine)
    ssl_ct = ContentType.objects.get_for_model(SSLCertificate)
    department_ct = ContentType.objects.get_for_model(Department)
    
    # Create Admin group if it doesn't exist
    admin_group, created = Group.objects.get_or_create(name='Admin')
    # Clear existing permissions and add all permissions for server management
    admin_group.permissions.clear()
    admin_permissions = [
        # Server permissions
        Permission.objects.get(content_type=server_ct, codename='add_server'),
        Permission.objects.get(content_type=server_ct, codename='change_server'),
        Permission.objects.get(content_type=server_ct, codename='delete_server'),
        Permission.objects.get(content_type=server_ct, codename='view_server'),
        # Service permissions
        Permission.objects.get(content_type=service_ct, codename='add_service'),
        Permission.objects.get(content_type=service_ct, codename='change_service'),
        Permission.objects.get(content_type=service_ct, codename='delete_service'),
        Permission.objects.get(content_type=service_ct, codename='view_service'),
        # Hyperlink permissions
        Permission.objects.get(content_type=hyperlink_ct, codename='add_hyperlink'),
        Permission.objects.get(content_type=hyperlink_ct, codename='change_hyperlink'),
        Permission.objects.get(content_type=hyperlink_ct, codename='delete_hyperlink'),
        Permission.objects.get(content_type=hyperlink_ct, codename='view_hyperlink'),
        # Host permissions
        Permission.objects.get(content_type=host_ct, codename='add_host'),
        Permission.objects.get(content_type=host_ct, codename='change_host'),
        Permission.objects.get(content_type=host_ct, codename='delete_host'),
        Permission.objects.get(content_type=host_ct, codename='view_host'),
        # VM permissions
        Permission.objects.get(content_type=vm_ct, codename='add_virtualmachine'),
        Permission.objects.get(content_type=vm_ct, codename='change_virtualmachine'),
        Permission.objects.get(content_type=vm_ct, codename='delete_virtualmachine'),
        Permission.objects.get(content_type=vm_ct, codename='view_virtualmachine'),
        # SSL Certificate permissions
        Permission.objects.get(content_type=ssl_ct, codename='add_sslcertificate'),
        Permission.objects.get(content_type=ssl_ct, codename='change_sslcertificate'),
        Permission.objects.get(content_type=ssl_ct, codename='delete_sslcertificate'),
        Permission.objects.get(content_type=ssl_ct, codename='view_sslcertificate'),
        # Department permissions
        Permission.objects.get(content_type=department_ct, codename='add_department'),
        Permission.objects.get(content_type=department_ct, codename='change_department'),
        Permission.objects.get(content_type=department_ct, codename='delete_department'),
        Permission.objects.get(content_type=department_ct, codename='view_department'),
    ]
    admin_group.permissions.add(*admin_permissions)
    
    # Create Manager group if it doesn't exist
    manager_group, created = Group.objects.get_or_create(name='Manager')
    # Clear existing permissions and add manager permissions
    manager_group.permissions.clear()
    manager_permissions = [
        # Server permissions (add, change, view)
        Permission.objects.get(content_type=server_ct, codename='add_server'),
        Permission.objects.get(content_type=server_ct, codename='change_server'),
        Permission.objects.get(content_type=server_ct, codename='view_server'),
        # Service permissions (add, change, view)
        Permission.objects.get(content_type=service_ct, codename='add_service'),
        Permission.objects.get(content_type=service_ct, codename='change_service'),
        Permission.objects.get(content_type=service_ct, codename='view_service'),
        # Hyperlink permissions (add, change, view)
        Permission.objects.get(content_type=hyperlink_ct, codename='add_hyperlink'),
        Permission.objects.get(content_type=hyperlink_ct, codename='change_hyperlink'),
        Permission.objects.get(content_type=hyperlink_ct, codename='view_hyperlink'),
        # Host permissions (add, change, view)
        Permission.objects.get(content_type=host_ct, codename='add_host'),
        Permission.objects.get(content_type=host_ct, codename='change_host'),
        Permission.objects.get(content_type=host_ct, codename='view_host'),
        # VM permissions (add, change, view)
        Permission.objects.get(content_type=vm_ct, codename='add_virtualmachine'),
        Permission.objects.get(content_type=vm_ct, codename='change_virtualmachine'),
        Permission.objects.get(content_type=vm_ct, codename='view_virtualmachine'),
        # SSL Certificate permissions (add, change, view)
        Permission.objects.get(content_type=ssl_ct, codename='add_sslcertificate'),
        Permission.objects.get(content_type=ssl_ct, codename='change_sslcertificate'),
        Permission.objects.get(content_type=ssl_ct, codename='view_sslcertificate'),
        # Department permissions (view only)
        Permission.objects.get(content_type=department_ct, codename='view_department'),
    ]
    manager_group.permissions.add(*manager_permissions)
    
    # Create Viewer group if it doesn't exist
    viewer_group, created = Group.objects.get_or_create(name='Viewer')
    # Clear existing permissions and add viewer permissions
    viewer_group.permissions.clear()
    viewer_permissions = [
        Permission.objects.get(content_type=server_ct, codename='view_server'),
        Permission.objects.get(content_type=service_ct, codename='view_service'),
        Permission.objects.get(content_type=hyperlink_ct, codename='view_hyperlink'),
        Permission.objects.get(content_type=host_ct, codename='view_host'),
        Permission.objects.get(content_type=vm_ct, codename='view_virtualmachine'),
        Permission.objects.get(content_type=ssl_ct, codename='view_sslcertificate'),
        Permission.objects.get(content_type=department_ct, codename='view_department'),
    ]
    viewer_group.permissions.add(*viewer_permissions)
    
    return {
        'admin': admin_group,
        'manager': manager_group,
        'viewer': viewer_group
    }