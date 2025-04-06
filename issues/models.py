from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from colorfield.fields import ColorField

class Status(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    color = ColorField(default='#FFFFFF')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super(Status, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Priorities(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color = ColorField(default="#FFFFFF")

    def __str__(self):
        return self.nombre


class Types(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color = ColorField(default="#FFFFFF")

    def __str__(self):
        return self.nombre


class Severities(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color = ColorField(default="#FFFFFF")

    def __str__(self):
        return self.nombre


class Issue(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('ready_for_test', 'Ready for Test'),
    ]

    subject = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.subject
