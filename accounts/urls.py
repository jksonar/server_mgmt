from django.urls import path
from . import views
from . import views_users

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    # Department management
    path('departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department-create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department-update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department-delete'),
    # User management
    path('users/', views_users.UserListView.as_view(), name='user-list'),
    path('users/add/', views_users.UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', views_users.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/edit/', views_users.UserUpdateView.as_view(), name='user-update'),
    path('impersonate/<int:user_id>/', views.impersonate_user, name='impersonate-user'),
    path('impersonate/stop/', views.stop_impersonating, name='stop-impersonating'),
]