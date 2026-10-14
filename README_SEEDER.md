# Datos ficticios con Faker

El comando propio [cargar_datos.py](Core/management/commands/cargar_datos.py) añade productos del inventario y comprueba que hayan quedado guardados. Con `--completo` genera también compras, ventas, sus detalles y movimientos para poblar las diez tablas propias del negocio. No utiliza los generadores de empleados ni vehículos del material de apoyo. Esta guía acompaña la sección 6 del [README principal](README.md).

## Instalar y comprobar Faker

Activa el entorno Python 3.12 preparado para este proyecto y ejecuta:

```powershell
python -m pip install -r requirements.txt
python -m pip check
python -m pip show Faker
python -c "from faker import Faker; print(Faker('es_CL').name())"
```

| Comando | Propósito |
| --- | --- |
| `pip install -r requirements.txt` | Instalar las cinco dependencias fijadas, incluida `Faker==40.40.0` |
| `pip check` | Detectar incompatibilidades o dependencias faltantes |
| `pip show Faker` | Mostrar la versión y ubicación instalada |
| `python -c ...` | Confirmar que la importación funciona generando un nombre chileno ficticio |

Si solo falta Faker en un entorno ya preparado, el comando específico es `python -m pip install Faker==40.40.0`. Para reconstruir el proyecto completo utiliza siempre `requirements.txt`. Faker se importa en Python con `from faker import Faker`; no se agrega a `INSTALLED_APPS`.

## Primera carga

```powershell
python manage.py migrate
python manage.py verificar_bd
python manage.py cargar_datos --cantidad 100 --semilla 42
python manage.py verificar_bd
```

`migrate` prepara las tablas. El primer diagnóstico identifica el archivo SQLite y sus conteos iniciales. La carga añade 100 productos y verifica los códigos creados en esa ejecución. El segundo diagnóstico permite comparar los registros almacenados y confirmar que la base sigue actualizada.

Se reutilizan o crean tres categorías: `Instrumentos`, `Audio` y `Accesorios`. Faker elige un artículo del catálogo musical y genera su variante, pasillo, estante, cantidad y stock mínimo. Es información de prueba.

## Opciones disponibles

```powershell
python manage.py cargar_datos --help
```

| Opción | Comportamiento |
| --- | --- |
| `--cantidad N` | Número de productos nuevos; de 1 a 1.000.000 |
| `--lote N` | Productos por grupo de trabajo; de 1 a 10.000, con 1.000 por defecto |
| `--semilla N` | Repetir valores aleatorios de Faker con las mismas opciones y versión |
| `--con-movimientos` | Añadir un movimiento de ingreso inicial por producto generado |
| `--completo` | Generar marca/proveedor/cliente, compra y detalle, venta y detalle, ingreso y salida; el stock nuevo es recibido menos vendido |
| `--database default` | Elegir el alias de conexión configurado |

Cada ejecución añade registros. Una semilla fija reproduce los valores ficticios, pero **no reproduce los códigos**: el prefijo UUID cambia para evitar duplicados entre cargas. Repetir el comando con la misma semilla no actualiza ni elimina los productos anteriores.

```powershell
python manage.py cargar_datos --cantidad 100 --lote 1000 --semilla 42 --con-movimientos
```

Este ejemplo añade 100 productos y 100 movimientos. Cada producto tiene stock entre 1 y 100 y su ingreso inicial registra la misma cantidad. Sin movimientos, el stock generado puede ser de 0 a 100. Las tres categorías no se incluyen en `--cantidad`.

Los ingresos se registran con el motivo **Recepción de mercadería**, sin mencionar la herramienta generadora en la pantalla. Una salida por venta se registra como **SALIDA / Por venta**. La opción `--con-movimientos` genera ingresos iniciales; no transforma esos ingresos en ventas.

## Carga completa de las diez tablas

```powershell
python manage.py migrate
python manage.py cargar_datos --cantidad 100 --lote 1000 --semilla 42 --completo
python manage.py verificar_bd
```

`migrate` prepara las diez tablas. La carga completa añade 100 productos, 100 compras, 100 detalles de compras, 100 ventas, 100 detalles de ventas y 200 movimientos. Las categorías, marcas, proveedores y clientes son catálogos pequeños que se reutilizan; no se generan 100 contactos por cada carga. Cada compra enlaza un proveedor; cada venta, un cliente; sus detalles identifican el producto y su valor unitario.

