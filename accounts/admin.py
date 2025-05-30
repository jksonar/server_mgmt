from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Department, User

# Register Department model
admin.site.register(Department)

# Customize User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_superuser', 'get_role', 'is_active')
    list_filter = ('is_superuser', 'groups', 'is_active', 'departments')
    fieldsets = UserAdmin.fieldsets + (
        ('Departments', {'fields': ('departments',)}),
    )
    filter_horizontal = ('groups', 'user_permissions', 'departments')
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Register User model with custom admin
admin.site.register(User, CustomUserAdmin)