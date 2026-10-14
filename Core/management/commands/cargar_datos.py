from base64 import urlsafe_b64encode
from datetime import datetime, timedelta, timezone as datetime_timezone
from decimal import Decimal
from time import perf_counter
from uuid import uuid4

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, connections, transaction
from django.test.utils import override_settings
from faker import Faker

from Core.models import (
    Categoria, Cliente, Compra, DetalleCompra, DetalleVenta, Marca,
    Movimiento, Producto, Proveedor, Venta,
)


class Command(BaseCommand):
    help = (
        'Añade productos ficticios con Faker y verifica su almacenamiento. '
        'Conserva los registros existentes.'
    )
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad', type=int, required=True,
            help='Productos nuevos que se añadirán (entre 1 y 1000000).',
        )
        parser.add_argument(
            '--lote', type=int, default=1000,
            help='Máximo de productos mantenidos en memoria por lote (1..10000).',
        )
        parser.add_argument(
            '--semilla', type=int,
            help='Repite los valores ficticios; los códigos siguen siendo únicos.',
        )
        parser.add_argument(
            '--con-movimientos', action='store_true',
            help='Crea también un ingreso de stock inicial por cada producto nuevo.',
        )
        parser.add_argument(
            '--completo', action='store_true',
            help=(
                'Puebla las diez tablas del negocio: catálogos, productos, compras, '
                'ventas, detalles y movimientos; el stock resulta de ingresos menos salidas.'
            ),
        )
        parser.add_argument(
            '--database', default='default', choices=tuple(connections),
            help='Alias de la base de datos configurada (por defecto: default).',
        )

    # DEBUG acumula el SQL de cada inserción. Se desactiva solo durante la carga
    # para que una prueba de un millón de filas también mantenga memoria acotada.
    @override_settings(DEBUG=False)
    def handle(self, *args, **options):
        cantidad = options['cantidad']
        tamano_lote = options['lote']
        if not 1 <= cantidad <= 1_000_000:
            raise CommandError('La cantidad debe estar entre 1 y 1000000.')
        if not 1 <= tamano_lote <= 10_000:
            raise CommandError('El lote debe estar entre 1 y 10000.')

        alias = options['database']
        if alias not in connections:
            raise CommandError(f'No existe el alias de base de datos: {alias}.')
        completo = options['completo']
        con_movimientos = options['con_movimientos'] or completo
        verbosity = options['verbosity']
        fake = Faker('es_CL')
        if options['semilla'] is not None:
            fake.seed_instance(options['semilla'])

        # Un UUID por ejecución permite repetir la semilla sin duplicar códigos.
        # 32 caracteres + guion + 7 cifras = max_length de Producto.codigo (40).
        identificador = uuid4()
        prefijo = identificador.hex
        # UUID en Base64 ocupa 22 caracteres; tipo + UUID + 7 cifras = 30.
        # Así cada documento respeta max_length sin perder la unicidad del UUID.
        prefijo_documento = urlsafe_b64encode(identificador.bytes).decode('ascii').rstrip('=')
        codigo_inicial = f'{prefijo}-0000001'
        codigo_final = f'{prefijo}-{cantidad:07d}'
        productos = Producto.objects.using(alias)
        movimientos = Movimiento.objects.using(alias)
        guardados = 0
        inicio = perf_counter()

        if verbosity:
            self.stdout.write(
                f'Carga: {prefijo}. Base: {alias}. Productos nuevos: {cantidad}. '
                f'Lote: {tamano_lote}.'
            )

        try:
            antes = productos.count()
            categorias = {}
            for nombre in ('Instrumentos', 'Audio', 'Accesorios'):
                categoria, _ = Categoria.objects.using(alias).get_or_create(nombre=nombre)
                categorias[nombre] = categoria.pk
            catalogos_completos = self.preparar_catalogos(fake, alias) if completo else None

            catalogo = (
                ('Guitarra eléctrica', categorias['Instrumentos']),
                ('Bajo eléctrico', categorias['Instrumentos']),
                ('Teclado', categorias['Instrumentos']),
                ('Batería', categorias['Instrumentos']),
                ('Amplificador', categorias['Audio']),
                ('Micrófono', categorias['Audio']),
                ('Interfaz de audio', categorias['Audio']),
                ('Cable de instrumento', categorias['Accesorios']),
                ('Atril', categorias['Accesorios']),
                ('Funda', categorias['Accesorios']),
            )
            # Guardamos los métodos del generador para reducir trabajo por fila.
            elegir = fake.random_element
            entero = fake.random_int
            modelo = fake.bothify
            siguiente_aviso = 0
            intervalo_aviso = max(tamano_lote, cantidad // 20)

            for primer_numero in range(1, cantidad + 1, tamano_lote):
                ultimo_numero = min(primer_numero + tamano_lote, cantidad + 1)
                lote = []
                operaciones = []
                for numero in range(primer_numero, ultimo_numero):
                    nombre, categoria_id = elegir(catalogo)
                    lote.append(Producto(
                        codigo=f'{prefijo}-{numero:07d}',
                        nombre=f'{nombre} {modelo(text="??-####").upper()}',
                        categoria_id=categoria_id,
                        ubicacion=f'Pasillo {entero(1, 20)} - Estante {entero(1, 50)}',
                        cantidad=entero(1 if con_movimientos else 0, 100),
                        stock_minimo=entero(1, 15),
                    ))
                    if completo:
                        comprado = lote[-1].cantidad
                        vendido = entero(1, comprado)
                        lote[-1].cantidad = comprado - vendido
                        lote[-1].marca_id = elegir(catalogos_completos['marcas'])
                        fecha_compra = fake.date_time_between_dates(
                            datetime_start=datetime(2025, 1, 1, tzinfo=datetime_timezone.utc),
                            datetime_end=datetime(2025, 12, 1, tzinfo=datetime_timezone.utc),
                            tzinfo=datetime_timezone.utc,
                        )
                        operaciones.append({
                            'numero': numero,
                            'comprado': comprado,
                            'vendido': vendido,
                            'costo': Decimal(entero(1_000, 500_000)),
                            'proveedor_id': elegir(catalogos_completos['proveedores']),
                            'cliente_id': elegir(catalogos_completos['clientes']),
                            'fecha_compra': fecha_compra,
                            'fecha_venta': fecha_compra + timedelta(days=entero(1, 30)),
                        })

                # Cada lote se confirma junto a sus movimientos. Un error revierte
                # ese lote; los lotes anteriores permanecen guardados.
                with transaction.atomic(using=alias):
                    productos.bulk_create(lote, batch_size=tamano_lote)
                    if con_movimientos:
                        # SQLite 3.35+ devuelve las PK en bulk_create. La consulta
                        # por códigos permite usar también motores que no lo hacen.
                        self.asignar_pk(productos, lote, 'codigo')
                    if completo:
                        self.crear_operaciones(
                            alias, lote, operaciones, prefijo_documento, tamano_lote,
                        )
                    elif con_movimientos:
                        movimientos.bulk_create([
                            Movimiento(
                                producto_id=producto.pk,
                                tipo='INGRESO',
                                cantidad=producto.cantidad,
                                motivo='Recepción de mercadería',
                            )
                            for producto in lote
                        ], batch_size=tamano_lote)

                guardados += len(lote)
                if verbosity and (guardados >= siguiente_aviso or guardados == cantidad):
                    self.stdout.write(f'Guardados: {guardados}/{cantidad}')
                    siguiente_aviso = guardados + intervalo_aviso

            # El rango exclusivo de códigos de esta ejecución usa el índice UNIQUE
            # y permite verificarla aunque otra sesión añada productos simultáneamente.
            carga = productos.filter(codigo__gte=codigo_inicial, codigo__lte=codigo_final)
            verificados = carga.count()
            if verificados != cantidad:
                raise CommandError(
                    f'Verificación fallida: se esperaban {cantidad} productos de esta '
                    f'carga y se encontraron {verificados}. Identificador: {prefijo}.'
                )
            if con_movimientos:
                ingresos = movimientos.filter(
                    producto__codigo__gte=codigo_inicial,
                    producto__codigo__lte=codigo_final,
                    tipo='INGRESO',
                ).count()
                if ingresos != cantidad:
                    raise CommandError(
                        f'Verificación fallida: se esperaban {cantidad} ingresos '
                        f'y se encontraron {ingresos}. Identificador: {prefijo}.'
                    )
            if completo:
                self.verificar_operaciones(alias, codigo_inicial, codigo_final, cantidad)
            despues = productos.count()
        except DatabaseError as error:
            raise CommandError(
                f'Error en la base de datos: {error}. Productos confirmados en esta '
                f'carga: {guardados}. Identificador: {prefijo}. '
                'Los lotes anteriores se conservan; una nueva ejecución añade otra carga.'
            ) from error
        except KeyboardInterrupt as error:
            raise CommandError(
                f'Carga interrumpida. Productos confirmados: {guardados}. '
                f'Identificador: {prefijo}. Los lotes anteriores se conservan.'
            ) from error

        self.stdout.write(self.style.SUCCESS(
            f'Verificación correcta: {verificados} productos nuevos almacenados. '
            f'Antes: {antes}. Después: {despues}. '
            f'Tiempo: {perf_counter() - inicio:.2f} s. Carga: {prefijo}.'
        ))
        if con_movimientos:
            self.stdout.write(self.style.SUCCESS(f'Ingresos iniciales verificados: {ingresos}.'))
        if completo:
            self.stdout.write(self.style.SUCCESS(
                f'Carga completa verificada: {cantidad} compras, {cantidad} detalles de compra, '
                f'{cantidad} ventas, {cantidad} detalles de venta y {cantidad * 2} movimientos. '
                'Las diez tablas del negocio contienen datos. Motivo de salida: Por venta.'
            ))

    @staticmethod
    def rut_ficticio(numero):
        """Identificadores estables con dígito verificador; no representan personas reales."""
        suma = sum(int(digito) * (2 + posicion % 6)
                   for posicion, digito in enumerate(reversed(str(numero))))
        resultado = 11 - suma % 11
        verificador = '0' if resultado == 11 else 'K' if resultado == 10 else str(resultado)
        return f'{numero}-{verificador}'

    def preparar_catalogos(self, fake, alias):
        """Reutiliza un catálogo pequeño; nunca actualiza los registros del usuario."""
        catalogos = {'marcas': [], 'proveedores': [], 'clientes': []}
        with transaction.atomic(using=alias):
            for nombre in ('Armonía Norte', 'Sonido Austral', 'Ritmo Pacífico'):
                marca, _ = Marca.objects.using(alias).get_or_create(
                    nombre=nombre, defaults={'pais': fake.country()[:80]},
                )
                catalogos['marcas'].append(marca.pk)
            for posicion in range(3):
                proveedor, _ = Proveedor.objects.using(alias).get_or_create(
                    rut=self.rut_ficticio(99_000_001 + posicion),
                    defaults={
                        'nombre': f'{fake.company()} Distribución Musical'[:120],
                        'email': fake.company_email(), 'telefono': fake.phone_number()[:20],
                        'direccion': fake.address().replace('\n', ', ')[:200],
                    },
                )
                catalogos['proveedores'].append(proveedor.pk)
            for posicion in range(5):
                cliente, _ = Cliente.objects.using(alias).get_or_create(
                    rut=self.rut_ficticio(99_100_001 + posicion),
                    defaults={
                        'nombre': fake.name()[:120], 'email': fake.email(),
                        'telefono': fake.phone_number()[:20],
                        'direccion': fake.address().replace('\n', ', ')[:200],
                    },
                )
                catalogos['clientes'].append(cliente.pk)
        return catalogos

    @staticmethod
    def asignar_pk(queryset, objetos, campo):
        """Recupera las PK en motores que no las devuelven con bulk_create."""
        if any(objeto.pk is None for objeto in objetos):
            por_clave = queryset.in_bulk(
                [getattr(objeto, campo) for objeto in objetos], field_name=campo,
            )
            for objeto in objetos:
                objeto.pk = por_clave[getattr(objeto, campo)].pk

    def crear_operaciones(self, alias, productos, operaciones, prefijo, tamano_lote):
        """Se ejecuta dentro de la transacción del lote, con memoria proporcional al lote."""
        compras = Compra.objects.using(alias)
        ventas = Venta.objects.using(alias)
        detalles_compra = DetalleCompra.objects.using(alias)
        detalles_venta = DetalleVenta.objects.using(alias)
        lote_compras = [Compra(
            numero=f'C{prefijo}{datos["numero"]:07d}',
            proveedor_id=datos['proveedor_id'], fecha=datos['fecha_compra'],
            observaciones='Compra de mercadería para reposición de bodega.',
        ) for datos in operaciones]
        lote_ventas = [Venta(
            numero=f'V{prefijo}{datos["numero"]:07d}',
            cliente_id=datos['cliente_id'], fecha=datos['fecha_venta'],
            observaciones='Venta de productos Music Pro.',
        ) for datos in operaciones]
        compras.bulk_create(lote_compras, batch_size=tamano_lote)
        ventas.bulk_create(lote_ventas, batch_size=tamano_lote)
        self.asignar_pk(compras, lote_compras, 'numero')
        self.asignar_pk(ventas, lote_ventas, 'numero')
        lote_detalles_compra = [DetalleCompra(
            compra_id=compra.pk, producto_id=producto.pk,
            cantidad=datos['comprado'], costo_unitario=datos['costo'],
        ) for producto, compra, datos in zip(productos, lote_compras, operaciones)]
        lote_detalles_venta = [DetalleVenta(
            venta_id=venta.pk, producto_id=producto.pk,
            cantidad=datos['vendido'], precio_unitario=datos['costo'] * Decimal('1.25'),
        ) for producto, venta, datos in zip(productos, lote_ventas, operaciones)]
        detalles_compra.bulk_create(lote_detalles_compra, batch_size=tamano_lote)
        detalles_venta.bulk_create(lote_detalles_venta, batch_size=tamano_lote)
        # Un solo detalle por documento en esta simulación permite recuperar sus
        # PK usando la FK única dentro de cada lote, sin añadir campos al esquema.
        self.asignar_pk_detalles(detalles_compra, lote_detalles_compra, 'compra_id')
        self.asignar_pk_detalles(detalles_venta, lote_detalles_venta, 'venta_id')
        lote_movimientos = []
        for producto, compra, venta, datos in zip(
            productos, lote_detalles_compra, lote_detalles_venta, operaciones,
        ):
            lote_movimientos.extend([
                Movimiento(
                    producto_id=producto.pk, tipo='INGRESO', cantidad=datos['comprado'],
                    motivo='Recepción de mercadería', fecha=datos['fecha_compra'],
                    detalle_compra_id=compra.pk,
                ),
                Movimiento(
                    producto_id=producto.pk, tipo='SALIDA', cantidad=datos['vendido'],
                    motivo='Por venta', fecha=datos['fecha_venta'], detalle_venta_id=venta.pk,
                ),
            ])
        Movimiento.objects.using(alias).bulk_create(lote_movimientos, batch_size=tamano_lote)

    @staticmethod
    def asignar_pk_detalles(queryset, objetos, campo):
        if any(objeto.pk is None for objeto in objetos):
            ids_documento = [getattr(objeto, campo) for objeto in objetos]
            por_documento = {
                getattr(objeto, campo): objeto.pk
                for objeto in queryset.filter(**{f'{campo}__in': ids_documento})
            }
            for objeto in objetos:
                objeto.pk = por_documento[getattr(objeto, campo)]

    @staticmethod
    def verificar_operaciones(alias, codigo_inicial, codigo_final, cantidad):
        filtro = {
            'producto__codigo__gte': codigo_inicial,
            'producto__codigo__lte': codigo_final,
        }
        conteos = {
            'detalles de compra': DetalleCompra.objects.using(alias).filter(**filtro).count(),
            'compras': DetalleCompra.objects.using(alias).filter(**filtro)
                .values('compra_id').distinct().count(),
            'detalles de venta': DetalleVenta.objects.using(alias).filter(**filtro).count(),
            'ventas': DetalleVenta.objects.using(alias).filter(**filtro)
                .values('venta_id').distinct().count(),
            'salidas': Movimiento.objects.using(alias).filter(
                **filtro, tipo='SALIDA', motivo='Por venta', detalle_venta__isnull=False,
            ).count(),
        }
        for nombre, almacenados in conteos.items():
            if almacenados != cantidad:
                raise CommandError(
                    f'Verificación fallida: se esperaban {cantidad} {nombre} '
                    f'y se encontraron {almacenados}.'
                )
