from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    ''''''
    
    def create_user(self, email, password = None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório")
        
        email = self.normalize_email(email)
        
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save()
        
        return user

    def create_superuser(self, email, password = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    '''Class for modeling custom user model. Extends `AbstractUser`.'''

    username = None
    email = models.EmailField(_('email address'), unique = True)

    user_permissions = models.ManyToManyField(
        Permission,
        related_name = 'customuser_permissions_set',
        blank = True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()