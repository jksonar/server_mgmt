from .auditlog import set_current_request

class AuditLogMiddleware:
    """Middleware to capture request context for audit logging"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set the current request in thread-local storage
        set_current_request(request)
        
        response = self.get_response(request)
        
        # Clear the request after processing
        set_current_request(None)
        
        return response