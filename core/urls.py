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
]