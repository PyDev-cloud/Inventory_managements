from django.contrib.auth.models import BaseUserManager


class BaseManager(BaseUserManager):
    def create_user(self,email,username,password,**extra_fields):
        if not username:
            raise "UserName is not valid "
        if not email:
            raise "Email is not valid "
        
        email=self.normalize_email(email)
        User=self.model(
            username=username,
            email=email,
            **extra_fields
        )
        password=User.set_password(password)
        self.save(using=self._db)
        return (User)
    

    def super_user(self,username,password,email,**extra_fields):
        User=self.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        User.is_staff=True
        User.is_superuser=True
        User.is_active=True

        self.save(using=self._db)
        return(User)