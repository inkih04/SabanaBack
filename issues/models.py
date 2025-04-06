from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Status(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    color = models.CharField(max_length=7, default="#FFFFFF")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super(Status, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Priorities(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#FFFFFF")

    def __str__(self):
        return self.nombre


class Types(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#FFFFFF")

    def __str__(self):
        return self.nombre


class Severities(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#FFFFFF")

    def __str__(self):
        return self.nombre


class Issue(models.Model):

    subject = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(
        Status,on_delete=models.SET_NULL,null=True,blank=True,related_name="issues"
    )
    # Relación con Priorities
    priority = models.ForeignKey(
        Priorities,on_delete=models.SET_NULL,null=True,blank=True,related_name="issues"
    )
    # Relación con Severities
    severity = models.ForeignKey(
        Severities,on_delete=models.SET_NULL,null=True,blank=True,related_name="issues"
    )
    # Relación con Types
    issue_type = models.ForeignKey(
        Types,on_delete=models.SET_NULL,null=True, blank=True,related_name="issues"
    )


    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.subject
