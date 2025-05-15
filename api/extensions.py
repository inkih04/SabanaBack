from drf_spectacular.extensions import OpenApiAuthenticationExtension
from .authentication import CustomAuthorizationHeaderTokenAuthentication

class CustomAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = CustomAuthorizationHeaderTokenAuthentication
    name = 'ApiToken'  # Debe coincidir con el nombre en SECURITY_DEFINITIONS

    def get_security_requirement(self, auto_schema):
        return [{'ApiToken': []}]

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Introduce tu token directamente sin ningún prefijo'
        }