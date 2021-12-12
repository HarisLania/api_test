from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Permission(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=200)
    permissions = models.ManyToManyField(Permission)

    def __str__(self) -> str:
        return self.name

class User(AbstractUser):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=64, unique=True)
    password = models.CharField(max_length=64)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    # username = None

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.username
    