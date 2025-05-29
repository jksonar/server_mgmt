from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='DashboardView'),
    path('servers/', views.ServerListView.as_view(), name='server-list'),
    path('servers/<int:pk>/', views.ServerDetailView.as_view(), name='server-detail'),
    path('servers/add/', views.ServerCreateView.as_view(), name='server-create'),
    path('servers/<int:pk>/update/', views.ServerUpdateView.as_view(), name='server-update'),
    path('updates/add/', views.ServerUpdateCreateView.as_view(), name='update-create'),
    path('services/add/', views.ServiceCreateView.as_view(), name='service-create'),
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
]