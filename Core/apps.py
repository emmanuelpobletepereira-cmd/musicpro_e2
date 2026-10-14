from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Core'
    # Conserva los nombres de tablas y el historial de migraciones existente.
    label = 'bodega'
    verbose_name = 'Bodega Music Pro'
