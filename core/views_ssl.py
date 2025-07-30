from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, View
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import HyperLink, SSLCertificate
from .utils.ssl_checker import get_ssl_expiry_date, check_url_accessibility
from .tasks import check_ssl_certificates
from accounts.mixins import RoleBasedAccessMixin

class SSLCertificateListView(RoleBasedAccessMixin, ListView):
    model = SSLCertificate
    template_name = "ssl/certificate_list.html"
    context_object_name = "certificates"
    allowed_roles = ['admin', 'manager', 'viewer']  # All roles can view certificates
    
    def get_queryset(self):
        user = self.request.user
        # Admin and superuser can see all certificates
        if user.is_superuser or user.is_admin():
            return SSLCertificate.objects.all().select_related('hyperlink', 'hyperlink__servers')
        # Manager and Viewer can only see certificates in their departments
        return SSLCertificate.objects.filter(
            hyperlink__servers__department__in=user.departments.all()
        ).distinct().select_related('hyperlink', 'hyperlink__servers')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group certificates by status
        certificates = self.get_queryset()
        
        context['critical_certs'] = [cert for cert in certificates if cert.status == "Critical"]
        context['warning_certs'] = [cert for cert in certificates if cert.status == "Warning"]
        context['valid_certs'] = [cert for cert in certificates if cert.status == "Valid"]
        context['expired_certs'] = [cert for cert in certificates if cert.status == "Expired"]
        context['unknown_certs'] = [cert for cert in certificates if cert.status == "Unknown"]
        
        return context

class SSLCertificateDetailView(RoleBasedAccessMixin, DetailView):
    model = SSLCertificate
    template_name = "ssl/certificate_detail.html"
    context_object_name = "certificate"
    allowed_roles = ['admin', 'manager', 'viewer']  # All roles can view certificate details

class CheckSSLCertificateView(RoleBasedAccessMixin, View):
    """
    View to manually check an SSL certificate for a hyperlink
    """
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can check SSL certificates
    
    def test_func(self):
        hyperlink_id = self.kwargs.get('pk')
        self.object = get_object_or_404(HyperLink, pk=hyperlink_id) # Set object for RoleBasedAccessMixin to check department
        return super().test_func()
    
    def get(self, request, *args, **kwargs):
        hyperlink_id = self.kwargs.get('pk')
        hyperlink = get_object_or_404(HyperLink, pk=hyperlink_id)
        
        # Check if URL is accessible
        is_accessible = check_url_accessibility(hyperlink.url)
        
        if not is_accessible:
            messages.error(request, f"URL {hyperlink.url} is not accessible")
            return redirect('core:hyperlink-detail', pk=hyperlink_id)
        
        # Get SSL certificate information
        expiry_date, issuer, subject, is_valid = get_ssl_expiry_date(hyperlink.url)
        
        if not expiry_date:
            messages.error(request, f"Could not retrieve SSL certificate information for {hyperlink.url}")
            return redirect('core:hyperlink-detail', pk=hyperlink_id)
        
        # Update or create SSL certificate record
        ssl_cert, created = SSLCertificate.objects.update_or_create(
            hyperlink=hyperlink,
            defaults={
                'expiry_date': expiry_date,
                'issuer': issuer or '',
                'subject': subject or '',
                'is_valid': is_valid,
                'notification_status': 'pending' if expiry_date and expiry_date > timezone.now() else 'expired'
            }
        )
        
        messages.success(request, f"SSL certificate for {hyperlink.url} checked successfully. Expires on {expiry_date.strftime('%Y-%m-%d')}")
        
        # Redirect to certificate detail page
        return redirect('core:ssl-certificate-detail', pk=ssl_cert.pk)

class RunSSLCheckView(RoleBasedAccessMixin, View):
    """
    View to manually trigger the SSL certificate check task
    """
    allowed_roles = ['admin']  # Only Admin can run SSL certificate check task
    
    def test_func(self):
        # The RoleBasedAccessMixin now handles the core role and department checks.
        # We only need to ensure the user has the allowed role.
        return super().test_func()
    
    def get(self, request, *args, **kwargs):
        try:
            # Run the task asynchronously
            task = check_ssl_certificates.delay()
            messages.success(request, f"SSL certificate check task started (Task ID: {task.id})")
        except Exception as e:
            # If Celery is not available, run the task synchronously
            try:
                result = check_ssl_certificates()
                messages.success(request, f"SSL certificate check completed: {result}")
            except Exception as inner_e:
                messages.error(request, f"Error checking SSL certificates: {str(inner_e)}")
        
        return redirect('core:ssl-certificate-list')

class SSLCertificateAPIView(RoleBasedAccessMixin, View):
    """
    API view to get SSL certificate information for a URL
    """
    allowed_roles = ['admin', 'manager']  # Only Admin and Manager can use the SSL certificate API
    def get(self, request, *args, **kwargs):
        url = request.GET.get('url')
        
        if not url:
            return JsonResponse({'error': 'URL parameter is required'}, status=400)
        
        # Check if URL is accessible
        is_accessible = check_url_accessibility(url)
        
        if not is_accessible:
            return JsonResponse({'error': f"URL {url} is not accessible"}, status=400)
        
        # Get SSL certificate information
        expiry_date, issuer, subject, is_valid = get_ssl_expiry_date(url)
        
        if not expiry_date:
            return JsonResponse({'error': f"Could not retrieve SSL certificate information for {url}"}, status=400)
        
        # Return certificate information
        return JsonResponse({
            'url': url,
            'expiry_date': expiry_date.isoformat(),
            'issuer': issuer,
            'subject': subject,
            'is_valid': is_valid,
            'days_to_expiry': (expiry_date - timezone.now()).days
        })