# views_api.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

# MODELOS QUE NECESITAS
from .models import (
    Producto,
    Categoria,
    Mesa,            # 👈 IMPORTANTE
    Carrito,
    CarritoItem,
    Pedido,
    PedidoDetalle,
)

# UTILIDADES DE TOKEN Y CARRITO
from .api_utils import (
    get_user_from_token,
    get_or_create_carrito
)


def api_categorias(request):
    user = get_user_from_token(request)

    if user is None:
        return JsonResponse({"error": "Token inválido o faltante."}, status=401)

    categorias = Categoria.objects.all()

    data = []

    for c in categorias:
        data.append({
            "id": c.id,
            "nombre": c.nombre,
            "descripcion": c.descripcion,
            "imagen": None   # <<<<<<<<<<<<<<<<<<<<<< AQUI SE ARREGLA
        })

    return JsonResponse(data, safe=False)



def api_categoria_detalle(request, categoria_id):
    """
    Devuelve una categoría y sus productos.
    Requiere Token.
    """

    user = get_user_from_token(request)

    if user is None:
        return JsonResponse({"error": "Token inválido."}, status=401)

    try:
        categoria = Categoria.objects.get(pk=categoria_id)
    except Categoria.DoesNotExist:
        return JsonResponse({"error": "Categoría no encontrada."}, status=404)

    productos = Producto.objects.filter(categoria=categoria)

    productos_json = [
        {
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "precio": float(p.precio),
        }
        for p in productos
    ]

    data = {
        "id": categoria.id,
        "nombre": categoria.nombre,
        "descripcion": categoria.descripcion,
        "productos": productos_json
    }

    return JsonResponse(data)


def api_productos(request):
    """
    Devuelve productos.
    - Si viene ?categoria=ID -> solo de esa categoría
    - Si no viene -> todos los productos activos
    Requiere token.
    """
    user = get_user_from_token(request)
    if user is None:
        return JsonResponse({"error": "Token inválido."}, status=401)

    categoria_id = request.GET.get("categoria")

    # Base: solo productos activos
    productos_qs = Producto.objects.filter(estado="activo")

    # Si viene categoria y es un número > 0, filtramos
    if categoria_id and categoria_id.isdigit() and int(categoria_id) > 0:
        productos_qs = productos_qs.filter(categoria_id=int(categoria_id))

    data = [
        {
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "precio": float(p.precio),
            "categoria_id": p.categoria.id,
            # URL ABSOLUTA para que Flutter no vea "file:///media..."
            "imagen": request.build_absolute_uri(p.imagen.url) if p.imagen else None,
        }
        for p in productos_qs
    ]

    return JsonResponse(data, safe=False)

# API DETALLE DE PRODUCTO
def api_producto_detalle(request, producto_id):
    user = get_user_from_token(request)
    if user is None:
        return JsonResponse({"error": "Token inválido."}, status=401)

    try:
        p = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado."}, status=404)

    data = {
        "id": p.id,
        "nombre": p.nombre,
        "descripcion": p.descripcion,
        "precio": float(p.precio),
        "categoria_id": p.categoria.id,
        # 👇 AQUÍ TAMBIÉN
        "imagen": request.build_absolute_uri(p.imagen.url) if p.imagen else None,
    }

    return JsonResponse(data)



def api_carrito_detalle(request):
    user = get_user_from_token(request)
    if user is None:
        return JsonResponse({"error": "Token inválido."}, status=401)

    carrito = get_or_create_carrito(user)

    items_json = []
    total = 0

    for item in carrito.items.all():
        subtotal = float(item.subtotal())
        total += subtotal

        items_json.append({
            "id": item.id,
            "producto_id": item.producto.id,
            "nombre": item.producto.nombre,
            "cantidad": item.cantidad,
            "nota": item.nota,
            "precio_unitario": float(item.precio_unitario),
            "subtotal": subtotal,
            # 👇 IMPORTANTE
            "imagen": request.build_absolute_uri(item.producto.imagen.url)
                      if item.producto.imagen else None,
        })

    return JsonResponse({
        "items": items_json,
        "total": total
    })

@csrf_exempt
def api_carrito_agregar(request):
    user = get_user_from_token(request)
    if user is None:
        return JsonResponse({"error": "Token inválido."}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    data = json.loads(request.body.decode("utf-8"))

    producto_id = data.get("producto_id")
    cantidad = data.get("cantidad", 1)
    nota = data.get("nota", "")

    producto = get_object_or_404(Producto, id=producto_id)

    carrito = get_or_create_carrito(user)

    # Si ya existe item, sumamos cantidad
    item, creado = CarritoItem.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={
            "cantidad": cantidad,
            "nota": nota,
            "precio_unitario": producto.precio
        }
    )

    if not creado:
        item.cantidad += cantidad
        item.save()

    return JsonResponse({"message": "Producto agregado al carrito."}, status=200)


@csrf_exempt
def api_carrito_eliminar(request, item_id):
    user = get_user_from_token(request)
    if user is None:
        return JsonResponse({"error": "Token inválido."}, status=401)

    carrito = get_or_create_carrito(user)

    try:
        item = carrito.items.get(id=item_id)
        item.delete()
    except CarritoItem.DoesNotExist:
        return JsonResponse({"error": "Item no encontrado."}, status=404)

    return JsonResponse({"message": "Item eliminado."}, status=200)

