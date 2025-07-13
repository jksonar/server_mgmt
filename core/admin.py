from django.contrib import admin
from .models import Server, ServerUpdate, Service, HyperLink, SSLCertificate, Host, VirtualMachine, AuditLog

# Register all models
admin.site.register(Server)
admin.site.register(ServerUpdate)
admin.site.register(Service)


@admin.register(HyperLink)
class HyperLinkAdmin(admin.ModelAdmin):
    list_display = ('url', 'servers', 'created_by', 'created_at', 'is_enabled')
    list_filter = ('is_enabled', 'created_at')
    search_fields = ('url', 'servers__name')

@admin.register(SSLCertificate)
class SSLCertificateAdmin(admin.ModelAdmin):
    list_display = ('hyperlink_url', 'expiry_date', 'days_to_expiry', 'status', 'notification_status', 'last_checked')
    list_filter = ('notification_status', 'is_valid')
    search_fields = ('hyperlink__url', 'issuer', 'subject')
    readonly_fields = ('days_to_expiry', 'status', 'status_color')
    
    def hyperlink_url(self, obj):
        return obj.hyperlink.url
    hyperlink_url.short_description = 'URL'

admin.site.register(Host)
admin.site.register(VirtualMachine)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'object_repr', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'model_name', 'object_repr', 'ip_address')
    readonly_fields = ('user', 'ip_address', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent editing of audit logs
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete audit logs
        return request.user.is_superuser