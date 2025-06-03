from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404
from core.models import Server, Host, VirtualMachine, HyperLink, SSLCertificate

class RoleBasedAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """    
    A mixin that provides role-based access control for views.
    It checks if the user has the appropriate permissions based on their group membership.
    
    - Admin: Full access to all features and modules
    - Manager: Edit/view access to resources in their departments
    - Viewer: View-only access to resources in their departments
    """
    
    # List of allowed roles for the view
    allowed_roles = ['admin', 'manager', 'viewer']
    
    def test_func(self):
        user = self.request.user
        
        # Superusers always have access
        if user.is_superuser:
            return True
            
        # Check if user is in Admin group - Admin has full access to everything
        if user.is_admin():
            return True
            
        # Check if the user's role is allowed for this view
        if not any(getattr(user, f'is_{role}')() for role in self.allowed_roles):
            return False
            
        # For SSL Certificate views - Viewers have view-only access
        if user.is_viewer() and (getattr(self, 'model', None) == SSLCertificate or 
                                 self.__module__ == 'core.views_ssl'):
            # Allow access only to DetailView and ListView for Viewers
            return self.__class__.__name__.endswith(('DetailView', 'ListView'))
            
        # For object-specific views
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            
            # Get the department based on object type
            department = None
            if isinstance(obj, Server):
                department = obj.department
            elif isinstance(obj, Host):
                department = obj.department
            elif isinstance(obj, VirtualMachine):
                department = obj.host.department
            elif isinstance(obj, HyperLink):
                department = obj.servers.department
            elif isinstance(obj, SSLCertificate):
                department = obj.hyperlink.servers.department
                # Viewers have view-only access to SSL certificates
                if user.is_viewer():
                    # Allow access only to DetailView and ListView for Viewers
                    return self.__class__.__name__.endswith(('DetailView', 'ListView'))
                
            # Check if user's department matches the object's department
            if department and department in user.departments.all():
                # Check if user is in Manager group and the action is allowed
                if user.is_manager():
                    # Managers can create, view, update, and delete objects in their departments
                    return True
                        
                # Check if user is in Viewer group and this is a read-only view
                elif user.is_viewer():
                    # Viewers can only access detail and list views
                    return self.__class__.__name__.endswith(('DetailView', 'ListView'))
            else:
                # User doesn't have access to this department
                return False
        
        # For list views without a specific object
        elif self.__class__.__name__.endswith('ListView'):
            # Both Managers and Viewers can access list views
            # The queryset will be filtered by department in get_queryset
            return user.is_manager() or user.is_viewer()
        
        # For create views without a specific object (e.g., adding a new server)
        elif self.__class__.__name__.endswith('CreateView'):
            # Only Admins and Managers can create new objects
            return user.is_manager()
            
        return False

    def get_queryset(self):
        """
        Filter the queryset based on the user's role and departments.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Superusers and Admins can see all objects
        if user.is_superuser or user.is_admin():
            return queryset
            
        # Viewers have view-only access to SSL certificates in their departments
        if user.is_viewer() and queryset.model == SSLCertificate:
            return queryset.filter(hyperlink__servers__department__in=user.departments.all())
            
        # Filter objects by user's departments for Managers and Viewers
        model = queryset.model
        
        if model == Server or model == Host:
            return queryset.filter(department__in=user.departments.all())
        elif model == VirtualMachine:
            return queryset.filter(host__department__in=user.departments.all())
        elif model == HyperLink:
            return queryset.filter(servers__department__in=user.departments.all())
        elif model == SSLCertificate:
            return queryset.filter(hyperlink__servers__department__in=user.departments.all())
            
        return queryset