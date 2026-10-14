# Evaluación 2: evidencia y guía de defensa

Music Pro aplica la gestión de base de datos y Django Admin al inventario de una bodega. Esta guía relaciona los diez indicadores de la evaluación con el código, los documentos y las acciones que debe demostrar el estudiante. **No asigna una nota:** el docente evalúa el funcionamiento y la explicación individual.

## Alcance de la evaluación

La pauta **E2 Evaluacion_inv_Caso_Semestral_Music_pro_U2 Backend.pdf**, p.8, distingue las etapas:

- **E2:** conexión a la base de datos y administración mediante Django Admin. Las pp.9-11 detallan modelos, diagrama, migraciones, datos con Faker, consultas y CRUD en Admin.
- **E3:** funciones CRUD propias de la aplicación y mecanismos de seguridad. El CRUD web de este proyecto es material complementario que permite practicar lo observado en el proyecto de referencia.
- **Etapa de API:** Django REST Framework, JSON y JWT aparecen en los objetivos semestrales, pp.2-4, y en la evaluación del 14 de diciembre de 2026, p.5.

La presentación **Music pro  - Presentacion.pdf**, pp.15-16, describe la bodega principal: ingreso, almacenamiento, salida y trazabilidad de productos. Esa área fundamenta los modelos de este proyecto. Las áreas de tienda, courier y pagos de las pp.17-22 pertenecen al contexto general del caso.

La pauta E2 indica trabajo individual y defensa en el computador del estudiante, pp.6 y 9. En el calendario, p.5, E2 figura para el **14 de octubre de 2026**, con ponderación del **25%**. Los documentos no fijan motor específico de base de datos ni nombre de rama Git. **El estudiante confirmó además una indicación del profesor de diez tablas propias del negocio.** El proyecto la incorpora con siete modelos nuevos y conserva los tres iniciales; [este listado](tablas_bd.md) permite ubicarlas. Este requisito adicional es distinto de los diez indicadores de evaluación.

## Matriz de los diez indicadores

Fuente: pauta PDF p.12 y archivo **E2 Escala_Apreciacion_U2 Backend.xlsx**, hoja `Escala de apreciacion`. Los números están en `C12:C21` y los enunciados en `D12:D21`.

| N.º / celda | Requisito | Evidencia del proyecto | Demostración y comprobación |
| --- | --- | --- | --- |
| 1 / D12 | Configurar correctamente la conexión y verificar su funcionamiento. | [Configuración SQLite](../musicpro_backend/settings.py), [diagnóstico de BD](../Core/management/commands/verificar_bd.py), [README, apartado 1](../README.md). | Ejecutar `python manage.py verificar_bd`; explicar motor, archivo, tablas, conteos y migraciones pendientes. |
| 2 / D13 | Definir y relacionar modelos, atributos, tipos, claves y relaciones. | [Modelos](../Core/models.py), [diagrama y diccionario de datos](diagrama_bd.md). | Explicar las diez entidades; identificar PK, campos únicos, FK y claves compuestas. Seguir Proveedor → Compra → DetalleCompra → Producto y Cliente → Venta → DetalleVenta → Movimiento. |
| 3 / D14 | Generar y ejecutar migraciones, representar la BD y generar datos con Faker verificando su almacenamiento. | [Historial de migraciones](../Core/migrations/), [imagen del modelo](diagrama_bd.png), [generador Faker](../Core/management/commands/cargar_datos.py), [resultados de cargas](resultados_cargas.json), [verificación](../VERIFICACION.md). | Mostrar `showmigrations bodega`, explicar creación y cambios posteriores, comparar modelos y diagrama, cargar datos y verificar la diferencia de conteos. |
| 4 / D15 | Configurar acceso a Admin y registrar los modelos requeridos. | [Ruta de administración](../musicpro_backend/urls.py), [registro de modelos](../Core/admin.py), [README, apartado 5](../README.md). | Iniciar servidor, ingresar con la cuenta creada mediante `createsuperuser` y mostrar los diez modelos de Bodega. |
| 5 / D16 | Configurar la visualización de los modelos para facilitar la administración. | [Configuración de Admin](../Core/admin.py). | Mostrar columnas, filtros, búsquedas, formularios, autocompletado y personalización del sitio. Explicar la comparación del stock con el mínimo de cada producto. |
| 6 / D17 | Crear registros en Admin con los campos definidos. | Formularios generados desde los [modelos](../Core/models.py) y [pruebas del CRUD](../Core/tests.py). | Crear una categoría y un producto de demostración. Consultar el registro con el ORM para comprobar su almacenamiento. |
| 7 / D18 | Consultar registros en Admin y comprobar que correspondan a la BD. | [Búsquedas y filtros](../Core/admin.py), [pruebas de consultas](../Core/test_database.py). | Buscar el código del producto en Admin y consultar el mismo código con `Producto.objects.filter(...)`. Comparar los valores. |
| 8 / D19 | Modificar registros y verificar su actualización en la BD. | Formulario de edición de Admin y [prueba de actualización](../Core/tests.py). | Modificar cantidad y ubicación del producto, guardar y repetir la consulta ORM. Mostrar su nuevo estado de stock. |
| 9 / D20 | Eliminar registros y comprobar su eliminación en la BD. | Eliminación de Admin, [relaciones protegidas](../Core/models.py), [pruebas de borrado e integridad](../Core/test_database.py). | Borrar los registros de demostración en el orden movimiento, producto, categoría. Comprobar con `exists()` que desaparecieron. Explicar qué impide `PROTECT`. |
| 10 / D21 | Demostrar y explicar Admin relacionando sus acciones con la gestión de los datos. | [Guía de comandos](../README.md), esta guía y [verificación realizada](../VERIFICACION.md). | Explicar qué tabla afecta cada operación y cómo se comprueba el resultado. Responder las preguntas de práctica que aparecen abajo. |

