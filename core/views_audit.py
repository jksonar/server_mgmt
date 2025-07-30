import csv
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import AuditLog
from accounts.mixins import RoleBasedAccessMixin

class AuditLogListView(RoleBasedAccessMixin, ListView):
    """View for displaying audit logs with filtering and pagination"""
    model = AuditLog
    template_name = 'core/audit_log.html'
    context_object_name = 'audit_logs'
    paginate_by = 50
    allowed_roles = ['admin']  # Only admin can view audit logs
    
    def get_queryset(self):
        user = self.request.user
        queryset = AuditLog.objects.select_related('user').all()

        # Admins and Superusers can see all audit logs
        if not (user.is_superuser or user.is_admin()):
            # Non-admins/superusers can only see logs related to their departments
            user_departments = user.departments.all()
            if not user_departments.exists():
                return AuditLog.objects.none() # No departments, no logs

            # Build a Q object for department-based filtering
            department_q = Q()

            # Filter for Server-related logs
            server_ids = Server.objects.filter(department__in=user_departments).values_list('id', flat=True)
            if server_ids.exists():
                department_q |= Q(model_name='Server', object_id__in=server_ids)
                department_q |= Q(model_name='Service', object_id__in=Service.objects.filter(server__id__in=server_ids).values_list('id', flat=True))
                department_q |= Q(model_name='HyperLink', object_id__in=HyperLink.objects.filter(servers__id__in=server_ids).values_list('id', flat=True))

            # Filter for Host-related logs
            host_ids = Host.objects.filter(department__in=user_departments).values_list('id', flat=True)
            if host_ids.exists():
                department_q |= Q(model_name='Host', object_id__in=host_ids)
                department_q |= Q(model_name='VirtualMachine', object_id__in=VirtualMachine.objects.filter(host__id__in=host_ids).values_list('id', flat=True))
            
            # Filter for Department-related logs (only for departments the user belongs to)
            department_q |= Q(model_name='Department', object_id__in=user_departments.values_list('id', flat=True))

            # Apply the department filter to the queryset
            queryset = queryset.filter(department_q)

        # Apply existing filters
        user_filter = self.request.GET.get('user')
        if user_filter:
            queryset = queryset.filter(
                Q(user__username__icontains=user_filter) |
                Q(user__first_name__icontains=user_filter) |
                Q(user__last_name__icontains=user_filter)
            )

        action_filter = self.request.GET.get('action')
        if action_filter:
            queryset = queryset.filter(action=action_filter)

        model_filter = self.request.GET.get('model')
        if model_filter:
            queryset = queryset.filter(model_name__icontains=model_filter)

        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)

        ip_filter = self.request.GET.get('ip_address')
        if ip_filter:
            queryset = queryset.filter(ip_address__icontains=ip_filter)

        return queryset.order_by('-timestamp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['action_choices'] = AuditLog.ACTION_CHOICES
        context['current_filters'] = {
            'user': self.request.GET.get('user', ''),
            'action': self.request.GET.get('action', ''),
            'model': self.request.GET.get('model', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'ip_address': self.request.GET.get('ip_address', ''),
        }
        
        # Get unique model names for filter dropdown
        context['model_choices'] = AuditLog.objects.values_list('model_name', flat=True).distinct().order_by('model_name')
        
        return context

@staff_member_required
def export_audit_logs_csv(request):
    """Export audit logs to CSV"""
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
    
    writer = csv.writer(response)
    
    # Write CSV header
    writer.writerow([
        'Timestamp', 'User', 'IP Address', 'Action', 'Model', 
        'Object ID', 'Object Representation', 'Changes'
    ])
    
    # Apply the same filters as the list view
    user = request.user
    queryset = AuditLog.objects.select_related('user').all()

    # Admins and Superusers can see all audit logs
    if not (user.is_superuser or user.is_admin()):
        # Non-admins/superusers can only see logs related to their departments
        user_departments = user.departments.all()
        if not user_departments.exists():
            return AuditLog.objects.none() # No departments, no logs

        # Build a Q object for department-based filtering
        department_q = Q()

        # Filter for Server-related logs
        server_ids = Server.objects.filter(department__in=user_departments).values_list('id', flat=True)
        if server_ids.exists():
            department_q |= Q(model_name='Server', object_id__in=server_ids)
            department_q |= Q(model_name='Service', object_id__in=Service.objects.filter(server__id__in=server_ids).values_list('id', flat=True))
            department_q |= Q(model_name='HyperLink', object_id__in=HyperLink.objects.filter(servers__id__in=server_ids).values_list('id', flat=True))

        # Filter for Host-related logs
        host_ids = Host.objects.filter(department__in=user_departments).values_list('id', flat=True)
        if host_ids.exists():
            department_q |= Q(model_name='Host', object_id__in=host_ids)
            department_q |= Q(model_name='VirtualMachine', object_id__in=VirtualMachine.objects.filter(host__id__in=host_ids).values_list('id', flat=True))
        
        # Filter for Department-related logs (only for departments the user belongs to)
        department_q |= Q(model_name='Department', object_id__in=user_departments.values_list('id', flat=True))

        # Apply the department filter to the queryset
        queryset = queryset.filter(department_q)

    # Filter by user
    user_filter = request.GET.get('user')
    if user_filter:
        queryset = queryset.filter(
            Q(user__username__icontains=user_filter) |
            Q(user__first_name__icontains=user_filter) |
            Q(user__last_name__icontains=user_filter)
        )

    # Filter by action
    action_filter = request.GET.get('action')
    if action_filter:
        queryset = queryset.filter(action=action_filter)

    # Filter by model
    model_filter = request.GET.get('model')
    if model_filter:
        queryset = queryset.filter(model_name__icontains=model_filter)

    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        queryset = queryset.filter(timestamp__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(timestamp__date__lte=date_to)

    # Filter by IP address
    ip_filter = request.GET.get('ip_address')
    if ip_filter:
        queryset = queryset.filter(ip_address__icontains=ip_filter)

    # Write data rows
    for log in queryset.order_by('-timestamp'):
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.username if log.user else 'System',
            log.ip_address or '',
            log.get_action_display(),
            log.model_name,
            log.object_id or '',
            log.object_repr or '',
            str(log.changes) if log.changes else ''
        ])
    
    return response
