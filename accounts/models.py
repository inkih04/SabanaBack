from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)  # Campo adicional para biografía

    def __str__(self):
        return self.username
