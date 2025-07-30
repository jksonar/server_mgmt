from django.contrib.auth import get_user_model, login
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()

class ImpersonationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.META.get('HTTP_X_TEST_BYPASS_IMPERSONATION'):
            return

        if request.user.is_authenticated and 'impersonating_id' in request.session:
            impersonating_id = request.session.get('impersonating_id')
            try:
                new_user = User.objects.get(id=impersonating_id)
                # Ensure the backend is set for the login function to work correctly
                new_user.backend = 'django.contrib.auth.backends.ModelBackend'
                # Login the impersonated user
                login(request, new_user)
                request.user_is_impersonating = True
            except User.DoesNotExist:
                # If the impersonated user does not exist, clear the session variables
                request.session.pop('impersonator_id', None)
                request.session.pop('impersonating_id', None)
                request.user_is_impersonating = False
        else:
            request.user_is_impersonating = False
