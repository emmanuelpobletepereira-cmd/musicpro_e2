from django import forms

from .models import Producto


class ProductoForm(forms.ModelForm):
    """Los formularios reutilizan las reglas de los modelos del inventario."""

    class Meta:
        model = Producto
        fields = ('codigo', 'nombre', 'categoria', 'marca', 'ubicacion', 'cantidad', 'stock_minimo')
        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre del producto',
            'categoria': 'Categoría',
            'marca': 'Marca',
            'ubicacion': 'Ubicación en bodega',
            'cantidad': 'Cantidad disponible',
            'stock_minimo': 'Stock mínimo',
        }
        help_texts = {
            'codigo': 'Identificador único del producto, de hasta 40 caracteres.',
            'marca': 'Opcional para conservar productos históricos sin una marca registrada.',
            'ubicacion': 'Por ejemplo: Pasillo 2, estante B.',
            'cantidad': 'Unidades disponibles. Se admite cero.',
            'stock_minimo': 'El stock es crítico cuando la cantidad es igual o inferior a este valor.',
        }
        widgets = {
            'cantidad': forms.NumberInput(attrs={'min': 0}),
            'stock_minimo': forms.NumberInput(attrs={'min': 0}),
        }
        error_messages = {
            'codigo': {'unique': 'Ya existe un producto con este código.'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = self.fields['categoria'].queryset.order_by('nombre')
        self.fields['categoria'].empty_label = 'Selecciona una categoría'
        self.fields['marca'].queryset = self.fields['marca'].queryset.order_by('nombre')
        self.fields['marca'].empty_label = 'Sin marca registrada'