Las pruebas automatizadas aportan evidencia repetible. La defensa requiere además ejecutar el proyecto y explicar personalmente las decisiones. Consulta [VERIFICACION.md](../VERIFICACION.md) para conocer las comprobaciones realizadas y sus resultados; no deben darse por aprobadas comprobaciones que aún no se ejecuten después de nuevos cambios.

## Diagramas para la entrega

La pauta E2, p.9 apartado 3 y p.11, exige un **diagrama de base de datos** con entidades/tablas, atributos, claves y relaciones, correspondiente a los modelos Django. El indicador 3 de la rúbrica también lo incluye.

- [Diagrama de base de datos en PNG](diagrama_bd.png): imagen para adjuntar a la plataforma.
- [Versión SVG](diagrama_bd.svg) y [diccionario con Mermaid](diagrama_bd.md): permiten revisar con claridad las relaciones y actualizar la documentación.
- [Arquitectura de la aplicación](diagrama_arquitectura.png) y [flujo de carga con Faker](flujo_carga.png): diagramas complementarios para explicar el recorrido de las solicitudes y la generación de datos.

La pauta no exige formalmente diagramas de arquitectura, flujo, casos de uso o secuencia para E2. Cuando se modifique un modelo, hay que conservar la correspondencia entre código, migración, diagrama y base de datos actualizada.

## Guion de defensa: CRUD en Django Admin

Activa el entorno y sigue primero la instalación, las migraciones y la creación del superusuario descritas en [README.md](../README.md). Ejecuta:

```powershell
python manage.py check
python manage.py showmigrations bodega
python manage.py verificar_bd
python manage.py runserver
```

`check` revisa configuración; `showmigrations` muestra el historial aplicado; `verificar_bd` consulta la conexión y las tablas reales; `runserver` inicia el servidor local. Abre `http://127.0.0.1:8000/admin/`. Mantén otra terminal con el mismo entorno virtual para las consultas ORM.

### 1. Crear y comprobar

En **Categorías**, crea `Demostración E2`. En **Productos**, crea un registro con estos valores:

| Campo | Valor de demostración |
| --- | --- |
| Código | `DEFENSA-E2-001` |
| Nombre | `Guitarra de demostración` |
| Categoría | `Demostración E2` |
| Ubicación | `Pasillo 1 - Estante 1` |
| Cantidad | `10` |
| Stock mínimo | `5` |