Los ingresos dicen **Recepción de mercadería** y las salidas **Por venta**. Sus referencias permiten llegar al documento de origen. Para cada producto nuevo, la cantidad recibida menos la vendida coincide con su stock generado. El diagnóstico muestra los conteos de las diez tablas y permite comprobar que todas tienen información.

`--completo` ya incluye los movimientos, por lo que no necesitas añadir `--con-movimientos`. El modo completo no cambia registros anteriores ni implementa una actualización automática del stock al editar documentos o movimientos desde Admin. Faker crea contactos ficticios; no se usan datos personales reales.

## Demostrar los cuatro volúmenes

La pauta solicita 100, 1.000, 100.000 y 1.000.000 datos. En este proyecto, el volumen se refiere a **productos nuevos**. Para medir cada carga por separado, utiliza un archivo SQLite nuevo por ensayo:

```powershell
$cantidadEnsayo = 100
$env:MUSICPRO_DB_PATH = Join-Path (Get-Location) ("ensayo-" + $cantidadEnsayo + "-" + (Get-Date -Format "yyyyMMdd-HHmmss-fff") + ".sqlite3")
python manage.py migrate
python manage.py verificar_bd
Measure-Command { python manage.py cargar_datos --cantidad $cantidadEnsayo --lote 1000 --semilla 42 }
python manage.py verificar_bd
```

Repite el bloque completo cambiando `$cantidadEnsayo` a `1000`, `100000` y `1000000`. La variable de entorno selecciona la base solo en esa terminal; `migrate` crea sus tablas; el primer diagnóstico debe mostrar cero productos; `Measure-Command` mide la ejecución y el último diagnóstico debe mostrar el volumen pedido. No elimines las bases habituales para realizar esta prueba.

| Ensayo | Productos al inicio en el archivo nuevo | Productos esperados al terminar |
| --- | --- | --- |
| 100 | 0 | 100 |
| 1.000 | 0 | 1.000 |
| 100.000 | 0 | 100.000 |
| 1.000.000 | 0 | 1.000.000 |

Si ejecutas los cuatro volúmenes sobre el mismo archivo vacío, terminarás con **1.101.100 productos**. Para revisar cualquier ensayo en Admin, crea su superusuario y arranca el servidor en la misma terminal. Detén primero el servidor anterior para evitar consultar una base distinta de la ensayada.

Al terminar, vuelve a la conexión habitual:

```powershell
Remove-Item Env:MUSICPRO_DB_PATH
python manage.py verificar_bd
```

Elimina la variable de entorno de la terminal; no elimina los archivos ni sus registros. El diagnóstico debe volver a identificar `db.sqlite3`.

## Qué sucede dentro del comando

![Generación, guardado y verificación por lotes](docs/flujo_carga.png)

El comando valida los argumentos y genera un lote de objetos en memoria. `bulk_create` inserta ese grupo; una transacción guarda juntos los productos y sus movimientos o documentos/detalles según la modalidad. Al terminar, consulta el rango de códigos exclusivo de la ejecución y comprueba el número almacenado. La base conserva las restricciones de claves únicas, relaciones y cantidades válidas.

El límite del lote controla cuántos objetos se preparan juntos, por lo que no se construye una lista con un millón de productos. Durante la generación se desactiva temporalmente `DEBUG` para evitar acumular el historial SQL. `bulk_create` no llama al `save()` individual ni a la validación de un formulario; el generador debe producir valores válidos.

Si se interrumpe la carga, los lotes confirmados permanecen y el lote que estaba en una transacción se revierte. Una nueva ejecución añade otra carga, no continúa automáticamente la anterior. Conserva el identificador que muestra el comando para reconocer esa ejecución.

Para la defensa, explica la diferencia entre la cantidad de productos y el tamaño del lote; muestra la ruta de la base activa, los conteos iniciales/finales y una búsqueda por código en Admin. Con `--completo`, un millón de productos añade también un millón de compras, detalles de compras, ventas y detalles de ventas, más dos millones de movimientos. Prueba primero una carga pequeña para mostrar las relaciones; los ensayos masivos básicos no verifican por sí solos el rendimiento de esa modalidad. Los tiempos dependen del equipo: consulta [VERIFICACION.md](VERIFICACION.md) para distinguir resultados ejecutados de comandos propuestos. El movimiento de ingreso inicial registra el stock; los movimientos posteriores siguen sin modificar automáticamente `Producto.cantidad`.
