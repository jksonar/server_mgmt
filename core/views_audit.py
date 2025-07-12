from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from auditlog.models import LogEntry

@staff_member_required
def audit_log_view(request):
    log_entries = LogEntry.objects.all()
    return render(request, 'core/audit_log.html', {'log_entries': log_entries})
