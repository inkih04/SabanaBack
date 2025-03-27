from django.db import models
from django.contrib.auth.models import User

class Issue(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('ready_for_test', 'Ready for Test'),
    ]

    subject = models.CharField(max_length=255)  # Campo de texto corto
    description = models.TextField()  # Campo de texto largo
    created_at = models.DateTimeField(auto_now_add=True)  # Se guarda la fecha de creación
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')  # Estado de la issue
    assigned_to = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True  # Usuario asignado
    )

    def __str__(self):
        return self.subject