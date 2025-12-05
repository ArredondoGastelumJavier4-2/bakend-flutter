# ======================================
# IMPORTS NECESARIOS
# ======================================
# ============================
# DJANGO CORE IMPORTS
# ============================
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ============================
# DJANGO AUTH
# ============================
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login  # alias para evitar conflicto

# ============================
# BASE DE DATOS
# ============================
from django.db import transaction

# ============================
# PROYECTO LOCAL
# ============================
from .forms import FormLogin, FormRegistro
from .models import (
    Producto,
    Categoria,
    Pedido,
    PedidoDetalle,
    Mesa,
    ApiToken,
)

# ============================
# PYTHON NATIVO
# ============================
import json

# ======================================
# REGISTRO DE CLIENTES
# ======================================
# ======================================
# REGISTRO DE CLIENTES (CON CARRITO)
# ======================================
def registro_view(request):
    from .models import Perfil, Carrito
    from .forms import FormRegistro

    if request.method == "POST":
        form = FormRegistro(request.POST, request.FILES)

        if form.is_valid():
            # Crear usuario
            user = User.objects.create_user(
                username=form.cleaned_data["email"],  # Email como username
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                is_staff=False,
                is_superuser=False
            )

            # Crear perfil
            perfil = Perfil.objects.create(usuario=user)

            # Foto personalizada o avatar default
            foto_subida = form.cleaned_data.get("foto")
            avatar_default = form.cleaned_data.get("avatar_default")

            if foto_subida:
                perfil.foto = foto_subida
            elif avatar_default:
                perfil.avatar_default = f"imagen0{avatar_default}.png"
            else:
                perfil.avatar_default = "imagen01.png"

            perfil.save()

            # ============================================
            # CREAR CARRITO AUTOMÁTICAMENTE
            # ============================================
            Carrito.objects.create(usuario=user)

            messages.success(request, "Registro exitoso. Ahora inicia sesión.")
            return redirect("login")

        # Si el formulario es inválido → recarga con errores
        return render(request, "menu/autenticacion/registro.html", {"form": form})

    else:
        form = FormRegistro()

    return render(request, "menu/autenticacion/registro.html", {"form": form})


