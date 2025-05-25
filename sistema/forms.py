from django import forms
from .models import Espacio

class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'tipoEspacio', 'capacidadMaxima']
