from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
import logging

from core.models import HyperLink, SSLCertificate
from core.utils.ssl_checker import get_ssl_expiry_date, check_url_accessibility

logger = logging.getLogger(__name__)

@shared_task
def check_ssl_certificates():
    """
    Check SSL certificates for all hyperlinks and update their expiry information.
    """
    hyperlinks = HyperLink.objects.filter(is_enabled=True)
    updated_count = 0
    error_count = 0
    
    for hyperlink in hyperlinks:
        try:
            # Check if URL is accessible
            is_accessible = check_url_accessibility(hyperlink.url)
            
            if not is_accessible:
                logger.warning(f"URL {hyperlink.url} is not accessible")
                continue
            
            # Get SSL certificate information
            expiry_date, issuer, subject, is_valid = get_ssl_expiry_date(hyperlink.url)
            
            # Update or create SSL certificate record
            ssl_cert, created = SSLCertificate.objects.update_or_create(
                hyperlink=hyperlink,
                defaults={
                    'expiry_date': expiry_date,
                    'issuer': issuer or '',
                    'subject': subject or '',
                    'is_valid': is_valid,
                    'notification_status': 'pending' if expiry_date and expiry_date > timezone.now() else 'expired'
                }
            )
            
            updated_count += 1
            
        except Exception as e:
            logger.error(f"Error checking SSL for {hyperlink.url}: {str(e)}")
            error_count += 1
    
    return f"Updated {updated_count} SSL certificates, {error_count} errors"

@shared_task
def send_ssl_expiry_notifications():
    """
    Send notifications for SSL certificates that are about to expire.
    """
    notification_days = settings.SSL_NOTIFICATION_DAYS
    notification_sent_count = 0
    
    for days in notification_days:
        # Calculate the date range for this notification period
        target_date = timezone.now() + timedelta(days=days)
        
        # Find certificates expiring on this date (within 24 hours)
        expiring_certs = SSLCertificate.objects.filter(
            notification_status='pending',
            expiry_date__gte=target_date,
            expiry_date__lt=target_date + timedelta(days=1)
        )
        
        for cert in expiring_certs:
            try:
                # Get server and department information
                hyperlink = cert.hyperlink
                server = hyperlink.servers
                department = server.department
                
                # Determine recipients (server owner and department admins)
                recipients = []
                if server.owner and server.owner.email:
                    recipients.append(server.owner.email)
                
                if department:
                    department_admins = department.admins.all()
                    for admin in department_admins:
                        if admin.email and admin.email not in recipients:
                            recipients.append(admin.email)
                
                if not recipients:
                    logger.warning(f"No recipients found for SSL notification: {cert}")
                    continue
                
                # Prepare email content
                subject = f"SSL Certificate Expiring in {days} days: {hyperlink.url}"
                context = {
                    'server_name': server.name,
                    'url': hyperlink.url,
                    'days': days,
                    'expiry_date': cert.expiry_date,
                    'issuer': cert.issuer,
                }
                
                html_message = render_to_string('emails/ssl_expiry_notification.html', context)
                plain_message = render_to_string('emails/ssl_expiry_notification.txt', context)
                
                # Send email
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipients,
                    html_message=html_message,
                    fail_silently=False,
                )
                
                # Update notification status
                cert.notification_status = 'notified'
                cert.save(update_fields=['notification_status'])
                
                notification_sent_count += 1
                
            except Exception as e:
                logger.error(f"Error sending SSL notification for {cert}: {str(e)}")
    
    return f"Sent {notification_sent_count} SSL expiry notifications"

@shared_task
def update_expired_certificates():
    """
    Update the status of expired certificates.
    """
    now = timezone.now()
    expired_count = SSLCertificate.objects.filter(
        expiry_date__lt=now,
        notification_status__in=['pending', 'notified']
    ).update(notification_status='expired', is_valid=False)
    
    return f"Updated {expired_count} expired SSL certificates"