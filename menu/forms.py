# ============================================================
# forms.py
# Formularios utilizados por el sistema:
# - Registro de clientes
# - Login
# - CRUD de productos
# - CRUD de categorías
# - Cambio de estatus de pedidos
# ============================================================

from django import forms
from django.contrib.auth.models import User
from .models import Producto, Categoria, Pedido


# ============================================================
# FORMULARIO DE REGISTRO (CLIENTE)
# ============================================================
class FormRegistro(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    # Foto subida por el usuario
    foto = forms.ImageField(required=False)

    # Foto predeterminada
    foto_default = forms.ChoiceField(
        required=False,
        choices=[
            ("perfil1.png", "Imagen 1"),
            ("perfil2.png", "Imagen 2"),
            ("perfil3.png", "Imagen 3"),
            ("perfil4.png", "Imagen 4"),
            ("perfil5.png", "Imagen 5"),
        ],
        widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]

    def clean(self):
        data = super().clean()
        password = data.get("password")
        password2 = data.get("password2")

        if password and password2 and password != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")
            
        return data
# ============================================================
# FORMULARIO DE LOGIN
# ============================================================
class FormLogin(forms.Form):
    """
    Formulario simple de login para usuarios.
    """
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")


# ============================================================
# FORMULARIO PARA PRODUCTOS
# ============================================================
class FormProducto(forms.ModelForm):
    """
    Formulario usado por administradores para agregar o editar productos.
    Permite subir imágenes.
    """
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'descripcion', 'precio', 'costo', 'estado', 'imagen']


# ============================================================
# FORMULARIO PARA CATEGORÍAS
# ============================================================
class FormCategoria(forms.ModelForm):
    """
    Formulario para crear o editar categorías de productos.
    """
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']


# ============================================================
# FORMULARIO PARA CAMBIAR ESTATUS DEL PEDIDO
# ============================================================
class FormPedidoEstado(forms.ModelForm):
    """
    Formulario usado en el panel admin para actualizar el estado del pedido.
    """
    class Meta:
        model = Pedido
        fields = ['estatus']

class FormRegistro(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    foto = forms.ImageField(required=False)
    avatar_default = forms.CharField(required=False)

    def clean(self):
        data = super().clean()

        if data.get("password") != data.get("password2"):
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return data