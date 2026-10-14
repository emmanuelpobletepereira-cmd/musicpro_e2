from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import (
    Categoria, Cliente, Compra, DetalleCompra, DetalleVenta,
    Movimiento, Producto, Proveedor, Venta,
)


class EdicionDocumentosConMovimientosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        categoria = Categoria.objects.create(nombre='Instrumentos')
        cls.producto = Producto.objects.create(
            codigo='EDITAR-1', nombre='Guitarra', categoria=categoria, ubicacion='A1',
        )
        cls.otro_producto = Producto.objects.create(
            codigo='EDITAR-2', nombre='Bajo', categoria=categoria, ubicacion='A2',
        )
        proveedor = Proveedor.objects.create(nombre='Proveedor', rut='11111111-1')
        cliente = Cliente.objects.create(nombre='Cliente', rut='22222222-2')
        cls.compra = Compra.objects.create(numero='C-EDITAR', proveedor=proveedor)
        cls.venta = Venta.objects.create(numero='V-EDITAR', cliente=cliente)
        cls.detalle_compra = DetalleCompra.objects.create(
            compra=cls.compra, producto=cls.producto,
            cantidad=10, costo_unitario=Decimal('100.00'),
        )
        cls.detalle_venta = DetalleVenta.objects.create(
            venta=cls.venta, producto=cls.producto,
            cantidad=10, precio_unitario=Decimal('125.00'),
        )
        for campo, tipo, detalle in (
            ('detalle_compra', 'INGRESO', cls.detalle_compra),
            ('detalle_venta', 'SALIDA', cls.detalle_venta),
        ):
            # Dos movimientos distintos comprueban que se revisan todos,
            # incluso cuando el primero tiene una cantidad menor.
            for cantidad in (2, 8):
                Movimiento.objects.create(
                    producto=cls.producto, tipo=tipo, cantidad=cantidad,
                    motivo='Recepción de mercadería' if tipo == 'INGRESO' else 'Por venta',
                    **{campo: detalle},
                )

    def test_cambiar_producto_del_detalle_no_deja_movimientos_incoherentes(self):
        for detalle in (self.detalle_compra, self.detalle_venta):
            with self.subTest(modelo=type(detalle).__name__):
                detalle.producto = self.otro_producto
                with self.assertRaises(ValidationError) as error:
                    detalle.full_clean()
                self.assertIn('producto', error.exception.message_dict)
                detalle.refresh_from_db()
                self.assertEqual(detalle.producto, self.producto)

    def test_reducir_cantidad_revisa_el_mayor_movimiento_asociado(self):
        for detalle in (self.detalle_compra, self.detalle_venta):
            with self.subTest(modelo=type(detalle).__name__):
                detalle.cantidad = 7
                with self.assertRaises(ValidationError) as error:
                    detalle.full_clean()
                self.assertIn('cantidad', error.exception.message_dict)
                detalle.cantidad = 8
                detalle.full_clean()

    def test_aumentar_cantidad_y_cambiar_precio_conserva_trazabilidad(self):
        for detalle, campo_precio in (
            (self.detalle_compra, 'costo_unitario'),
            (self.detalle_venta, 'precio_unitario'),
        ):
            with self.subTest(modelo=type(detalle).__name__):
                detalle.cantidad = 12
                setattr(detalle, campo_precio, Decimal('150.25'))
                detalle.full_clean()
                detalle.save()
                detalle.refresh_from_db()
                self.assertEqual(detalle.cantidad, 12)
                self.assertEqual(detalle.subtotal, Decimal('1803.00'))
                for movimiento in detalle.movimiento_set.all():
                    movimiento.full_clean()

    def test_detalle_sin_movimientos_admite_editar_producto_y_cantidad(self):
        for modelo, documento, campo_precio in (
            (DetalleCompra, {'compra': self.compra}, 'costo_unitario'),
            (DetalleVenta, {'venta': self.venta}, 'precio_unitario'),
        ):
            with self.subTest(modelo=modelo.__name__):
                detalle = modelo.objects.create(
                    producto=self.otro_producto, cantidad=10,
                    **documento, **{campo_precio: Decimal('50.00')},
                )
                # Se usa un documento nuevo para evitar la restricción de un
                # producto por documento al cambiarlo al producto ya usado.
                if modelo is DetalleCompra:
                    detalle.compra = Compra.objects.create(
                        numero='C-SIN-MOVIMIENTOS', proveedor=self.compra.proveedor,
                    )
                else:
                    detalle.venta = Venta.objects.create(
                        numero='V-SIN-MOVIMIENTOS', cliente=self.venta.cliente,
                    )
                detalle.producto = self.producto
                detalle.cantidad = 1
                detalle.full_clean()
                detalle.save()
                detalle.refresh_from_db()
                self.assertEqual(detalle.producto, self.producto)
                self.assertEqual(detalle.cantidad, 1)

    def test_campos_invalidos_y_detalles_nuevos_producen_validacion(self):
        for modelo, documento, campo_precio in (
            (DetalleCompra, {'compra': self.compra}, 'costo_unitario'),
            (DetalleVenta, {'venta': self.venta}, 'precio_unitario'),
        ):
            with self.subTest(modelo=modelo.__name__):
                nuevo = modelo(
                    producto=self.otro_producto, cantidad=1,
                    **documento, **{campo_precio: Decimal('50.00')},
                )
                nuevo.full_clean()
                nuevo.producto_id = 'invalido'
                nuevo.cantidad = 'invalido'
                with self.assertRaises(ValidationError):
                    nuevo.full_clean()
                existente = modelo.objects.get(pk=(
                    self.detalle_compra.pk if modelo is DetalleCompra else self.detalle_venta.pk
                ))
                existente.producto_id = 'invalido'
                existente.cantidad = 'invalido'
                with self.assertRaises(ValidationError):
                    existente.full_clean()
