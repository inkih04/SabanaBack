from django.contrib import admin
from .models import Issue, Attachment  # Asegúrate de importar tus modelos

# Registra los modelos para que aparezcan en el admin
admin.site.register(Issue)
admin.site.register(Attachment)
from django.contrib import admin

# Register your models here.
