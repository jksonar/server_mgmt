from auditlog.registry import auditlog
from django.contrib.auth.models import Group
from .models import User, Department

auditlog.register(User)
auditlog.register(Group)
auditlog.register(Department)
