from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

USER_TYPES = [
    ('Superuser', 'Superuser'),
    ('Manager', 'Manager'),
    ('Accounts', 'Accounts'),
    ('Sales_Team', 'Sales Team'),
    ('Employee', 'Employee'),
    ('Customer', 'Customer'),
]

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, user_type='Customer', **extra_fields):
        if not username:
            raise ValueError('Username is required')
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.is_staff = extra_fields.get('is_staff', False)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, user_type='Superuser', **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPES, default='Customer')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    join_date = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['-join_date']

    def __str__(self):
        return f"{self.username} ({self.user_type})"

class RolePermission(models.Model):
    role = models.CharField(max_length=50, choices=USER_TYPES)
    permission = models.CharField(max_length=100)
    allowed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role} | {self.permission} = {self.allowed}"
