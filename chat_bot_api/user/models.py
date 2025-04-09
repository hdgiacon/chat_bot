from django.db import models
from django.contrib.auth.models import Permission, AbstractUser

class CustomUser(AbstractUser):
    '''Class for modeling custom user model. Extends `AbstractUser`.'''
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name = 'customuser_permissions_set',
        blank = True
    )