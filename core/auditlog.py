from auditlog.registry import auditlog
from .models import Server, ServerUpdate, Service, HyperLink, Host, VirtualMachine, SSLCertificate

auditlog.register(Server)
auditlog.register(ServerUpdate)
auditlog.register(Service)
auditlog.register(HyperLink)
auditlog.register(Host)
auditlog.register(VirtualMachine)
auditlog.register(SSLCertificate)
