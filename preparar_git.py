"""Importa el estado actual de Music Pro en 15 commits locales por componentes."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys


RAIZ = Path(__file__).resolve().parent
GRUPOS = [
    ('Configurar dependencias y archivos excluidos', [
        '.gitignore', 'musicpro_backend/.gitignore', 'requirements.txt', 'servidor.bat',
    ]),
    ('Configurar el proyecto Django y la conexion SQLite', [
        'manage.py', 'musicpro_backend/__init__.py',
        'musicpro_backend/settings.py', 'musicpro_backend/urls.py',
        'musicpro_backend/asgi.py', 'musicpro_backend/wsgi.py',
    ]),
    ('Registrar la aplicacion de bodega y sus rutas', [
        'Core/__init__.py', 'Core/apps.py', 'Core/urls.py',
    ]),
    ('Definir los diez modelos del negocio y sus relaciones', ['Core/models.py']),
    ('Incorporar el historial de migraciones de la bodega', [
        'Core/migrations/__init__.py', 'Core/migrations/0001_initial.py',
        'Core/migrations/0002_producto_stock_minimo.py',
        'Core/migrations/0003_integridad_movimientos.py',
        'Core/migrations/0004_normalizar_motivos_movimientos.py',
        'Core/migrations/0005_diez_tablas_bodega.py',
    ]),
    ('Configurar el CRUD, filtros y busquedas de Django Admin', ['Core/admin.py']),
    ('Implementar formularios y vistas del inventario', [
        'Core/forms.py', 'Core/views.py',
    ]),
    ('Agregar estructura visual, paginacion y estilos locales', [
        'templates/base.html', 'templates/paginacion.html',
        'Core/static/Core/inventario.css',
    ]),
    ('Agregar las pantallas del CRUD de productos', [
        'templates/index.html', 'templates/producto_form.html',
        'templates/producto_confirmar_eliminacion.html',
    ]),
    ('Mostrar movimientos, documentos y motivos de venta', ['templates/movimientos.html']),
    ('Generar datos relacionados con Faker y cargas por lotes', [
        'Core/management/__init__.py', 'Core/management/commands/__init__.py',
        'Core/management/commands/cargar_datos.py',
    ]),
    ('Diagnosticar la conexion, tablas y migraciones', [
        'Core/management/commands/verificar_bd.py',
    ]),
    ('Verificar CRUD, integridad y generacion de datos con pruebas', [
        'Core/tests.py', 'Core/test_database.py', 'Core/test_crud_web.py',
        'Core/test_modelo_bodega.py', 'Core/test_edicion_documentos.py',
        'Core/test_semilla_completa.py',
    ]),
    ('Documentar el esquema y los diagramas de Music Pro', [
        'docs/diagrama_bd.md', 'docs/diagrama_bd.svg', 'docs/diagrama_bd.png',
        'docs/diagrama_arquitectura.svg', 'docs/diagrama_arquitectura.png',
        'docs/flujo_carga.svg', 'docs/flujo_carga.png', 'docs/diagramas.md',
    ]),
    ('Documentar instalacion, evaluacion y publicacion en GitHub', [
        'README.md', 'README_ADMIN.md', 'README_MIGRACIONES.md',
        'README_SEEDER.md', 'README_GITHUB.md', 'readme', 'VERIFICACION.md',
        'docs/tablas_bd.md', 'docs/rubrica_e2.md',
        'docs/correspondencia_referencia.md', 'docs/resultados_cargas.json',
        'docs/verificacion_diez_tablas.json', 'preparar_git.py',
    ]),
]


def git(*argumentos, comprobar=True, capturar=False):
    return subprocess.run(
        ['git', *argumentos], cwd=RAIZ, check=comprobar,
        capture_output=capturar, text=True, encoding='utf-8', errors='replace',
    )


def identidad(clave, pregunta):
    resultado = git('config', '--get', clave, comprobar=False, capturar=True)
    valor = resultado.stdout.strip()
    if not valor:
        valor = input(pregunta).strip()
    if not valor:
        raise ValueError(f'Falta {clave}; no se ha inicializado el repositorio.')
    return valor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ver', action='store_true', help='Mostrar los 15 grupos sin modificar Git.')
    opciones = parser.parse_args()
    archivos = [ruta for _, rutas in GRUPOS for ruta in rutas]
    if len(GRUPOS) != 15 or len(archivos) != len(set(archivos)):
        raise ValueError('El plan debe tener 15 grupos sin archivos repetidos.')
    faltantes = [ruta for ruta in archivos if not (RAIZ / ruta).is_file()]
    if faltantes:
        raise ValueError('Faltan archivos: ' + ', '.join(faltantes))
    for numero, (mensaje, rutas) in enumerate(GRUPOS, 1):
        print(f'{numero:02}. {mensaje} ({len(rutas)} archivos)', flush=True)
    if opciones.ver:
        print('Vista previa: no se ha modificado Git.')
        return
    if not shutil.which('git'):
        raise ValueError('Git no esta instalado o no aparece en PATH.')
    existente = git('rev-parse', '--show-toplevel', comprobar=False, capturar=True)
    if (RAIZ / '.git').exists() or existente.returncode == 0:
        raise ValueError('Ya existe un repositorio. Consulta git log; este script solo prepara la primera importacion.')

    nombre = identidad('user.name', 'Tu nombre para los commits: ')
    correo = identidad('user.email', 'Tu correo de GitHub (puede ser el noreply): ')
    git('init', '-b', 'main')
    git('config', '--local', 'user.name', nombre)
    git('config', '--local', 'user.email', correo)
    for mensaje, rutas in GRUPOS:
        git('add', '--', *rutas)
        git('commit', '-m', mensaje)

    total = int(git('rev-list', '--count', 'HEAD', capturar=True).stdout.strip())
    if total != 15:
        raise ValueError(f'Se esperaban 15 commits; Git informa {total}.')
    print('\nListo: 15 commits locales en main. Aun no se ha subido nada a GitHub.')
    git('log', '--oneline', '--reverse')
    estado = git('status', '--short', capturar=True).stdout.strip()
    if estado:
        print('\nArchivos adicionales que debes revisar con git status:\n' + estado)
    print('\nContinua con README_GITHUB.md para conectar el repositorio y hacer push.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError, EOFError) as error:
        print(f'\nNo se completo la preparacion: {error}', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nPreparacion cancelada.', file=sys.stderr)
        sys.exit(1)