# ======================================
# LOGIN DE USUARIOS
# ======================================
def login_view(request):
    form = FormLogin()

    if request.method == "POST":
        form = FormLogin(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            usuario = authenticate(request, username=email, password=password)

            if usuario is None:
                messages.error(request, "Credenciales incorrectas.")
                return redirect("login")

            login(request, usuario)

            if usuario.is_staff:
                return redirect("admin_home")
            return redirect("cliente_dashboard")

    return render(request, "menu/autenticacion/login.html", {"form": form})


# ======================================
# LOGOUT
# ======================================
def logout_view(request):
    logout(request)
    return redirect("login")


# ======================================
# DASHBOARD DEL CLIENTE (HOME)
# ======================================
@login_required
def cliente_dashboard(request):
    categorias = Categoria.objects.all()
    data_categorias = []

    for cat in categorias:
        productos = Producto.objects.filter(
            categoria=cat,
            estado="activo"
        )[:3]  # Mostrar solo los primeros 3

        data_categorias.append({
            "categoria": cat,
            "productos": productos
        })

    return render(request, "menu/cliente/home.html", {
        "data_categorias": data_categorias,
        "categorias": categorias
    })


# ======================================
# DETALLE DE CATEGORÍA
# ======================================
@login_required
def categoria_detalle(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    productos = Producto.objects.filter(categoria=categoria, estado="activo")

    return render(request, "menu/cliente/categoria_detalle.html", {
        "categoria": categoria,
        "productos": productos
    })


# ======================================
# DETALLE DE PRODUCTO
# ======================================
@login_required
def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Agregar producto al carrito
    if request.method == "POST":
        return redirect("agregar_carrito", producto_id=producto.id)

    return render(request, "menu/cliente/producto_detalle.html", {"producto": producto})


# ======================================
# CARRITO (USANDO SESIÓN)
# ======================================
@login_required
def carrito(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0

    for product_id, data in cart.items():
        producto = Producto.objects.get(id=product_id)
        subtotal = producto.precio * data["cantidad"]
        total += subtotal

        items.append({
            "id": product_id,
            "producto": producto,
            "cantidad": data["cantidad"],
            "subtotal": subtotal
        })

    return render(request, "menu/cliente/carrito.html", {
        "items": items,
        "total": total
    })


# ======================================
# AGREGAR PRODUCTO AL CARRITO
# ======================================
@login_required
def agregar_carrito(request, producto_id):
    """
    Agrega un producto al carrito con la cantidad seleccionada
    y las instrucciones opcionales del cliente.
    """
    cart = request.session.get("cart", {})

    # Cantidad seleccionada por el usuario
    cantidad = int(request.POST.get("cantidad", 1))
    nota = request.POST.get("nota", "")

    # Si el producto no está en el carrito, se agrega nuevo
    if str(producto_id) not in cart:
        cart[str(producto_id)] = {"cantidad": cantidad, "nota": nota}
    else:
        # Si ya existe, suma la cantidad
        cart[str(producto_id)]["cantidad"] += cantidad

    # Guardar cambios
    request.session["cart"] = cart

    messages.success(request, f"✅ {cantidad} × {Producto.objects.get(id=producto_id).nombre} agregado(s) al carrito.")
    return redirect("cliente_dashboard")




# ======================================
# ELIMINAR ITEM DEL CARRITO
# ======================================
@login_required
def eliminar_carrito(request, item_id):
    cart = request.session.get("cart", {})

    if str(item_id) in cart:
        del cart[str(item_id)]

    request.session["cart"] = cart
    return redirect("carrito")


# ======================================
# PAGO TARJETA
# ======================================
from .models import Mesa

@login_required
def pago_tarjeta(request):
    mesas = Mesa.objects.all().order_by('numero')
    return render(request, "menu/cliente/pago_tarjeta.html", {'mesas': mesas})



# ======================================
# CONFIRMAR PEDIDO
# ======================================
@login_required
@transaction.atomic
def confirmar_pedido(request):
    if request.method == "POST":
        # --- Mesa seleccionada ---
        mesa_id = request.POST.get("mesa_id")
        mesa = None
        if mesa_id:
            try:
                mesa = Mesa.objects.get(numero=mesa_id)
                mesa.ocupada = True
                mesa.save()
            except Mesa.DoesNotExist:
                messages.error(request, "Mesa seleccionada no válida.")
                return redirect("pago_tarjeta")

        # --- Obtener carrito (ajustado a tu estructura) ---
        cart = request.session.get("cart", {})
        if not cart:
            messages.error(request, "Tu carrito está vacío.")
            return redirect("cliente_dashboard")

        total = 0
        for product_id, data in cart.items():
            producto = Producto.objects.get(id=product_id)
            total += producto.precio * data["cantidad"]

        # --- Crear pedido ---
        pedido = Pedido.objects.create(
            cliente=request.user,
            total=total,
            estatus="activo",
            metodo_pago="tarjeta" if not request.POST.get("pagar_sucursal") else "sucursal",
        )

        # --- Crear detalles ---
        for product_id, data in cart.items():
            producto = Producto.objects.get(id=product_id)
            PedidoDetalle.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=data["cantidad"],
                precio_unitario=producto.precio,
            )

        # --- Limpiar carrito ---
        request.session["cart"] = {}
        request.session.modified = True

        # --- Calcular tiempo estimado ---
        pedidos_activos = Pedido.objects.filter(estatus="activo").count()
        tiempo_estimado = 20 + (pedidos_activos * 10)

        # --- Mensaje de éxito ---
        messages.success(
            request,
            f"✅ Tu pedido se ha creado con éxito. Tiempo estimado: {tiempo_estimado} minutos."
        )

        # --- Redirigir al HOME (donde sí se muestran los mensajes) ---
        return redirect("cliente_dashboard")


    return redirect("cliente_dashboard")

# ======================================
# PERFIL DEL CLIENTE
# ======================================
@login_required
def perfil_cliente(request):
    perfil = request.user.perfil

    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        nueva_foto = request.FILES.get("foto")
        nuevo_avatar = request.POST.get("avatar_default")
        nueva_contra = request.POST.get("password")

        if nueva_foto:
            perfil.foto = nueva_foto
            perfil.avatar_default = None
        elif nuevo_avatar:
            perfil.avatar_default = nuevo_avatar
            perfil.foto = None
        elif not perfil.foto and not perfil.avatar_default:
            perfil.avatar_default = "imagen01.png"

        if nueva_contra:
            user.set_password(nueva_contra)
            user.save()
            update_session_auth_hash(request, user)

        user.save()
        perfil.save()
        messages.success(request, "✅ Perfil actualizado correctamente")
        return redirect("perfil_cliente")

    return render(request, "menu/cliente/perfil.html", {"perfil": perfil})


# ======================================
# HISTORIAL DE COMPRAS
# ======================================
@login_required
def compras_cliente(request):
    pedidos = Pedido.objects.filter(cliente=request.user).order_by("-fecha")
    return render(request, "menu/cliente/compras.html", {"pedidos": pedidos})


# ======================================
# REDIRECCIÓN HOME SEGÚN USUARIO
# ======================================
def home_redirect(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.is_staff:
        return redirect("admin_home")
    return redirect("cliente_dashboard")


# ======================================
# CONTADOR GLOBAL DE ITEMS EN CARRITO
# ======================================
def carrito_items_count(request):
    if request.user.is_authenticated and not request.user.is_staff:
        cart = request.session.get("cart", {})
        total_items = sum(item["cantidad"] for item in cart.values())
        return {"carrito_items_count": total_items}
    return {"carrito_items_count": 0}

# ======================================
# DETALLE DE UN PEDIDO
# ======================================
@login_required
def pedido_detalle(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    detalles = PedidoDetalle.objects.filter(pedido=pedido)

    return render(request, "menu/cliente/pedido_detalle.html", {
        "pedido": pedido,
        "detalles": detalles
    })



# ======================================
# api token pal fluter
# ======================================
@csrf_exempt
def api_login(request):
    """
    Endpoint de login para la app Flutter.
    Acepta:
      - email
      - password
    Devuelve:
      - token
      - user_id
      - email
    """

    # Solo POST
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido. Usa POST."}, status=405)

    # Leer JSON recibido
    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    email = data.get("email")
    password = data.get("password")

    # Validar campos obligatorios
    if not email or not password:
        return JsonResponse({"error": "Faltan email o password."}, status=400)

    # Buscar usuario por email
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado."}, status=400)

    # Autenticar usando el username real del usuario
    user = authenticate(request, username=user_obj.username, password=password)

    if user is None:
        return JsonResponse({"error": "Credenciales incorrectas."}, status=400)

    # Login en Django (opcional pero recomendado)
    django_login(request, user)

    # Obtener o generar token para API
    token, _ = ApiToken.objects.get_or_create(user=user)

    return JsonResponse({
        "token": token.key,
        "user_id": user.id,
        "email": user.email,
        "message": "Login exitoso."
    }, status=200)

