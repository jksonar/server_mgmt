from django.contrib import admin
from .models import Server, ServerUpdate, Service, AuditLog
# Register your models here.
admin.site.register(Server)
admin.site.register(ServerUpdate)
admin.site.register(Service)
admin.site.register(AuditLog)