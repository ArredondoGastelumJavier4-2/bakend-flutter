from django.contrib import admin
from .models import Categoria, Producto, Perfil, Pedido, PedidoDetalle

admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Perfil)
admin.site.register(Pedido)
admin.site.register(PedidoDetalle)
