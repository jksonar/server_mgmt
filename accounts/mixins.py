from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404
from core.models import Server, Host, VirtualMachine, HyperLink, SSLCertificate

class RoleBasedAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    A mixin that provides role-based access control for views.
    It checks if the user has the appropriate permissions based on their group membership.
    
    - Admin: Full access to all servers
    - Manager: Edit/view access to servers in their departments
    - Viewer: View-only access to servers in their departments
    """
    
    def test_func(self):
        # Superusers always have access
        if self.request.user.is_superuser:
            return True
            
        # Check if user is in Admin group
        if self.request.user.groups.filter(name='Admin').exists():
            return True
            
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
                
            # Check if user's department matches the object's department
            if department and department in self.request.user.departments.all():
                # Check if user is in Manager group and the action is allowed
                if self.request.user.groups.filter(name='Manager').exists():
                    # For create/update/delete views, check if the user has permission
                    if self.__class__.__name__.endswith(('CreateView', 'UpdateView')):
                        return True
                    elif self.__class__.__name__.endswith('DeleteView'):
                        # Managers cannot delete objects
                        return False
                    else:  # For detail/list views
                        return True
                        
                # Check if user is in Viewer group and this is a read-only view
                elif self.request.user.groups.filter(name='Viewer').exists():
                    # Viewers can only access detail and list views
                    return self.__class__.__name__.endswith(('DetailView', 'ListView'))
        
        # For list views without a specific object
        elif self.__class__.__name__.endswith('ListView'):
            # Both Managers and Viewers can access list views
            # The queryset will be filtered by department in get_queryset
            return self.request.user.groups.filter(name__in=['Manager', 'Viewer']).exists()
        
        # For create views without a specific object (e.g., adding a new server)
        elif self.__class__.__name__.endswith('CreateView'):
            # Only Admins and Managers can create new objects
            return self.request.user.groups.filter(name='Manager').exists()
            
        return False

    def get_queryset(self):
        """
        Filter the queryset based on the user's role and departments.
        """
        queryset = super().get_queryset()
        
        # Superusers and Admins can see all objects
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists():
            return queryset
            
        # Filter objects by user's departments for Managers and Viewers
        model = queryset.model
        
        if model == Server or model == Host:
            return queryset.filter(department__in=self.request.user.departments.all())
        elif model == VirtualMachine:
            return queryset.filter(host__department__in=self.request.user.departments.all())
        elif model == HyperLink:
            return queryset.filter(servers__department__in=self.request.user.departments.all())
        elif model == SSLCertificate:
            return queryset.filter(hyperlink__servers__department__in=self.request.user.departments.all())
            
        return queryset