# ============================================================
# views_admin.py
# Vistas exclusivas del panel administrativo del sistema.
# Solo usuarios con permisos de staff pueden acceder.
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Producto, Categoria, Pedido, Mesa
from .forms import FormProducto, FormCategoria, FormPedidoEstado

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from menu.models import Perfil

# ============================================================
# DECORADOR PARA PERMITIR SOLO ADMINISTRADORES (is_staff == True)
# ============================================================
def admin_required(view_func):
    """
    Decorador personalizado que permite acceso solo
    a usuarios administradores (is_staff=True).
    """
    return user_passes_test(lambda u: u.is_staff, login_url='/login/')(view_func)


# ============================================================
# DASHBOARD PRINCIPAL DEL ADMINISTRADOR
# ============================================================
@admin_required
def admin_home(request):
    """
    Dashboard general del administrador.
    Muestra conteos de clientes, productos, categorías y pedidos.
    """
    contexto = {
        'clientes': User.objects.count(),
        'productos': Producto.objects.count(),
        'categorias': Categoria.objects.count(),
        'pedidos': Pedido.objects.count(),
    }
    return render(request, 'menu/admin_panel/home.html', contexto)


# ============================================================
# PRODUCTOS — LISTA
# ============================================================
@admin_required
def producto_lista(request):
    """
    Lista todos los productos registrados en el sistema.
    """
    productos = Producto.objects.all()
    return render(request, 'menu/admin_panel/producto_lista.html', {'productos': productos})


