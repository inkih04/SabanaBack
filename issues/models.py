from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from storages.backends.s3boto3 import S3Boto3Storage


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
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_issues"
    )
    def __str__(self):
        return self.subject


class Attachment(models.Model):
    issue = models.ForeignKey(Issue, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/', storage=S3Boto3Storage())
    uploaded_at = models.DateTimeField(auto_now_add=True)



# -------------------------------
# Extensión del modelo User: Profile
# -------------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Campo para guardar la biografía o descripción breve
    biography = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', storage=S3Boto3Storage(), blank=True, null=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'


# -------------------------------
# Señales para crear y actualizar el perfil automáticamente
# -------------------------------
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Si ya existe el perfil, lo guarda; en caso contrario, la señal create_user_profile se encargará de crearlo.
    if hasattr(instance, 'profile'):
        instance.profile.save()



class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return {self.issue}