import os
import secrets

import requests
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.files.base import ContentFile
from allauth.socialaccount.models import SocialAccount

@receiver(user_logged_in)
def update_avatar_on_login(sender, request, user, **kwargs):
    """
    Descarga y guarda el avatar sólo si es la primera vez que el usuario inicia sesión.
    """
    print("Entrando a la señal de login")
    try:
        # Asegúrate de que el perfil exista
        profile = user.profile

        # Si el usuario ya tiene avatar asignado, no hacemos nada.
        if profile.avatar:
            print(f"El usuario {user.username} ya tiene un avatar registrado: {profile.avatar.name}")
            return

        # Buscar la cuenta social de Google asociada al usuario
        social_account = SocialAccount.objects.filter(user=user, provider='google').first()
        if social_account:
            extra_data = social_account.extra_data
            picture_url = extra_data.get('picture')
            if picture_url:
                response = requests.get(picture_url)
                if response.status_code == 200:
                    # Define el nombre del archivo; podría personalizarse
                    file_name = f"{user.username}_google_avatar.jpg"
                    print("Storage usado para avatar:", profile.avatar.storage)
                    profile.avatar.save(file_name, ContentFile(response.content), save=True)
                    print(f"Avatar de {user.username} actualizado en S3 como {file_name}")
                else:
                    print(f"No se pudo descargar el avatar, status code: {response.status_code}")
            else:
                print("No se encontró URL de avatar en los datos extra de Google.")
        else:
            print("El usuario no tiene cuenta social de Google vinculada.")
    except Exception as e:
        print(f"Error al actualizar el avatar en login: {e}")


@receiver(user_logged_in)
def ensure_api_token(sender, user, request, **kwargs):
    profile = user.profile
    if not profile.api_token:
        print("Token generado")
        # Genera un token de 40 hexadecimales
        profile.api_token = secrets.token_hex(20)
        profile.save()



