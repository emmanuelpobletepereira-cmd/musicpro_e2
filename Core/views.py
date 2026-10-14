from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ProductoForm
from .models import Categoria, DetalleCompra, DetalleVenta, Movimiento, Producto


def home(request):
    consulta = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    stock = request.GET.get('stock', '')
    productos = Producto.objects.select_related('categoria', 'marca').order_by('id')
    if consulta:
        productos = productos.filter(
            Q(codigo__icontains=consulta)
            | Q(nombre__icontains=consulta)
            | Q(ubicacion__icontains=consulta)
        )
    if categoria:
        # Un parámetro inválido no debe provocar un error de conversión del ORM.
        if categoria.isascii() and categoria.isdigit() and len(categoria) <= 19:
            productos = productos.filter(categoria_id=int(categoria))
        else:
            productos = productos.none()
    if stock == 'critico':
        productos = productos.filter(cantidad__lte=F('stock_minimo'))
    elif stock == 'normal':
        productos = productos.filter(cantidad__gt=F('stock_minimo'))
    else:
        stock = ''
    pagina = Paginator(productos, 50).get_page(request.GET.get('page'))
    return render(request, 'index.html', {
        'productos': pagina,
        'pagina': pagina,
        'consulta': consulta,
        'categorias': Categoria.objects.order_by('nombre'),
        'categoria_seleccionada': categoria,
        'stock_seleccionado': stock,
    })


def vista_movimientos(request):
    tipo = request.GET.get('tipo', '')
    movimientos = Movimiento.objects.select_related(
        'producto', 'detalle_compra__compra', 'detalle_venta__venta',
    ).order_by('-fecha', '-id')
    if tipo in ('INGRESO', 'SALIDA'):
        movimientos = movimientos.filter(tipo=tipo)
    else:
        tipo = ''
    pagina = Paginator(movimientos, 50).get_page(request.GET.get('page'))
    return render(request, 'movimientos.html', {
        'movimientos': pagina, 'pagina': pagina, 'tipo_seleccionado': tipo,
    })


@login_required(login_url='admin:login')
@permission_required('bodega.add_producto', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def producto_crear(request):
    form = ProductoForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        producto = form.save()
        messages.success(request, f'Producto {producto.codigo} creado correctamente.')
        return redirect('home')
    return render(request, 'producto_form.html', {
        'form': form, 'titulo': 'Registrar producto', 'accion': 'Crear producto',
    })


@login_required(login_url='admin:login')
@permission_required('bodega.change_producto', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST if request.method == 'POST' else None, instance=producto)
    if request.method == 'POST' and form.is_valid():
        producto = form.save()
        messages.success(request, f'Producto {producto.codigo} actualizado correctamente.')
        return redirect('home')
    return render(request, 'producto_form.html', {
        'form': form, 'producto': producto,
        'titulo': 'Editar producto', 'accion': 'Guardar cambios',
    })


@login_required(login_url='admin:login')
@permission_required('bodega.delete_producto', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto.objects.select_related('categoria'), pk=pk)
    error = ''
    if request.method == 'POST':
        codigo = producto.codigo
        try:
            producto.delete()
        except ProtectedError:
            error = (
                'No se puede eliminar este producto porque tiene movimientos o documentos asociados. '
                'Se conserva el producto para proteger el historial de la bodega.'
            )
        else:
            messages.success(request, f'Producto {codigo} eliminado correctamente.')
            return redirect('home')
    return render(request, 'producto_confirmar_eliminacion.html', {
        'producto': producto,
        'tiene_movimientos': Movimiento.objects.filter(producto=producto).exists(),
        'tiene_documentos': (
            DetalleCompra.objects.filter(producto=producto).exists()
            or DetalleVenta.objects.filter(producto=producto).exists()
        ),
        'error': error,
    })
