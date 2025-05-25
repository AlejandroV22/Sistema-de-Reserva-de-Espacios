from django.shortcuts import render, redirect, get_object_or_404
from .models import Espacio, Usuario, Reserva , HorarioDisponible
from .forms import EspacioForm 
from django.http import JsonResponse
from datetime import datetime
import json
from django.utils.dateparse import parse_date
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
    fecha_str = request.GET.get('fecha')
    print(f"Espacio recibido: {espacio_id}, Fecha recibida: {fecha_str}")

    if not espacio_id or not fecha_str:
        return JsonResponse({'error': 'Parámetros faltantes'}, status=400)

    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        dia_semana = fecha.weekday() # lunes = 0, domingo = 6

        # Obtener los horarios base grandes para el espacio y día
        horarios_base = HorarioDisponible.objects.filter(espacio_id=espacio_id, dia_semana=dia_semana)

        reservas_existentes = Reserva.objects.filter(
            espacio_id=espacio_id,
            fecha_Reserva=fecha 
        )

        disponibles = []
        # Definir la duración de los bloques que quieres mostrar (ej., 1 hora)
        intervalo_horas = timedelta(minutes=60) # Puedes cambiar a minutes=30 para intervalos de 30 minutos

        for horario_base_item in horarios_base:
            # Iterar desde la hora de inicio del horario base hasta la hora de fin
            current_time = datetime.combine(fecha, horario_base_item.hora_inicio)
            end_time_base = datetime.combine(fecha, horario_base_item.hora_fin)

            # Generar intervalos de tiempo
            while current_time + intervalo_horas <= end_time_base:
                slot_start_dt = current_time
                slot_end_dt = current_time + intervalo_horas
                
                slot_start = slot_start_dt.time()
                slot_end = slot_end_dt.time()
                
                slot_ocupado = False
                for reserva_item in reservas_existentes:
                    # Comprobar si el slot actual se superpone con alguna reserva existente
                    # ¡IMPORTANTE! Asegúrate de que 'hora_inicio' y 'hora_fin' aquí
                    # coincidan EXACTAMENTE con los nombres de las columnas en tu tabla 'sistema_reserva'
                    # (ej. si es 'horaInicio', cámbialo a 'reserva_item.horaInicio')
                    if (reserva_item.hora_inicio < slot_end and reserva_item.hora_fin > slot_start): # Usar 'hora_inicio' y 'hora_fin' (si aplicaste snake_case en modelo)
                        slot_ocupado = True
                        break # Este slot está ocupado, no hay necesidad de seguir verificando

                if not slot_ocupado:
                    disponibles.append({
                        'hora_inicio': slot_start.strftime('%H:%M'),
                        'hora_fin': slot_end.strftime('%H:%M')
                    })
                
                current_time += intervalo_horas # Mover al siguiente intervalo

        return JsonResponse({'horarios': disponibles})

    except Espacio.DoesNotExist:
        return JsonResponse({'error': 'Espacio no encontrado'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
    except Exception as e:
        print(f"Error en obtener_horarios_disponibles: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)


    
  
def reservas_view(request):
    return render(request, 'reservas.html')
   

def confirmar_reserva(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            espacio_id = data.get('espacio_id')
            fecha_str = data.get('fecha')
            hora_inicio_str = data.get('hora_inicio')
            hora_fin_str = data.get('hora_fin')

            if not (espacio_id and fecha_str and hora_inicio_str and hora_fin_str):
                return JsonResponse({'success': False, 'message': 'Datos incompletos.'}, status=400)

            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()

            espacio = Espacio.objects.get(id=espacio_id)

            # Validar que el horario solicitado esté dentro de un horario disponible para ese día de la semana
            dia_semana = fecha.weekday()
            horarios_disponibles = HorarioDisponible.objects.filter(
                espacio=espacio,
                dia_semana=dia_semana,
                hora_inicio__lte=hora_inicio,
                hora_fin__gte=hora_fin
            )

            if not horarios_disponibles.exists():
                return JsonResponse({'success': False, 'message': 'El horario seleccionado no está disponible.'}, status=400)

            # Validar conflictos: reservas que se cruzan con el horario solicitado
            conflictos = Reserva.objects.filter(
                espacio=espacio,
                fecha_Reserva=fecha
            ).filter(
                Q(horaInicio__lt=hora_fin) & Q(horaFin__gt=hora_inicio)
            )

            if conflictos.exists():
                return JsonResponse({'success': False, 'message': 'El horario seleccionado ya está reservado.'}, status=409)

            # Crear reserva
            Reserva.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                espacio=espacio,
                fecha_Reserva=fecha,
                horaInicio=hora_inicio,
                horaFin=hora_fin,
            )

            return JsonResponse({'success': True, 'message': 'Reserva confirmada exitosamente.'})

        except Espacio.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Espacio no encontrado.'}, status=404)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Formato de fecha u hora inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)