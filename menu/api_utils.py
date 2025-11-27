# api_utils.py

from django.http import JsonResponse
from .models import ApiToken


def get_user_from_token(request):
    """
    Extrae el token del header Authorization y retorna el usuario correspondiente.
    Este será usado en TODOS los endpoints del API.

    Espera:
    Authorization: Token <token>

    Retorna:
    - usuario (si existe)
    - None (si no existe)
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    # Formato esperado: "Token xxyyzz..."
    if not auth_header.startswith("Token "):
        return None

    token_key = auth_header.replace("Token ", "").strip()

    # Buscamos el token en la BD
    try:
        api_token = ApiToken.objects.get(key=token_key)
        return api_token.user
    except ApiToken.DoesNotExist:
        return None

from .models import Carrito

def get_or_create_carrito(user):
    """
    Obtiene o crea el carrito del usuario.
    """
    carrito, creado = Carrito.objects.get_or_create(usuario=user)
    return carrito
