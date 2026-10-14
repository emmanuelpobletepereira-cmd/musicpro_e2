from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse
from .models import Categoria, Producto, Movimiento


class EvaluacionDosTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser('prueba', password='Clave-de-prueba-123')
        self.client.force_login(user)
        self.categoria = Categoria.objects.create(nombre='Audio')

    def test_crud_producto_en_admin(self):
        datos = dict(codigo='DEF-01', nombre='Amplificador', categoria=self.categoria.pk,
                     ubicacion='A1', cantidad=10, stock_minimo=5)
        respuesta = self.client.post(reverse('admin:bodega_producto_add'), datos)
        self.assertEqual(respuesta.status_code, 302)
        producto = Producto.objects.get(codigo='DEF-01')
        datos['cantidad'] = 20
        respuesta = self.client.post(reverse('admin:bodega_producto_change', args=[producto.pk]), datos)
        self.assertEqual(respuesta.status_code, 302)
        producto.refresh_from_db()
        self.assertEqual(producto.cantidad, 20)
        self.assertContains(self.client.get(reverse('admin:bodega_producto_changelist'), {'q': 'DEF-01'}), 'Amplificador')
        self.assertContains(self.client.get('/'), 'DEF-01')
        respuesta = self.client.post(reverse('admin:bodega_producto_delete', args=[producto.pk]), {'post': 'yes'})
        self.assertEqual(respuesta.status_code, 302)
        self.assertFalse(Producto.objects.filter(pk=producto.pk).exists())

    def test_faker_y_paginas(self):
        call_command('cargar_datos', cantidad=100)
        self.assertEqual(Producto.objects.count(), 100)
        self.assertEqual(Producto.objects.values('codigo').distinct().count(), 100)
        self.assertEqual(len(self.client.get('/').context['productos']), 50)
        self.assertEqual(self.client.get('/movimientos/').status_code, 200)

    def test_movimiento_rechaza_cero_en_admin(self):
        producto = Producto.objects.create(codigo='P1', nombre='Cable', categoria=self.categoria, ubicacion='A')
        respuesta = self.client.post(reverse('admin:bodega_movimiento_add'), {
            'producto': producto.pk, 'tipo': 'SALIDA', 'cantidad': 0,
            'fecha_0': '2026-10-12', 'fecha_1': '10:00:00', 'motivo': 'Prueba',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('cantidad', respuesta.context['adminform'].form.errors)
        self.assertEqual(Movimiento.objects.count(), 0)

    def test_historial_filtra_salidas_y_ofrece_registro_por_venta(self):
        producto = Producto.objects.create(
            codigo='VENTA-01', nombre='Guitarra', categoria=self.categoria, ubicacion='A1',
        )
        ingreso = Movimiento.objects.create(
            producto=producto, tipo='INGRESO', cantidad=10, motivo='Recepción de mercadería',
        )
        salida = Movimiento.objects.create(
            producto=producto, tipo='SALIDA', cantidad=2, motivo='Por venta',
        )
        respuesta = self.client.get(reverse('movimientos'), {'tipo': 'SALIDA'})
        self.assertEqual([m.pk for m in respuesta.context['movimientos']], [salida.pk])
        self.assertContains(respuesta, 'Por venta')
        self.assertNotContains(respuesta, 'Recepción de mercadería')
        self.assertContains(respuesta, 'tipo=SALIDA&amp;motivo=Por%20venta')
        respuesta = self.client.get(reverse('movimientos'), {'tipo': 'INGRESO'})
        self.assertEqual([m.pk for m in respuesta.context['movimientos']], [ingreso.pk])
        respuesta = self.client.get(reverse('movimientos'), {'tipo': 'INVALIDO'})
        self.assertEqual(len(respuesta.context['movimientos']), 2)
