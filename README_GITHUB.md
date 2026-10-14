# Publicar Music Pro en GitHub con 15 commits

El proyecto incluye [preparar_git.py](preparar_git.py), que inicializa Git y guarda los archivos actuales en **15 commits locales por componentes**. Usa las fechas reales de ejecución: es una importación organizada del estado actual. Las primeras revisiones contienen partes del proyecto; la revisión 15 contiene la aplicación completa. El script no crea un repositorio en GitHub ni sube archivos.

## 1. Crear los commits locales

Abre PowerShell y entra a la carpeta:

```powershell
cd C:\Users\Emmanuel\Desktop\musicpro_e2
git --version
```

`cd` selecciona el proyecto; `git --version` confirma que Git está instalado. En este equipo se comprobó Git 2.55.0.windows.3.

Puedes consultar primero la distribución sin modificar nada:

```powershell
.\.venv\Scripts\python.exe preparar_git.py --ver
```

Para crear el repositorio y los 15 commits:

```powershell
.\.venv\Scripts\python.exe preparar_git.py
```

Si Git todavía no tiene tu identidad, el programa solicita tu nombre y correo. Utiliza el correo asociado a GitHub o tu dirección `noreply`, disponible en **Settings > Emails** de GitHub. Los guarda únicamente en este repositorio. El nombre puede ser tu nombre personal; no necesita coincidir con tu usuario de GitHub.

El programa ejecuta `git init -b main`, prepara los archivos de cada grupo con `git add` y guarda cada grupo con `git commit -m`. Detiene la ejecución si encuentra un repositorio existente, evitando repetir la importación. Si se interrumpe después de inicializar Git, revisa `git status` y `git log --oneline` antes de continuar; conserva el historial existente.

| Commit | Contenido |
| ---: | --- |
| 1 | Configurar dependencias y archivos excluidos |
| 2 | Configurar el proyecto Django y la conexion SQLite |
| 3 | Registrar la aplicacion de bodega |
| 4 | Definir los diez modelos del negocio y sus relaciones |
| 5 | Incorporar el historial de migraciones de la bodega |
| 6 | Configurar el CRUD, filtros y busquedas de Django Admin |
| 7 | Generar datos relacionados con Faker y cargas por lotes |
| 8 | Diagnosticar la conexion, tablas y migraciones |
| 9 | Verificar CRUD, filtros y rutas de Django Admin |
| 10 | Probar integridad de la base y cargas por lotes |
| 11 | Probar los diez modelos y su administracion |
| 12 | Proteger la edicion de documentos vinculados |
| 13 | Verificar la generacion completa de datos relacionados |
| 14 | Documentar el esquema y los diagramas de Music Pro |
| 15 | Documentar instalacion, evaluacion y publicacion en GitHub |

Comprueba el resultado:

```powershell
git rev-list --count HEAD
git log --oneline --reverse
git status --short
```

El primer comando debe mostrar **15**; el segundo enumera los mensajes del historial. El tercero debe quedar sin salida si no hay archivos adicionales ni cambios pendientes. Estos commits se pueden subir juntos mediante un solo `push`.

## 2. Crear un repositorio vacío en GitHub

1. Inicia sesión en [GitHub](https://github.com/) y selecciona **New repository**.
2. Escribe `musicpro_e2` como nombre y selecciona **Public**, según la pauta de entrega.
3. Deja desactivada la creación de README, `.gitignore` y licencia: estos archivos se gestionan desde el proyecto local y así el repositorio remoto comienza vacío.
4. Selecciona **Create repository** y copia la URL HTTPS que aparece, con la forma `https://github.com/TU_USUARIO/musicpro_e2.git`.

Este procedimiento corresponde a la [guía oficial para subir un proyecto local](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).

## 3. Conectar y subir

En la misma terminal, reemplaza `TU_USUARIO` por tu usuario real, o pega la URL que copiaste:

```powershell
git remote add origin https://github.com/TU_USUARIO/musicpro_e2.git
git remote -v
git push -u origin main
```

- `remote add origin` vincula el proyecto local con ese repositorio de GitHub.
- `remote -v` muestra la dirección vinculada para comprobarla.
- `push -u origin main` sube los 15 commits y configura la rama remota para futuras subidas. Completa el inicio de sesión que solicite Git/GitHub.

Si aparece `remote origin already exists`, consulta `git remote -v`. Si la URL es incorrecta, corrígela con `git remote set-url origin URL_CORRECTA` y vuelve a hacer `push`.

Si la subida es rechazada porque el remoto contiene commits, revisa su historial y no sobrescribas el trabajo. Para conservar exactamente los 15 commits de esta importación, el destino debe comenzar vacío.

## 4. Revisar la entrega y volver a ejecutar el proyecto

Actualiza la página de GitHub: debe mostrar el código, README, diagramas y **15 commits** en `main`. Abre el último commit para copiar su enlace si el profesor lo solicita.

`.gitignore` excluye `.venv`, `db.sqlite3`, respaldos, archivos `.env`, cachés y archivos temporales. La base no se publica porque contiene usuarios y datos locales. Las migraciones y Faker permiten reconstruir las diez tablas en otro equipo:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py cargar_datos --cantidad 20 --semilla 42 --completo
.\.venv\Scripts\python.exe manage.py createsuperuser
.\servidor.bat
```

La configuración usa una clave pública explícita para desarrollo local. Para otros entornos, define una clave privada mediante la variable `DJANGO_SECRET_KEY`; los archivos `.env` no se cargan automáticamente. Consulta [README.md](README.md) para la instalación completa.

Para cambios futuros, selecciona los archivos modificados con `git add`, crea un nuevo commit y ejecuta `git push`. Cada cambio posterior aumenta el contador; no es necesario conservarlo en 15 después de la entrega.

## Actualizar el repositorio ya publicado: solo Django Admin

Si ya publicaste la primera versión, conserva los commits existentes. La corrección retira las vistas, formularios y plantillas propias, y deja únicamente la ruta `/admin/`. Actualiza GitHub desde la carpeta del proyecto:

```powershell
git diff --stat
git add -u
git commit -m "Usar exclusivamente Django Admin y retirar las vistas propias"
git push
```

`diff --stat` resume los cambios; `add -u` prepara modificaciones y eliminaciones de archivos ya registrados, sin incluir archivos nuevos ajenos a esta corrección. El nuevo commit se añade al historial: si tenías 15, tendrás 16. No vuelvas a ejecutar `preparar_git.py` ni reinicialices el repositorio existente.
