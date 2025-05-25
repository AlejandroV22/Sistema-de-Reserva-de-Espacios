from django.shortcuts import render, redirect, get_object_or_404
from .models import Espacio, Usuario, Reserva , HorarioDisponible
from .forms import EspacioForm 
from django.http import JsonResponse
from datetime import datetime

# Create your views here.


def login_view(request):
    return render(request, 'login.html')


def panel_usuario_view(request):
    return render(request, 'panel_usuario.html')

def panel_espacios(request):
    espacios = Espacio.objects.all()
    return render(request, 'panel_espacios.html', {'espacios': espacios})

def agregar_espacio(request):
    if request.method == 'POST':
        form = EspacioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('panel_espacios')
    else:
        form = EspacioForm()
    return render(request, 'agregar_espacio.html', {'form': form})

def eliminar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)
    espacio.delete()
    return ('panel_espacios')

def panel_administrador(request): #Panel de administrador personalizado
    return render(request, 'panel_administrador.html')

def panel_usuarios(request): #Administracion de usuarios 
    return render(request, 'panel_usuarios.html')  

def admin_panel_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'admin_panel_usuarios.html', {'usuarios': usuarios})

def obtener_horarios_disponibles(request):
    espacio_id = request.GET.get('espacio_id')
    fecha_str = request.GET.get('fecha')  # ejemplo: '2025-05-24'

    if not espacio_id or not fecha_str:
        return JsonResponse({'error': 'Parámetros faltantes'}, status=400)

    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        dia_semana = fecha.weekday()  # lunes = 0, domingo = 6

        horarios = HorarioDisponible.objects.filter(espacio_id=espacio_id, dia_semana=dia_semana)
        reservas = Reserva.objects.filter(espacio_id=espacio_id, fecha_Reserva=fecha)

        disponibles = []

        for horario in horarios:
            conflicto = reservas.filter(
                horaInicio=horario.hora_inicio,
                horaFin=horario.hora_fin
            ).exists()
            if not conflicto:
                disponibles.append({
                    'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                    'hora_fin': horario.hora_fin.strftime('%H:%M')
                })

        return JsonResponse({'horarios': disponibles})

    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)