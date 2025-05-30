import ssl
import socket
import OpenSSL
import requests
from datetime import datetime
import logging
from urllib.parse import urlparse
from django.utils import timezone
import pytz

logger = logging.getLogger(__name__)

def get_ssl_expiry_date(url):
    """
    Get the SSL certificate expiry date for a given URL.
    
    Args:
        url (str): The URL to check (can be with or without protocol)
    
    Returns:
        tuple: (expiry_date, issuer, subject, is_valid) or (None, None, None, False) if error
    """
    try:
        # Ensure URL has a protocol
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        
        # Parse the URL to get the hostname
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        
        # Remove port if present
        if ':' in hostname:
            hostname = hostname.split(':')[0]
        
        # Create a connection to the server
        context = ssl.create_default_context()
        conn = socket.create_connection((hostname, 443), timeout=10)
        sock = context.wrap_socket(conn, server_hostname=hostname)
        
        # Get certificate
        cert = sock.getpeercert(binary_form=True)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
        
        # Extract expiry date
        naive_expiry_date = datetime.strptime(x509.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ')
        # Make the expiry date timezone-aware
        expiry_date = timezone.make_aware(naive_expiry_date, timezone.utc)
        
        # Extract issuer and subject
        issuer = dict(x509.get_issuer().get_components())
        issuer_str = ', '.join([f"{k.decode('utf-8')}={v.decode('utf-8')}" for k, v in issuer.items()])
        
        subject = dict(x509.get_subject().get_components())
        subject_str = ', '.join([f"{k.decode('utf-8')}={v.decode('utf-8')}" for k, v in subject.items()])
        
        # Check if certificate is valid using timezone-aware comparison
        is_valid = timezone.now() < expiry_date
        
        sock.close()
        conn.close()
        
        return expiry_date, issuer_str, subject_str, is_valid
    
    except Exception as e:
        logger.error(f"Error checking SSL for {url}: {str(e)}")
        return None, None, None, False

def check_url_accessibility(url):
    """
    Check if a URL is accessible via HTTP request.
    
    Args:
        url (str): The URL to check
    
    Returns:
        bool: True if accessible, False otherwise
    """
    try:
        # Ensure URL has a protocol
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code < 400
    except Exception as e:
        logger.error(f"Error accessing {url}: {str(e)}")
        return False