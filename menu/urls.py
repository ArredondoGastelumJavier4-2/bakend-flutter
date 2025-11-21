from django.urls import path
from . import views
from . import views_admin


urlpatterns = [

    # ============================
    # AUTENTICACIÓN
    # ============================
    path('', views.home_redirect, name="home_redirect"),  # ESTA ES LA NUEVA
    path('login/', views.login_view, name="login"),
    path('registro/', views.registro_view, name="registro"),
    path('logout/', views.logout_view, name="logout"),

    # ============================
    # CLIENTE
    # ============================
    path('cliente/', views.cliente_dashboard, name="cliente_dashboard"),
    path('cliente/perfil/', views.perfil_cliente, name="perfil_cliente"),
    path('cliente/compras/', views.compras_cliente, name="compras_cliente"),

    # Categorías y productos
    path('categoria/<int:categoria_id>/', views.categoria_detalle, name="categoria_detalle"),
    path('producto/<int:producto_id>/', views.producto_detalle, name="producto_detalle"),

    # Carrito
    path('carrito/', views.carrito, name="carrito"),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name="agregar_carrito"),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_carrito, name="eliminar_carrito"),

    # Pago
    path('pago/tarjeta/', views.pago_tarjeta, name="pago_tarjeta"),
    path('pago/confirmar/', views.confirmar_pedido, name="confirmar_pedido"),

    # ============================
    # ADMIN PANEL
    # ============================
    path('admin_panel/', views_admin.admin_home, name="admin_home"),

    # Productos
    path('admin_panel/productos/', views_admin.producto_lista, name="producto_lista"),
    path('admin_panel/productos/agregar/', views_admin.producto_agregar, name="producto_agregar"),
    path('admin_panel/productos/editar/<int:producto_id>/', views_admin.producto_editar, name="producto_editar"),
    path('admin_panel/productos/eliminar/<int:producto_id>/', views_admin.producto_eliminar, name="producto_eliminar"),

    # Categorías
    path('admin_panel/categorias/', views_admin.categoria_lista, name="categoria_lista"),
    path('admin_panel/categorias/agregar/', views_admin.categoria_agregar, name="categoria_agregar"),
    path('admin_panel/categorias/editar/<int:categoria_id>/', views_admin.categoria_editar, name="categoria_editar"),
    path('admin_panel/categorias/eliminar/<int:categoria_id>/', views_admin.categoria_eliminar, name="categoria_eliminar"),

    # Clientes
    path('admin_panel/clientes/', views_admin.cliente_lista, name="cliente_lista"),
    path('admin_panel/clientes/eliminar/<int:cliente_id>/', views_admin.cliente_eliminar, name="cliente_eliminar"),

    # Pedidos
    path('admin_panel/pedidos/', views_admin.pedido_lista, name="pedido_lista"),
    path('admin_panel/pedidos/<int:pedido_id>/', views_admin.pedido_detalle, name="pedido_detalle"),
    # Pedido detalle (cliente)
    path('cliente/pedido/<int:pedido_id>/', views.pedido_detalle, name="pedido_detalle_cliente"),


    # Reportes
    path('admin_panel/reportes/ventas/', views_admin.reporte_ventas, name="reporte_ventas"),
    path("cliente/perfil/", views.perfil_cliente, name="cliente_perfil"),
    path('admin_panel/perfil/', views_admin.perfil_admin, name="perfil_admin"),

    path('admin_panel/mesas/', views_admin.mesa_lista, name="mesa_lista"),

]
