from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    # Replace single department field with many-to-many relationship
    departments = models.ManyToManyField(Department, blank=True, related_name='users')
    
    def __str__(self):
        return self.username