Utiliza un código libre si ya existe uno de una demostración anterior. Consulta el registro almacenado:

```powershell
python manage.py shell -c "from Core.models import Producto; print(list(Producto.objects.filter(codigo='DEFENSA-E2-001').values('codigo', 'nombre', 'categoria__nombre', 'ubicacion', 'cantidad', 'stock_minimo')))"
```

`filter` selecciona el registro y `values` obtiene sus campos y el nombre de la categoría relacionada directamente desde la base de datos.

### 2. Consultar y filtrar

Busca `DEFENSA-E2-001` en Admin, filtra por su categoría y abre la ficha. Compara lo mostrado con la consulta anterior. El producto todavía está sobre el mínimo, porque `10 > 5`.

### 3. Modificar y comprobar

Cambia la ubicación a `Pasillo 2 - Estante 3` y la cantidad a `3`. Guarda y repite la consulta ORM. El producto debe aparecer en el filtro de stock crítico porque `3 <= 5`. Explica que se actualizó la fila existente, conservando su identificador.

### 4. Relacionar y validar

Crea un movimiento para ese producto: tipo `INGRESO`, cantidad `3`, motivo `Demostración individual E2`. Muestra la relación, la búsqueda por código del producto y el filtro de tipo. Intenta guardar un movimiento con cantidad `0` para mostrar la validación del formulario.

**El stock se administra manualmente en esta etapa.** Crear, editar o eliminar un movimiento no actualiza automáticamente `Producto.cantidad`. El movimiento registra información de trazabilidad; el stock se modifica en el producto. Explica esta regla al presentar ambos registros.

### 5. Eliminar y comprobar

Intenta eliminar el producto con el movimiento asociado y muestra la protección de la relación. Elimina después el movimiento de demostración, el producto y finalmente la categoría. Comprueba:

```powershell
python manage.py shell -c "from Core.models import Categoria, Producto; print('Producto existe:', Producto.objects.filter(codigo='DEFENSA-E2-001').exists()); print('Categoría existe:', Categoria.objects.filter(nombre='Demostración E2').exists())"
```

Ambas consultas deben devolver `False` cuando esos registros de demostración se hayan eliminado. Usa únicamente los registros creados para esta práctica.

## Faker: las cuatro cargas de la pauta

La pauta PDF, p.10, indica probar con el docente cargas de **100, 1.000, 100.000 y 1.000.000** y comprobar su almacenamiento. Los comandos, su propósito y el procedimiento para usar bases SQLite de ensayo están en [README.md, apartado 6](../README.md).

Cada ejecución de `cargar_datos --cantidad N` añade **N productos nuevos**. Los catálogos y los movimientos/documentos opcionales son registros adicionales. La modalidad `--completo` permite mostrar información relacionada en las diez tablas, y la básica permite medir los cuatro volúmenes sin crear millones de documentos. Ejecutar los cuatro volúmenes consecutivamente sobre una tabla vacía añade 1.101.100 productos; para comparar cada volumen por separado, usa un archivo de ensayo nuevo para cada carga.

Para cada volumen, presenta la ruta de la BD, el conteo inicial, el comando utilizado, el conteo final y la diferencia. Los datos son ficticios: Faker genera ejemplos y no aporta información real de clientes, proveedores o inventario. La semilla ayuda a reproducir los valores; los códigos distinguen cada ejecución.

## Preguntas para practicar la explicación

