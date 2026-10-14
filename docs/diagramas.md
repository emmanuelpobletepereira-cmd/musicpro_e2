# Diagramas de Music Pro

**Sube [diagrama_bd.png](diagrama_bd.png)**: es una sola imagen del modelo de base de datos, exigida por la pauta E2 (páginas 9 y 11). Representa los diez modelos propios del negocio solicitados adicionalmente por el profesor y corresponde a los campos implementados en Django. Las diez tablas de usuarios, permisos y sesiones se explican por separado en [tablas_bd.md](tablas_bd.md).

| Diagrama | Uso | Archivos |
| --- | --- | --- |
| Base de datos | Imagen para la entrega: diez entidades, todos los campos, PK, FK, UK y cardinalidades | [PNG](diagrama_bd.png), [SVG](diagrama_bd.svg), [diccionario y Mermaid](diagrama_bd.md) |
| Arquitectura | Apoyo para explicar configuración, Admin, comandos, ORM y SQLite | [PNG](diagrama_arquitectura.png), [SVG](diagrama_arquitectura.svg) |
| Carga con Faker | Apoyo para explicar modalidades, lotes, transacciones y verificación | [PNG](flujo_carga.png), [SVG](flujo_carga.svg) |

La pauta solicita el diagrama de base de datos; los dos esquemas de apoyo son complementarios para la defensa. Los diagramas describen esta implementación propia de Music Pro.

## Arquitectura

![Arquitectura de Music Pro](diagrama_arquitectura.png)

```mermaid
flowchart TD
    persona[Usuario y navegador] --> admin[Django Admin: acceso staff y permisos]
    configuracion[Configuración y URL /admin/] --> admin
    admin --> modelos[ORM: diez modelos de bodega]
    comandos[Comandos: Faker y diagnóstico] --> modelos
    migraciones[Migraciones Django] --> sqlite[(SQLite: diez tablas de negocio + diez internas)]
    modelos --> sqlite
```

## Generación de datos

![Carga por lotes y verificación de Faker](flujo_carga.png)

```mermaid
flowchart TD
    opciones[Validar cantidad, lote y alias] --> faker[Preparar Faker y catálogos]
    faker --> lote[Construir lote de productos]
    lote --> modo{Modalidad}
    modo -- Básica --> productos[Solo productos]
    modo -- con-movimientos --> ingresos[Productos + ingreso inicial]
    modo -- completo --> documentos[Productos + compras/ventas + detalles + ingresos/salidas]
    productos --> transaccion[Guardar lote en transacción]
    ingresos --> transaccion
    documentos --> transaccion
    transaccion --> pendientes{¿Quedan productos?}
    pendientes -- Sí --> lote
    pendientes -- No --> verificar[Consultar registros guardados y relaciones según modalidad]
    verificar --> resultado[Mostrar antes, después, nuevos y tiempo]
    transaccion -. Fallo .-> fallo[Revertir lote actual; conservar lotes confirmados]
```

Las cargas se suman y `--cantidad N` siempre cuenta productos nuevos. `--con-movimientos` añade un ingreso por producto; `--completo` añade un ingreso y una salida por producto junto con sus documentos, y calcula stock neto para esos productos nuevos. No actualiza automáticamente el stock cuando después editas documentos/movimientos desde Admin. Consulta [README_SEEDER.md](../README_SEEDER.md) para ejemplos y ensayos independientes.
