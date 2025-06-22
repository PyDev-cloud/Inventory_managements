from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from .manager import BaseManager
# Create your models here.
User_type={
    ('Manager','Manager'),
    ('Accounts','Accounts'),
    ('Sales_Team','Sales_Team'),
    ('Employee','Employee'),

    ('Admin','Admin')
}
class User(AbstractBaseUser):
    username=models.CharField(max_length=50,validators=[UnicodeUsernameValidator],unique=True)
    email=models.EmailField(max_length=100, unique=True)
    user_type=models.CharField(max_length=50,choices=User_type,default='Student')
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    join_date=models.DateTimeField(auto_now_add=True)
    object=BaseManager()

    USERNAME_FIELD='username'
    REQUIRED_FIELDS=['email',]
    class Meta:
        ordering =['-join_date']