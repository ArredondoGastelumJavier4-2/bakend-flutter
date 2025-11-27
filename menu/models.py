from django.db import models
from django.contrib.auth.models import User


# -----------------------------
# CATEGORÍA
# -----------------------------
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# -----------------------------
# PRODUCTO
# -----------------------------
class Producto(models.Model):

    ESTADOS = (
        ('activo', 'Activo'),
        ('agotado', 'Agotado'),
    )

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre


# -----------------------------
# PERFIL (EXTENSIÓN DE USER)
# -----------------------------
class Perfil(models.Model):
    ROLES = (
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
    )

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    avatar_default = models.CharField(max_length=20, blank=True, null=True)  # <- antes era foto_default
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.CharField(max_length=10, choices=ROLES, default='cliente')

    def __str__(self):
        return self.usuario.username


# -----------------------------
# PEDIDO
# -----------------------------
class Pedido(models.Model):

    ESTATUS = (
        ('activo', 'Activo'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
    )

    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estatus = models.CharField(max_length=10, choices=ESTATUS, default='activo')
    metodo_pago = models.CharField(max_length=20, blank=True, null=True)  # tarjeta / sucursal

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"


# -----------------------------
# DETALLE DE PEDIDO
# -----------------------------
class PedidoDetalle(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    notas = models.TextField(blank=True, null=True)  # "sin cebolla", etc

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


# -----------------------------
# Mesa
# -----------------------------
class Mesa(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    ocupada = models.BooleanField(default=False)

    def __str__(self):
        return f"Mesa {self.numero} {'(Ocupada)' if self.ocupada else '(Libre)'}"
    

# -----------------------------
# Token
# -----------------------------

from django.conf import settings
from django.db import models
import secrets  # lo usamos para generar tokens seguros


def generate_token():
    """
    Genera un token aleatorio hexadecimal de 40 caracteres.
    Usamos secrets para que sea criptográficamente seguro.
    """
    return secrets.token_hex(20)


class ApiToken(models.Model):
    """
    Token de API para autenticar usuarios desde Flutter u otras apps.
    Un usuario puede tener un token.
    Si quieres que tenga varios, cambia OneToOneField por ForeignKey.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_token"
    )
    key = models.CharField(
        max_length=40,
        unique=True,
        default=generate_token  # se genera automáticamente
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token de {self.user} ({self.key})"


# -----------------------------
# CARRITO (MODELO REAL)
# -----------------------------
class Carrito(models.Model):
    """
    Carrito real asociado a un usuario.
    Un usuario tiene un carrito activo.
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"


# -----------------------------
# ITEMS DEL CARRITO
# -----------------------------
class CarritoItem(models.Model):
    """
    Items dentro del carrito.
    Guarda producto, cantidad, nota opcional.
    """
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    nota = models.TextField(blank=True, null=True)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} × {self.producto.nombre}"