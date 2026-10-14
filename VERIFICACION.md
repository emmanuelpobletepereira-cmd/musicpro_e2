# Verificación de base de datos — 13 de octubre de 2026

Entorno comprobado: Python 3.12.14, Django 6.1.1, Faker 40.40.0 y SQLite. Las cinco dependencias de `requirements.txt` coinciden con las del proyecto de apoyo y las versiones instaladas: asgiref 3.12.1, Django 6.1.1, Faker 40.40.0, sqlparse 0.6.0 y tzdata 2026.5. `python -m pip check` no detectó incompatibilidades.

## Diez tablas propias y migraciones

El profesor exige diez tablas propias del negocio, según confirmación del estudiante. Están implementadas como Categoria, Marca, Proveedor, Cliente, Producto, Compra, DetalleCompra, Venta, DetalleVenta y Movimiento. Todas están registradas en Django Admin.

- `python manage.py check`: sin errores.
- `python manage.py makemigrations --check --dry-run`: sin cambios pendientes.
- `python manage.py showmigrations bodega`: `0001` a `0005` aplicadas.
- `python manage.py verificar_bd`: conexión correcta, 20 tablas (10 propias y 10 internas de Django), 0 migraciones pendientes.
- `PRAGMA foreign_key_check`: ninguna violación de claves foráneas.

La migración `0005_diez_tablas_bodega` incorpora siete entidades y relaciones opcionales para conservar los registros anteriores. La carpeta de la aplicación es `Core`; mantiene la etiqueta `bodega` y el historial de migraciones.

| Tabla del negocio | Registros en la base habitual |
| --- | ---: |
| `bodega_categoria` | 3 |
| `bodega_marca` | 3 |
| `bodega_proveedor` | 3 |
| `bodega_cliente` | 5 |
| `bodega_producto` | 221 |
| `bodega_compra` | 20 |
| `bodega_detallecompra` | 20 |
| `bodega_venta` | 20 |
| `bodega_detalleventa` | 20 |
| `bodega_movimiento` | 141 |

La [guía de tablas](docs/tablas_bd.md) indica la función y ruta del Admin de cada entidad.

## Conservación y muestra completa

Antes de ampliar el esquema se creó `backups/db_antes_diez_tablas.sqlite3`: contenía 3 categorías, 201 productos y 101 movimientos. Después se compararon todas las columnas originales de esas tablas mediante `EXCEPT`, del respaldo hacia la base actual. No faltan filas ni cambió ningún valor original; se añadieron columnas y registros nuevos.

Se ejecutó una vez sobre la base habitual:

```powershell
python manage.py cargar_datos --cantidad 20 --lote 7 --semilla 42 --completo
```

La muestra añadió 20 productos, 20 compras, 20 ventas, sus respectivos detalles y 40 movimientos. Se comprobó para cada producto nuevo que el stock equivale a lo comprado menos lo vendido, que tiene un ingreso y una salida, y que ambos apuntan al documento correcto. Los registros nuevos superaron `full_clean()` y la comprobación de claves foráneas. El [informe JSON](docs/verificacion_diez_tablas.json) conserva conteos y resultados de esta auditoría.

La carga completa calcula el stock inicial neto de los productos nuevos. La edición posterior de documentos o movimientos desde Admin requiere mantener el stock manualmente, como explica el README.

## Motivos de movimientos

La migración anterior `0004_normalizar_motivos_movimientos` sustituyó el texto de Faker por **Recepción de mercadería** en los ingresos de muestra y **Por venta** en la salida existente. Antes se creó `backups/db_antes_motivos.sqlite3`; solo cambiaron los motivos, conservando identificadores, productos, tipos, cantidades y fechas.

La nueva muestra completa mantiene esos motivos: hay 120 ingresos con motivo **Recepción de mercadería** y 21 salidas con motivo **Por venta**. El historial permite filtrar por tipo y muestra el documento vinculado cuando existe. Los movimientos antiguos pueden conservar el origen vacío.

## Pruebas automáticas y revisión visual

```powershell
python manage.py test Core --noinput --verbosity 1
```

**40 pruebas aprobadas** en 25,093 segundos con Django 6.1.1, después de retirar la interfaz web propia, sin errores del comprobador de Django. Cubren CRUD, filtros y paginación en Admin, registro y renderizado de los diez modelos, totales decimales, restricciones y relaciones protegidas, coherencia del origen de movimientos, edición de detalles vinculados, cargas completas por lotes, conservación de datos y rollback del lote fallido. También comprueban que solo se publica `/admin/` y que las antiguas rutas propias devuelven 404.

La aplicación utiliza exclusivamente Django Admin. Se retiraron `Core/views.py`, `Core/forms.py`, `Core/urls.py`, las plantillas propias, el CSS del inventario y las pruebas exclusivas del CRUD web. La configuración carga las plantillas incorporadas de Django. La arquitectura se actualizó, renderizó y revisó visualmente; el diagrama de base de datos conserva los diez modelos, 53 campos y 11 relaciones de clave foránea.

Tras retirar las vistas, `verificar_bd` confirmó los mismos conteos de las diez tablas y cero migraciones pendientes. No fue necesario cambiar modelos, generar migraciones ni modificar datos. La verificación `makemigrations --check --dry-run` informó que no hay cambios de estructura.

La imagen que se entrega es [diagrama_bd.png](docs/diagrama_bd.png). La [matriz de la rúbrica](docs/rubrica_e2.md) y la [correspondencia con la referencia](docs/correspondencia_referencia.md) explican la evidencia. GitHub público, subida a la plataforma y defensa individual siguen pendientes; estas verificaciones no constituyen una calificación docente.

## Antecedente: pruebas de volumen del esquema anterior

Estos tiempos se midieron **antes de la ampliación a diez tablas**, con la modalidad básica de productos, lote de 1.000 y semilla 2026. Se usó un archivo SQLite temporal independiente y cargas consecutivas aditivas. La base habitual no recibió estos productos. No son mediciones de `--completo` ni una nueva ejecución sobre el esquema ampliado.

| Productos solicitados | Antes | Después | Diferencia comprobada | Tiempo observado |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 0 | 100 | 100 | 1,38 s |
| 1.000 | 100 | 1.100 | 1.000 | 0,08 s |
| 100.000 | 1.100 | 101.100 | 100.000 | 9,50 s |
| 1.000.000 | 101.100 | 1.101.100 | 1.000.000 | 73,92 s |

Se verificó cada diferencia de conteo de forma independiente y una muestra con `full_clean()`. Después se probaron 12 productos con ingresos mediante `--con-movimientos`, sin violaciones de claves foráneas. El detalle histórico está en [resultados_cargas.json](docs/resultados_cargas.json). Los tiempos dependen del equipo, el disco y la inicialización de Faker. [README_SEEDER.md](README_SEEDER.md) explica cómo repetir los cuatro volúmenes sobre el esquema actual en una base separada.
