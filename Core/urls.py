from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movimientos/', views.vista_movimientos, name='movimientos'),
    path('productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
]
