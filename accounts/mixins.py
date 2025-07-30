from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

class RoleBasedAccessMixin(UserPassesTestMixin, AccessMixin):
    allowed_roles = []  # Define roles that can access this view

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not self.test_func():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        user = self.request.user
        
        # Superusers and Admins have full access
        if user.is_superuser or user.is_admin():
            return True

        # Check if the user's role is allowed for this view
        if self.allowed_roles and not any(getattr(user, f'is_{role}')() for role in self.allowed_roles):
            return False

        # For object-level permissions, check if the object's department is in the user's departments
        # This assumes the view has a get_object() method or self.object is set
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            if hasattr(obj, 'department') and obj.department:
                return obj.department in user.departments.all()
            # If the object doesn't have a department or it's null, allow access if no other department restriction applies
            return True
        
        # If it's a list view or create view, and no specific object is being accessed,
        # and the user has an allowed role, grant access.
        return True


class ImpersonationRequiredMixin(AccessMixin):
    """
    Mixin to ensure that a view is only accessible by the original user when impersonating.
    If the user is impersonating, they are redirected to the dashboard with an error message.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user_is_impersonating:
            messages.error(request, "You cannot perform this action while impersonating another user. Please stop impersonating first.")
            return redirect('core:DashboardView')
        return super().dispatch(request, *args, **kwargs)
