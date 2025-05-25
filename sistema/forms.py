from django import forms
from .models import Sancion, Usuario, Reserva, Espacio


class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'tipoEspacio', 'capacidadMaxima']

class ReservaForm(forms.ModelForm):
   
    fecha_Reserva = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Reserva" 
    )
    horaInicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Hora de Inicio"
    )
    horaFin = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Hora de Fin"
    )

    class Meta:
        model = Reserva
        fields = ['fecha_Reserva', 'horaInicio', 'horaFin']

class SancionForm(forms.ModelForm):
    class Meta:
        model = Sancion
        fields = ['usuario', 'motivo', 'fecha_levantamiento']
        widgets = {
            'fecha_levantamiento': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }



