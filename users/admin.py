from django.contrib import admin
from .models import User, Permission, Role
# Register your models here.

admin.site.register(User)
admin.site.register(Permission)
admin.site.register(Role)