@csrf_exempt
def api_confirmar_pago(request):
    """
    Crea un pedido basado en el carrito del usuario.
    Requiere token y recibe JSON con datos de pago.
    """
    user = get_user_from_token(request)
    if user is None:
        return JsonResponse({"error": "Token inválido."}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    # Leer JSON de la app
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    metodo_pago = data.get("metodo_pago", "tarjeta")
    mesa_numero = data.get("mesa", None)

    # Obtener carrito real
    carrito = get_or_create_carrito(user)
    items = carrito.items.all()

    if not items:
        return JsonResponse({"error": "El carrito está vacío."}, status=400)

    # Asignar mesa si viene
    mesa = None
    if mesa_numero:
        try:
            mesa = Mesa.objects.get(numero=mesa_numero)
            mesa.ocupada = True
            mesa.save()
        except Mesa.DoesNotExist:
            return JsonResponse({"error": "Mesa no válida."}, status=400)

    # Calcular total
    total = 0
    for item in items:
        total += float(item.subtotal())

    # Crear Pedido
    pedido = Pedido.objects.create(
        cliente=user,
        total=total,
        estatus="activo",
        metodo_pago=metodo_pago
    )

    # Crear detalles
    for item in items:
        PedidoDetalle.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            notas=item.nota
        )

    # Vaciar carrito
    carrito.items.all().delete()

    # Calcular tiempo estimado
    pedidos_activos = Pedido.objects.filter(estatus="activo").count()
    tiempo_estimado = 20 + (pedidos_activos * 10)

    # Respuesta final para Flutter
    return JsonResponse({
        "message": "Pedido creado correctamente.",
        "pedido_id": pedido.id,
        "total": total,
        "tiempo_estimado": tiempo_estimado
    }, status=200)

def api_pedidos(request):
    """
    Lista todos los pedidos del usuario autenticado por token.
    """
    user = get_user_from_token(request)
    if user is None:
        return JsonResponse({"error": "Token inválido."}, status=401)

    pedidos = Pedido.objects.filter(cliente=user).order_by("-fecha")

    data = []

    for p in pedidos:
        data.append({
            "id": p.id,
            "fecha": p.fecha.strftime("%Y-%m-%d %H:%M"),
            "total": float(p.total),
            "estatus": p.estatus,
            "metodo_pago": p.metodo_pago,
        })

    return JsonResponse(data, safe=False)
def api_pedido_detalle(request, pedido_id):
    """
    Devuelve el detalle de un pedido específico del usuario.
    """
    user = get_user_from_token(request)
    if user is None:
        return JsonResponse({"error": "Token inválido."}, status=401)

    try:
        pedido = Pedido.objects.get(id=pedido_id, cliente=user)
    except Pedido.DoesNotExist:
        return JsonResponse({"error": "Pedido no encontrado."}, status=404)

    detalles_json = []

    for det in pedido.detalles.all():
        detalles_json.append({
            "producto_id": det.producto.id,
            "nombre": det.producto.nombre,
            "cantidad": det.cantidad,
            "precio_unitario": float(det.precio_unitario),
            "subtotal": float(det.subtotal()),
            "nota": det.notas,
            # 👇 AQUÍ
            "imagen": request.build_absolute_uri(det.producto.imagen.url)
                    if det.producto.imagen else None,
        })

    data = {
        "id": pedido.id,
        "fecha": pedido.fecha.strftime("%Y-%m-%d %H:%M"),
        "total": float(pedido.total),
        "estatus": pedido.estatus,
        "metodo_pago": pedido.metodo_pago,
        "items": detalles_json
    }

    return JsonResponse(data, status=200)

from django.contrib.auth.models import User
from .models import Perfil, Carrito
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def api_registro(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    avatar_default = data.get("avatar_default", "imagen01.png")

    if not all([first_name, last_name, email, password]):
        return JsonResponse({"error": "Faltan campos"}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({"error": "El usuario ya existe"}, status=400)

    # Crear usuario
    user = User.objects.create_user(
        username=email,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        is_staff=False,
        is_superuser=False
    )

    # Crear perfil
    perfil = Perfil.objects.create(
        usuario=user,
        avatar_default=avatar_default
    )

    # Crear carrito
    Carrito.objects.create(usuario=user)

    return JsonResponse({
        "message": "Usuario registrado correctamente",
        "user_id": user.id
    }, status=201)

from django.contrib.auth.models import User
from .models import Perfil, Carrito
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def api_registro(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    avatar_default = data.get("avatar_default", "imagen01.png")

    if not all([first_name, last_name, email, password]):
        return JsonResponse({"error": "Faltan campos"}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({"error": "El usuario ya existe"}, status=400)

    # Crear usuario
    user = User.objects.create_user(
        username=email,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        is_staff=False,
        is_superuser=False
    )

    # Crear perfil
    perfil = Perfil.objects.create(
        usuario=user,
        avatar_default=avatar_default
    )

    # Crear carrito
    Carrito.objects.create(usuario=user)

    return JsonResponse({
        "message": "Usuario registrado correctamente",
        "user_id": user.id
    }, status=201)
