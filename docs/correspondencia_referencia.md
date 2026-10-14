# Decisiones de adaptación al caso Music Pro

`django-examples-main` se utiliza como material de aprendizaje para conservar sus elementos técnicos y su recorrido de estudio. Music Pro desarrolla diez entidades propias para catálogos, compras, ventas, detalles y trazabilidad de bodega. No se incorporan los modelos de empleados, vehículos, biblioteca, hospital o comercio del material de apoyo.

Los nombres de archivo de la primera columna son rutas relativas a la carpeta entregada `django-examples-main/django-examples-main`. Permiten comprobar de dónde procede cada idea pedagógica; el equivalente indica dónde se implementa en Music Pro.

| Elemento observado en el material de apoyo | Equivalente de Music Pro | Decisión de adaptación |
| --- | --- | --- |
| `requirements.txt`: cinco dependencias con versiones fijadas | [requirements.txt](../requirements.txt) | Conservar las cinco utilidades y versiones solicitadas; no añadir paquetes para el CRUD ni para los diagramas |
| `manage.py`, `sistema/settings.py`, `sistema/urls.py` | [manage.py](../manage.py), [settings.py](../musicpro_backend/settings.py), [urls.py](../musicpro_backend/urls.py) | Mantener la estructura Django y utilizar la configuración propia del inventario |
| Aplicaciones de dominio separadas, como `rrhh` y `automotora_basica` | [Core/apps.py](../Core/apps.py) | Mantener una aplicación de negocio que responda al caso Music Pro; conservar la etiqueta `bodega` por compatibilidad con las tablas existentes |
| Modelos relacionados en `rrhh/models.py` y `automotora_basica/models.py` | [Core/models.py](../Core/models.py) | Diez entidades de bodega relacionadas mediante claves propias, detalles de documentos, reglas de cantidad/precio y relaciones protegidas |
| Historial en `rrhh/migrations/` y `automotora_basica/migrations/` | [Core/migrations/](../Core/migrations/) | Conservar la creación inicial y los cambios posteriores; no sustituir el historial por una base precargada |
| Personalización en `rrhh/admin.py`, `automotora_basica/admin.py` y `README_ADMIN.md` | [Core/admin.py](../Core/admin.py), [README_ADMIN.md](../README_ADMIN.md) | Listados, filtros, búsquedas, secciones de formulario, identificadores de solo lectura y nombres propios de bodega |
| Comandos `rrhh/management/commands/seed_empleado.py` y `automotora_basica/management/commands/seed_vehiculos.py` | [cargar_datos.py](../Core/management/commands/cargar_datos.py) | Generación musical con Faker, cantidad configurable, lotes, semilla y modalidad completa de compras/ventas con sus movimientos |
| Explicación de consultas ORM y datos en `README_SEEDER.md` | [verificar_bd.py](../Core/management/commands/verificar_bd.py), [README_SEEDER.md](../README_SEEDER.md) | Verificar conexión real, tablas y conteos; comprobar cada carga por sus códigos únicos |
| Ruta de aprendizaje de `readme.md`, `README_ADMIN.md`, `README_MIGRACIONES.md`, `README_SEEDER.md` | [README.md](../README.md) y las tres guías temáticas | Mantener material para ejecutar y explicar el proyecto, redactado para el caso de la evaluación |

## Dependencias conservadas

| Paquete y versión | Uso |
| --- | --- |
| `asgiref==3.12.1` | Integración síncrona/asíncrona de Django |
| `Django==6.1.1` | Aplicación, modelos, consultas, migraciones, Admin, formularios y permisos |
| `Faker==40.40.0` | Datos ficticios con configuración `es_CL` |
| `sqlparse==0.6.0` | Herramientas de procesamiento de SQL utilizadas por Django |
| `tzdata==2026.5` | Zonas horarias, incluida `America/Santiago` en Windows |

La instalación se realiza con `python -m pip install -r requirements.txt` y se revisa con `python -m pip check`. SQLite viene con Python. Los diagramas se entregan como archivos PNG/SVG y no necesitan una dependencia nueva para abrirlos.

## Relación con la evaluación

La pauta E2, páginas 8–11, concentra la demostración en conexión, modelos, diagrama, migraciones, Admin y datos ficticios. La interfaz utiliza exclusivamente Django Admin: los formularios, listados y operaciones CRUD los proporciona el administrador de Django. No se implementan vistas, formularios ni plantillas propias. No se incorpora Django REST Framework ni JWT, que pertenecen a una etapa posterior y tampoco están en las cinco dependencias indicadas.

El [diagrama de entidades y relaciones](diagrama_bd.png) representa las diez tablas de negocio solicitadas adicionalmente por el profesor y es la imagen requerida para la entrega. [La arquitectura](diagrama_arquitectura.png) y [el flujo Faker](flujo_carga.png) apoyan la explicación. La [matriz de evidencias](rubrica_e2.md) relaciona el código con los diez indicadores de la escala, sin convertir las marcas precargadas del archivo de rúbrica en una calificación obtenida.

Las decisiones centrales siguen siendo explicables: SQLite para una base local, claves foráneas obligatorias y referencias opcionales justificadas, `PROTECT` para conservar relaciones, stock administrado manualmente, migraciones acumulativas y carga masiva por lotes. Los resultados comprobados están separados de las instrucciones de demostración en [VERIFICACION.md](../VERIFICACION.md).