# ============================================================
# PRODUCTOS — AGREGAR
# ============================================================
@admin_required
def producto_agregar(request):
    """
    Formulario para agregar un nuevo producto.
    Incluye imagen, precio, categoría, descripción, etc.
    """
    if request.method == 'POST':
        form = FormProducto(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto agregado correctamente.")
            return redirect('producto_lista')
    else:
        form = FormProducto()

    return render(request, 'menu/admin_panel/producto_form.html', {
        'form': form,
        'titulo': 'Agregar Producto',
        'producto': {},
        'categorias': Categoria.objects.all()
    })


# ============================================================
# PRODUCTOS — EDITAR
# ============================================================
@admin_required
def producto_editar(request, producto_id):
    """
    Edita los datos de un producto existente.
    """
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = FormProducto(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect('producto_lista')

    else:
        form = FormProducto(instance=producto)

    return render(request, 'menu/admin_panel/producto_form.html', {
        'form': form,
        'titulo': 'Editar Producto',
        'producto': producto,
        'categorias': Categoria.objects.all()
    })


# ============================================================
# PRODUCTOS — ELIMINAR
# ============================================================
@admin_required
def producto_eliminar(request, producto_id):
    """
    Elimina un producto y muestra una pantalla de confirmación.
    """
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        producto.delete()
        messages.error(request, "Producto eliminado.")
        return redirect('producto_lista')

    return render(request, 'menu/admin_panel/producto_eliminar.html', {'producto': producto})


# ============================================================
# CATEGORÍAS — LISTA
# ============================================================
@admin_required
def categoria_lista(request):
    """
    Lista todas las categorías existentes.
    """
    categorias = Categoria.objects.all()
    return render(request, 'menu/admin_panel/categoria_lista.html', {'categorias': categorias})


# ============================================================
# CATEGORÍAS — AGREGAR
# ============================================================
@admin_required
def categoria_agregar(request):
    """
    Formulario para crear una nueva categoría.
    """
    if request.method == 'POST':
        form = FormCategoria(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría agregada con éxito.")
            return redirect('categoria_lista')
    else:
        form = FormCategoria()

    return render(request, 'menu/admin_panel/categoria_form.html', {
        'form': form,
        'titulo': 'Agregar Categoría',
        'categoria': {}
    })


# ============================================================
# CATEGORÍAS — EDITAR
# ============================================================
@admin_required
def categoria_editar(request, categoria_id):
    """
    Edita una categoría existente.
    """
    categoria = get_object_or_404(Categoria, id=categoria_id)

    if request.method == 'POST':
        form = FormCategoria(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada.")
            return redirect('categoria_lista')

    else:
        form = FormCategoria(instance=categoria)

    return render(request, 'menu/admin_panel/categoria_form.html', {
        'form': form,
        'titulo': 'Editar Categoría',
        'categoria': categoria
    })


# ============================================================
# CATEGORÍAS — ELIMINAR
# ============================================================
@admin_required
def categoria_eliminar(request, categoria_id):
    """
    Confirmación y eliminación de una categoría.
    """
    categoria = get_object_or_404(Categoria, id=categoria_id)

    if request.method == 'POST':
        categoria.delete()
        messages.error(request, "Categoría eliminada.")
        return redirect('categoria_lista')

    return render(request, 'menu/admin_panel/categoria_eliminar.html', {'categoria': categoria})


# ============================================================
# CLIENTES — LISTA
# ============================================================
@admin_required
def cliente_lista(request):
    """
    Lista todos los clientes registrados.
    (Solo los que NO son staff.)
    """
    clientes = User.objects.filter(is_staff=False)
    return render(request, 'menu/admin_panel/cliente_lista.html', {'clientes': clientes})


# ============================================================
# CLIENTES — ELIMINAR
# ============================================================
@admin_required
def cliente_eliminar(request, cliente_id):
    """
    Elimina un cliente del sistema.
    """
    cliente = get_object_or_404(User, id=cliente_id)

    if request.method == 'POST':
        cliente.delete()
        messages.error(request, "Cliente eliminado.")
        return redirect('cliente_lista')

    return render(request, 'menu/admin_panel/cliente_eliminar.html', {'cliente': cliente})


# ============================================================
# PEDIDOS — LISTA
# ============================================================
@admin_required
def pedido_lista(request):
    """
    Lista todos los pedidos, ordenados por fecha descendente.
    """
    pedidos = Pedido.objects.order_by('-fecha')
    return render(request, 'menu/admin_panel/pedido_lista.html', {'pedidos': pedidos})


# ============================================================
# PEDIDOS — DETALLE Y CAMBIO DE ESTADO
# ============================================================
@admin_required
def pedido_detalle(request, pedido_id):
    """
    Muestra los detalles del pedido y permite cambiar su estado.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        form = FormPedidoEstado(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Estado del pedido #{pedido.id} actualizado correctamente.")
            return redirect('pedido_lista')  # ⬅️ Redirige a la lista general de pedidos


    else:
        form = FormPedidoEstado(instance=pedido)

    return render(request, 'menu/admin_panel/pedido_detalle.html', {
        'pedido': pedido,
        'form': form
    })


# ============================================================
# REPORTES — VENTAS
# ============================================================
@admin_required
def reporte_ventas(request):
    """
    Muestra todas las ventas entregadas y calcula total general.
    """
    ventas = Pedido.objects.filter(estatus="entregado")
    total_general = sum(v.total for v in ventas)

    return render(request, 'menu/admin_panel/reporte_ventas.html', {
        'ventas': ventas,
        'total_general': total_general
    })

# Solo accesible para administradores
@user_passes_test(lambda u: u.is_staff)
def perfil_admin(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user, defaults={"rol": "admin"})

    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        nueva_foto = request.FILES.get("foto")
        nuevo_avatar = request.POST.get("avatar_default")
        nueva_contra = request.POST.get("password")
        nuevo_telefono = request.POST.get("telefono")

        # ✅ Guardar teléfono
        perfil.telefono = nuevo_telefono

        # ✅ Guardar nueva foto
        if nueva_foto:
            perfil.foto = nueva_foto
            perfil.avatar_default = None  # quitar avatar

        # ✅ Guardar avatar si seleccionó uno
        elif nuevo_avatar:
            perfil.avatar_default = nuevo_avatar
            perfil.foto = None  # quitar foto

        # ✅ Si no tiene ni foto ni avatar, asignar uno por defecto
        elif not perfil.foto and not perfil.avatar_default:
            perfil.avatar_default = "imagen01.png"

        # ✅ Cambiar contraseña si se escribió
        if nueva_contra:
            user.set_password(nueva_contra)
            user.save()
            update_session_auth_hash(request, user)

        user.save()
        perfil.save()

        messages.success(request, "✅ Perfil del administrador actualizado correctamente.")
        return redirect("perfil_admin")

    return render(request, "menu/admin_panel/perfil_admin.html", {"perfil": perfil})


from django.http import JsonResponse

@admin_required
def mesa_lista(request):
    mesas = Mesa.objects.all().order_by('numero')

    if request.method == 'POST':
        mesa_id = request.POST.get('mesa_id')
        if mesa_id:
            mesa = Mesa.objects.get(id=mesa_id)
            mesa.ocupada = not mesa.ocupada
            mesa.save()
            return JsonResponse({'success': True, 'ocupada': mesa.ocupada})
        else:
            return JsonResponse({'success': False, 'error': 'Mesa no encontrada'})

    return render(request, 'menu/admin_panel/mesa_lista.html', {'mesas': mesas})
