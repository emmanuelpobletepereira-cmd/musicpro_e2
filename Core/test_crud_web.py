from urllib.parse import urlencode
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.html import escape

from .models import Categoria, Compra, DetalleCompra, Movimiento, Producto, Proveedor


class ProductoCrudWebTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.create(nombre='Instrumentos')
        cls.producto = Producto.objects.create(
            codigo='WEB-01', nombre='Guitarra', categoria=cls.categoria,
            ubicacion='Pasillo 1', cantidad=8, stock_minimo=3,
        )
        cls.operador = get_user_model().objects.create_user(
            'operador-web', password='Clave-de-prueba-123', is_staff=True,
        )
        cls.operador.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='bodega',
            codename__in=['add_producto', 'change_producto', 'delete_producto'],
        ))
        cls.lector = get_user_model().objects.create_user('lector-web', is_staff=True)

    def datos_producto(self, **cambios):
        datos = {
            'codigo': 'WEB-NUEVO', 'nombre': 'Bajo eléctrico',
            'categoria': self.categoria.pk, 'ubicacion': 'Pasillo 2',
            'cantidad': 12, 'stock_minimo': 4,
        }
        datos.update(cambios)
        return datos

    def rutas_escritura(self):
        return (
            reverse('producto_crear'),
            reverse('producto_editar', args=[self.producto.pk]),
            reverse('producto_eliminar', args=[self.producto.pk]),
        )

    def test_anonimo_consulta_y_debe_identificarse_para_modificar(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.assertEqual(self.client.get(reverse('movimientos')).status_code, 200)
        for ruta in self.rutas_escritura():
            for metodo in ('get', 'post'):
                with self.subTest(ruta=ruta, metodo=metodo):
                    respuesta = getattr(self.client, metodo)(ruta)
                    self.assertEqual(respuesta.status_code, 302)
                    self.assertEqual(respuesta.url, f'{reverse("admin:login")}?next={ruta}')
        self.assertEqual(Producto.objects.count(), 1)

    def test_autenticado_sin_permisos_recibe_403_y_no_cambia_datos(self):
        self.client.force_login(self.lector)
        for ruta in self.rutas_escritura():
            for metodo in ('get', 'post'):
                with self.subTest(ruta=ruta, metodo=metodo):
                    respuesta = getattr(self.client, metodo)(ruta, self.datos_producto())
                    self.assertEqual(respuesta.status_code, 403)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.codigo, 'WEB-01')
        self.assertEqual(Producto.objects.count(), 1)
        listado = self.client.get(reverse('home'))
        self.assertNotContains(listado, reverse('producto_crear'))
        self.assertNotContains(listado, reverse('producto_editar', args=[self.producto.pk]))
        self.assertNotContains(listado, reverse('producto_eliminar', args=[self.producto.pk]))

    def test_permiso_de_crear_no_autoriza_editar_ni_eliminar(self):
        self.lector.user_permissions.add(Permission.objects.get(
            content_type__app_label='bodega', codename='add_producto',
        ))
        self.client.force_login(self.lector)
        self.assertEqual(self.client.get(reverse('producto_crear')).status_code, 200)
        self.assertRedirects(
            self.client.post(reverse('producto_crear'), self.datos_producto()), reverse('home'),
        )
        for ruta in self.rutas_escritura()[1:]:
            self.assertEqual(self.client.post(ruta, self.datos_producto()).status_code, 403)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_crear_consultar_editar_y_eliminar_producto_sin_movimientos(self):
        self.client.force_login(self.operador)
        self.assertEqual(self.client.get(reverse('producto_crear')).status_code, 200)
        self.assertEqual(Producto.objects.count(), 1)
        respuesta = self.client.post(reverse('producto_crear'), self.datos_producto())
        self.assertRedirects(respuesta, reverse('home'))
        nuevo = Producto.objects.get(codigo='WEB-NUEVO')
        self.assertEqual(nuevo.categoria_id, self.categoria.pk)
        self.assertContains(self.client.get(reverse('home'), {'q': 'WEB-NUEVO'}), 'Bajo eléctrico')
        editar = reverse('producto_editar', args=[nuevo.pk])
        self.assertEqual(self.client.get(editar).context['form'].instance.pk, nuevo.pk)
        respuesta = self.client.post(editar, self.datos_producto(cantidad=0, ubicacion='Pasillo 5'))
        self.assertRedirects(respuesta, reverse('home'))
        nuevo.refresh_from_db()
        self.assertEqual(nuevo.cantidad, 0)
        self.assertEqual(nuevo.ubicacion, 'Pasillo 5')
        self.assertFalse(Movimiento.objects.exists())
        eliminar = reverse('producto_eliminar', args=[nuevo.pk])
        self.assertContains(self.client.get(eliminar), 'Confirmar eliminación')
        self.assertTrue(Producto.objects.filter(pk=nuevo.pk).exists())
        self.assertRedirects(self.client.post(eliminar), reverse('home'))
        self.assertFalse(Producto.objects.filter(pk=nuevo.pk).exists())

    def test_formulario_rechaza_codigo_duplicado_negativos_y_categoria_inexistente(self):
        self.client.force_login(self.operador)
        casos = (
            ({'codigo': self.producto.codigo}, 'codigo'),
            ({'cantidad': -1}, 'cantidad'),
            ({'stock_minimo': -1}, 'stock_minimo'),
            ({'categoria': self.categoria.pk + 100}, 'categoria'),
            ({'nombre': ''}, 'nombre'),
        )
        for cambios, campo in casos:
            with self.subTest(cambios=cambios):
                respuesta = self.client.post(reverse('producto_crear'), self.datos_producto(**cambios))
                self.assertEqual(respuesta.status_code, 200)
                self.assertIn(campo, respuesta.context['form'].errors)
                self.assertEqual(Producto.objects.count(), 1)
        respuesta = self.client.post(
            reverse('producto_editar', args=[self.producto.pk]), self.datos_producto(cantidad=-1),
        )
        self.assertIn('cantidad', respuesta.context['form'].errors)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad, 8)

    def test_eliminar_producto_relacionado_conserva_historial_y_explica_proteccion(self):
        movimiento = Movimiento.objects.create(
            producto=self.producto, tipo='INGRESO', cantidad=8, motivo='Recepción inicial',
        )
        self.client.force_login(self.operador)
        ruta = reverse('producto_eliminar', args=[self.producto.pk])
        self.assertContains(self.client.get(ruta), 'proteger el historial')
        respuesta = self.client.post(ruta)
        self.assertContains(respuesta, 'No se puede eliminar este producto')
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())
        self.assertTrue(Movimiento.objects.filter(pk=movimiento.pk).exists())
        movimiento.refresh_from_db()
        self.assertEqual(movimiento.cantidad, 8)

    def test_producto_con_documento_sin_movimiento_conserva_su_historial(self):
        proveedor = Proveedor.objects.create(nombre='Proveedor', rut='33333333-3')
        compra = Compra.objects.create(numero='C-WEB-01', proveedor=proveedor)
        DetalleCompra.objects.create(
            compra=compra, producto=self.producto, cantidad=8,
            costo_unitario=Decimal('1000.00'),
        )
        self.client.force_login(self.operador)
        ruta = reverse('producto_eliminar', args=[self.producto.pk])
        respuesta = self.client.get(ruta)
        self.assertContains(respuesta, 'documentos de compra/venta asociados')
        self.assertNotContains(respuesta, 'Confirmar eliminación')
        respuesta = self.client.post(ruta)
        self.assertContains(respuesta, 'No se puede eliminar este producto')
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_metodos_no_admitidos_y_registros_ausentes(self):
        self.client.force_login(self.operador)
        for ruta in self.rutas_escritura():
            for metodo in ('put', 'delete', 'patch'):
                with self.subTest(ruta=ruta, metodo=metodo):
                    self.assertEqual(getattr(self.client, metodo)(ruta).status_code, 405)
        for nombre in ('producto_editar', 'producto_eliminar'):
            for metodo in ('get', 'post'):
                ruta = reverse(nombre, args=[self.producto.pk + 100])
                self.assertEqual(getattr(self.client, metodo)(ruta).status_code, 404)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_post_exige_token_csrf_y_formulario_entrega_token_valido(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.operador)
        ruta = reverse('producto_crear')
        self.assertEqual(cliente.post(ruta, self.datos_producto()).status_code, 403)
        self.assertEqual(Producto.objects.count(), 1)
        self.assertContains(cliente.get(ruta), 'csrfmiddlewaretoken')
        token = cliente.cookies['csrftoken'].value
        respuesta = cliente.post(ruta, {**self.datos_producto(), 'csrfmiddlewaretoken': token})
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Producto.objects.filter(codigo='WEB-NUEVO').exists())


class InventarioFiltrosWebTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.audio = Categoria.objects.create(nombre='Audio')
        cls.accesorios = Categoria.objects.create(nombre='Accesorios')
        cls.bajo = Producto.objects.create(
            codigo='FILTRO-BAJO', nombre='Amplificador', categoria=cls.audio,
            ubicacion='Pasillo 7', cantidad=2, stock_minimo=3,
        )
        cls.igual = Producto.objects.create(
            codigo='FILTRO-IGUAL', nombre='Monitor', categoria=cls.audio,
            ubicacion='Pasillo 8', cantidad=3, stock_minimo=3,
        )
        cls.normal = Producto.objects.create(
            codigo='FILTRO-NORMAL', nombre='Cable', categoria=cls.accesorios,
            ubicacion='Pasillo 9', cantidad=4, stock_minimo=3,
        )

    def ids(self, **parametros):
        respuesta = self.client.get(reverse('home'), parametros)
        self.assertEqual(respuesta.status_code, 200)
        return {producto.pk for producto in respuesta.context['productos']}

    def test_busqueda_por_codigo_nombre_y_ubicacion_se_combina_con_filtros(self):
        for consulta in ('FILTRO-BAJO', 'Amplificador', 'Pasillo 7'):
            self.assertEqual(self.ids(q=consulta), {self.bajo.pk})
        self.assertEqual(self.ids(stock='critico'), {self.bajo.pk, self.igual.pk})
        self.assertEqual(self.ids(stock='normal'), {self.normal.pk})
        self.assertEqual(self.ids(q='Amplificador', categoria=self.audio.pk, stock='critico'), {self.bajo.pk})
        self.assertEqual(self.ids(q='Amplificador', categoria=self.accesorios.pk), set())

    def test_categoria_invalida_devuelve_listado_vacio_sin_error(self):
        for categoria in ('texto', '-1', '1' * 100, '²'):
            with self.subTest(categoria=categoria):
                self.assertEqual(self.ids(categoria=categoria), set())

    def test_paginacion_conserva_busqueda_categoria_y_estado_de_stock(self):
        Producto.objects.bulk_create([
            Producto(
                codigo=f'PAG-{numero}', nombre='Serie & audio', categoria=self.audio,
                ubicacion='Estante A', cantidad=1, stock_minimo=2,
            ) for numero in range(51)
        ])
        filtros = {'q': 'Serie & audio', 'categoria': self.audio.pk, 'stock': 'critico'}
        respuesta = self.client.get(reverse('home'), filtros)
        self.assertEqual(len(respuesta.context['productos']), 50)
        self.assertEqual(respuesta.context['pagina'].paginator.count, 51)
        enlace = '?' + urlencode({**filtros, 'page': 2})
        self.assertContains(respuesta, f'href="{escape(enlace)}"')
        siguiente = self.client.get(reverse('home'), {**filtros, 'page': 2})
        self.assertEqual(len(siguiente.context['productos']), 1)
        self.assertEqual(siguiente.context['pagina'].paginator.count, 51)
