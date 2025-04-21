from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

from django.db.models.signals import post_save
from django.dispatch import receiver
from storages.backends.s3boto3 import S3Boto3Storage

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
    due_date = models.DateField(null=True, blank=True)
    watchers = models.ManyToManyField(User, related_name='watched_issues', blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_issues"
    )
    def __str__(self):
        return self.subject


class Attachment(models.Model):
    issue = models.ForeignKey(Issue, related_name='attachment', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/', storage=S3Boto3Storage())
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')})"



# -------------------------------
# Extensión del modelo User: Profile
# -------------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Campo para guardar la biografía o descripción breve
    biography = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', storage=S3Boto3Storage(), blank=True, null=True)
    api_token = models.CharField(
        max_length=40,
        unique=True,
        blank=True,
        help_text="Token de acceso a la API, se genera al primer login."
    )

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
        return f"Comentario de {self.user.username} en '{self.issue.subject}'"