| Pregunta | Idea que debes poder explicar con tu código |
| --- | --- |
| ¿Qué base de datos utiliza el proyecto? | SQLite; motor y ruta configurados en `DATABASES`; la variable de ensayo permite elegir otro archivo. |
| ¿Qué diferencia hay entre modelo, migración y tabla? | El modelo define la estructura en Python; la migración registra su cambio; la tabla es la estructura aplicada y almacenada en SQLite. |
| ¿Para qué sirve `makemigrations` y para qué sirve `migrate`? | El primero genera el historial de cambios; el segundo los aplica a la base. |
| ¿Por qué se conserva la etiqueta `bodega` si la carpeta se llama `Core`? | La etiqueta mantiene los nombres históricos de tablas y migraciones, mientras `Core` es el módulo de Python. |
| ¿Qué son PK, FK y un campo único? | Identidad del registro, referencia a otra tabla y restricción contra duplicados, respectivamente. Mostrar ejemplos en el diagrama. |
| ¿Qué evita `PROTECT`? | El ORM impide borrar una categoría utilizada o un producto con movimientos asociados. |
| ¿Cómo sabes que Admin guardó un cambio? | Consultar el mismo registro por código desde el ORM y comparar sus valores. |
| ¿Qué diferencia existe entre filtro y búsqueda? | El filtro selecciona una condición definida; la búsqueda encuentra coincidencias en los campos configurados. |
| ¿Por qué el movimiento no cambia el stock? | La versión actual registra movimientos y administra la cantidad del producto de forma manual. |
| ¿Por qué Faker utiliza lotes? | Para limitar los objetos mantenidos en memoria y agrupar inserciones al probar hasta un millón de productos. |
| ¿Qué ocurre si se interrumpe una carga? | Los lotes confirmados permanecen; el lote fallido se revierte. Una nueva ejecución añade otra carga. |
| ¿Cómo se valida una carga? | Contar los productos de esa ejecución y comparar los totales, además de consultar una muestra y sus relaciones. |

La pauta PDF, p.6, exige demostrar comprensión del proyecto y del código. Practica estas respuestas recorriendo tus propios archivos y ejecutando los comandos.

## Puntaje y entregables pendientes de la instancia docente

El archivo de rúbrica define diez indicadores. En `Escala de apreciacion`, las celdas `E11`, `F11` y `G11` fijan **Excelente: 10**, **Bueno: 5** e **Insatisfactorio: 0**. `H12:H21` calcula cada indicador y `H24` suma un máximo de **100 puntos**. Las marcas `x` prellenadas en el archivo adjunto forman parte de esa referencia y no constituyen una calificación comprobada de este proyecto.

La hoja `Poderación 60%` contiene una imagen de la tabla de notas, no valores de celda: muestra exigencia del 60%, nota mínima 1,0, aprobación con 60 puntos equivalente a 4,0 y nota máxima 7,0. La decisión de valoración de cada indicador corresponde al docente.

La pauta PDF, p.11, pide:

- Proyecto funcional, modelos, migraciones, BD actualizada, Admin y datos de prueba disponibles para la defensa.
- **Repositorio GitHub público con el código y el último commit.** Verificar que incluya configuración, modelos, migraciones, administración, dependencias y documentación. Comprobar que otra persona pueda abrir el enlace.
- **Subir la imagen del modelo de base de datos y el enlace público a la plataforma.** La imagen preparada es [diagrama_bd.png](diagrama_bd.png).
- Defensa individual y explicación de las decisiones de desarrollo.

La documentación y los archivos preparados no acreditan por sí mismos la publicación en GitHub, la entrega en la plataforma ni la realización de la defensa. Esas acciones deben comprobarse al entregar.

## Fuentes de los requisitos

Los adjuntos originales se consultaron sin modificarlos. Sus nombres y localizadores permiten volver a la evidencia sin depender de rutas particulares del computador:

0. **Aclaración del estudiante en este chat:** el profesor pidió diez tablas propias del negocio, además de los diez indicadores; es la fuente del número de entidades requerido.
1. **E2 Evaluacion_inv_Caso_Semestral_Music_pro_U2 Backend.pdf**: p.5 calendario; p.6 defensa; p.8 separación E2/E3; pp.9-10 contenidos y cargas; p.11 entregables; p.12 indicadores.
2. **E2 Escala_Apreciacion_U2 Backend.xlsx**: hoja `Escala de apreciacion`, `C12:D21` indicadores, `E11:G11` escala, `H12:H21` cálculo y `H24` total; hoja `Poderación 60%`, imagen de conversión de puntaje a nota.
3. **Music pro  - Presentacion.pdf**: pp.15-16 necesidades de la bodega; pp.17-22 otras áreas del caso semestral.
