# Dónde están las diez tablas propias de Music Pro

La base habitual es [db.sqlite3](../db.sqlite3). Las tablas se almacenan dentro de ese archivo; cada tabla no es un archivo independiente. La conexión se configura en [settings.py](../musicpro_backend/settings.py).

## Las diez tablas del negocio

Los diez modelos se definen en [Core/models.py](../Core/models.py) y se registran en [Core/admin.py](../Core/admin.py). Inicia el servidor con `python manage.py runserver` y abre [Django Admin](http://127.0.0.1:8000/admin/): aparecen dentro de **Bodega**. Necesitas una cuenta administradora.

| N.º | Tabla SQLite | Modelo Django | Función | Ruta del Admin |
| --- | --- | --- | --- | --- |
| 1 | `bodega_categoria` | `Categoria` | Clasificar instrumentos, audio y accesorios | `/admin/bodega/categoria/` |
| 2 | `bodega_marca` | `Marca` | Identificar fabricante y país de los productos | `/admin/bodega/marca/` |
| 3 | `bodega_proveedor` | `Proveedor` | Identificar la contraparte de cada compra | `/admin/bodega/proveedor/` |
| 4 | `bodega_cliente` | `Cliente` | Identificar la contraparte de cada venta | `/admin/bodega/cliente/` |
| 5 | `bodega_producto` | `Producto` | Código, clasificación, ubicación y existencias | `/admin/bodega/producto/` |
| 6 | `bodega_compra` | `Compra` | Encabezado: número, proveedor, fecha y observaciones | `/admin/bodega/compra/` |
| 7 | `bodega_detallecompra` | `DetalleCompra` | Productos, cantidades y costos de una compra | `/admin/bodega/detallecompra/` |
| 8 | `bodega_venta` | `Venta` | Encabezado: número, cliente, fecha y observaciones | `/admin/bodega/venta/` |
| 9 | `bodega_detalleventa` | `DetalleVenta` | Productos, cantidades y precios de una venta | `/admin/bodega/detalleventa/` |
| 10 | `bodega_movimiento` | `Movimiento` | Ingresos/salidas, motivo y detalle documental de origen | `/admin/bodega/movimiento/` |

No se cuentan modelos ajenos al dominio para completar el número. Las siete entidades añadidas representan marcas, contactos y documentos reales del proceso de una bodega. Los documentos separan encabezado y detalle para permitir varios productos por compra o venta; los movimientos permiten seguir el ingreso o salida de cada producto.

## Las diez tablas internas de Django

| Tabla | Función |
| --- | --- |
| `auth_user` | Cuentas de usuarios |
| `auth_group` | Grupos de usuarios |
| `auth_permission` | Permisos por modelo y acción |
| `auth_user_groups` | Relación de usuarios con grupos |
| `auth_user_user_permissions` | Permisos individuales |
| `auth_group_permissions` | Permisos de grupos |
| `django_admin_log` | Historial de acciones del Admin |
| `django_content_type` | Registro de los tipos de modelos |
| `django_session` | Sesiones de autenticación |
| `django_migrations` | Registro de migraciones aplicadas |

Después de aplicar todas las migraciones hay **20 tablas: 10 propias del negocio y 10 internas**. SQLite mantiene además `sqlite_sequence`, una tabla técnica que no se considera entidad de bodega ni aparece en la introspección habitual de Django.

## Comprobarlo desde PowerShell

Dentro de la carpeta que contiene `manage.py`, con el entorno activado:

```powershell
python manage.py migrate
python manage.py verificar_bd
python manage.py shell -c "from django.apps import apps; from django.db import connection; modelos=list(apps.get_app_config('bodega').get_models()); print('Modelos de negocio:', len(modelos)); print('\n'.join(m._meta.db_table for m in modelos)); print('Tablas presentes:', len(connection.introspection.table_names()))"
```

`migrate` aplica la estructura completa. `verificar_bd` consulta conexión, tablas y conteos. El último comando toma los modelos reales desde Django y enumera sus tablas: debe informar diez modelos de negocio y veinte tablas presentes en la base migrada. Si no activaste el entorno, reemplaza `python` por `.\.venv\Scripts\python.exe`.

Para añadir ejemplos relacionados en las diez tablas:

```powershell
python manage.py cargar_datos --cantidad 100 --semilla 42 --completo
python manage.py verificar_bd
```

La carga añade registros ficticios sin borrar los existentes. Reutiliza pequeños catálogos y genera compras/ventas con sus detalles y movimientos. Las salidas de venta muestran **Por venta**; los ingresos, **Recepción de mercadería**.

## Requisito del profesor y archivo que se sube

La rúbrica enumera diez indicadores de evaluación. **El estudiante confirmó que el profesor también exige diez tablas propias del negocio**; el esquema implementado incorpora ambas condiciones, sin contar tablas de autenticación como entidades de bodega.

La pauta E2, páginas 9 y 11, pide la imagen de **un diagrama de base de datos**. Sube [diagrama_bd.png](diagrama_bd.png), que representa juntas las diez tablas, sus atributos, claves y relaciones. [El diccionario](diagrama_bd.md) y [el SVG](diagrama_bd.svg) sirven para revisar sus detalles. Los diagramas de arquitectura y Faker son apoyos para explicar el proyecto.
