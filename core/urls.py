from django.urls import path
from . import views
from . import views_ssl
from . import views_audit

app_name = 'core'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='DashboardView'),
    path('servers/', views.ServerListView.as_view(), name='server-list'),
    path('servers/<int:pk>/', views.ServerDetailView.as_view(), name='server-detail'),
    path('servers/add/', views.ServerCreateView.as_view(), name='server-create'),
    path('servers/<int:pk>/update/', views.ServerUpdateView.as_view(), name='server-update'),
    path('updates/add/', views.ServerUpdateCreateView.as_view(), name='update-create'),
    path('services/add/', views.ServiceCreateView.as_view(), name='service-create'),
    path('services/<int:pk>/update/', views.ServiceUpdateView.as_view(), name='service-update'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service-delete'),
    path('servers/urls/', views.HyperLinkCreateView.as_view(), name='server-urls'),
    path('servers/urls/<int:pk>/', views.HyperLinkDetailView.as_view(), name='server-urls-detail'),
    path('servers/urls/<int:pk>/update/', views.HyperLinkUpdateView.as_view(), name='server-urls-update'),
    path('servers/urls/<int:pk>/delete/', views.HyperLinkDeleteView.as_view(), name='server-urls-delete'),
    path('servers/urls/all/', views.HyperLinkListView.as_view(), name='server-urls-list'),  # Add this line
    
    # Host-VM URLs
    path('hosts/', views.HostVMListView.as_view(), name='host-vm-list'),
    path('hosts/<int:pk>/', views.HostDetailView.as_view(), name='host-detail'),
    path('hosts/add/', views.HostCreateView.as_view(), name='host-create'),
    path('hosts/<int:pk>/update/', views.HostUpdateView.as_view(), name='host-update'),
    path('vms/add/', views.VMCreateView.as_view(), name='vm-create'),
    path('vms/<int:pk>/', views.VMDetailView.as_view(), name='vm-detail'),
    path('vms/<int:pk>/update/', views.VMUpdateView.as_view(), name='vm-update'),
    # Add VM to specific host
    path('hosts/<int:host_id>/vms/add/', views.VMCreateView.as_view(), name='host-vm-create'),
    
    # SSL Certificate URLs
    path('ssl/certificates/', views_ssl.SSLCertificateListView.as_view(), name='ssl-certificate-list'),
    path('ssl/certificates/<int:pk>/', views_ssl.SSLCertificateDetailView.as_view(), name='ssl-certificate-detail'),
    path('ssl/check/<int:pk>/', views_ssl.CheckSSLCertificateView.as_view(), name='check-ssl-certificate'),
    path('ssl/run-check/', views_ssl.RunSSLCheckView.as_view(), name='run-ssl-check'),
    path('ssl/api/check/', views_ssl.SSLCertificateAPIView.as_view(), name='ssl-api-check'),
    # Audit Log URLs
    path('audit-logs/', views_audit.AuditLogListView.as_view(), name='audit-log-list'),
    path('audit-logs/export/', views_audit.export_audit_logs_csv, name='audit-log-export'),
]