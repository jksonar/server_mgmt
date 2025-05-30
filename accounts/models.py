from django.db import models
from django.contrib.auth.models import AbstractUser, Group

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    # Replace single department field with many-to-many relationship
    departments = models.ManyToManyField(Department, blank=True, related_name='users')
    
    def __str__(self):
        return self.username
    
    def is_admin(self):
        """Check if user is in the Admin group"""
        return self.groups.filter(name='Admin').exists() or self.is_superuser
    
    def is_manager(self):
        """Check if user is in the Manager group"""
        return self.groups.filter(name='Manager').exists()
    
    def is_viewer(self):
        """Check if user is in the Viewer group"""
        return self.groups.filter(name='Viewer').exists()
    
    def get_role(self):
        """Get the user's highest role"""
        if self.is_superuser or self.is_admin():
            return 'Admin'
        elif self.is_manager():
            return 'Manager'
        elif self.is_viewer():
            return 'Viewer'
        else:
            return 'No Role'
