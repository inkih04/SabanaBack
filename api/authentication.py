from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from issues.models import Profile  # Ajusta la importación según tu estructura


class CustomAuthorizationHeaderTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        token = auth_header.strip()

        if not token:
            return None

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        try:
            # Encuentra el perfil con el token correspondiente
            profile = Profile.objects.get(api_token=token)
            user = profile.user

            # Verifica si el usuario está activo
            if not user.is_active:
                raise AuthenticationFailed('Usuario inactivo o eliminado')

            return (user, token)
        except Profile.DoesNotExist:
            raise AuthenticationFailed('Token inválido')

    # Añade este método
    def get_scheme_name(self):
        return 'ApiToken'