from django.shortcuts import render, redirect, get_object_or_404
from .models import Espacio, Usuario, Reserva , HorarioDisponible, Sancion
from .forms import EspacioForm, SancionForm
from django.http import JsonResponse
from datetime import datetime, timedelta
import json
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_POST , require_GET
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import SancionForm
from django.core.mail import send_mail
from django.utils import timezone
from sistema.tasks import enviar_correo_confirmacion

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            if usuario.is_active:  
                login(request, usuario)
                if usuario.rol == 'admin':
                    return redirect('panel_administrador')
                else:
                    return redirect('panel_usuario')
            else:
                return render(request, 'login.html', {'error': 'Usuario inactivo'})
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')


@login_required # <--- solo usuarios autenticados pueden acceder
def panel_usuario_view(request):
   
    user_reservas = Reserva.objects.filter(usuario=request.user).order_by('fecha_Reserva', 'horaInicio')
    context = {
        'user_reservas': user_reservas,
        
    }
    return render(request, 'panel_usuario.html', context)


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
    return redirect ('admin_panel_espacios')

def panel_administrador(request): #Panel de administrador personalizado
    return render(request, 'panel_administrador.html')


def ver_reservas(request):#Ver reservas en el panel de administrador
    reservas = Reserva.objects.select_related('usuario', 'espacio').all()
    return render(request, 'ver_reservas.html', {'reservas': reservas})


def marcar_asistencia(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    asistio = request.POST.get("asistio")

    if asistio == "True":
        reserva.asistio = True
    elif asistio == "False":
        reserva.asistio = False
    else:
        reserva.asistio = True # o lo que consideres por defecto

    reserva.save()
    return HttpResponseRedirect(reverse('ver_reservas'))



def panel_usuarios(request): #Administracion de usuarios 
    return render(request, 'panel_usuarios.html')  

def admin_panel_usuarios(request):
    usuarios = Usuario.objects.all()

    # Agregar usuario
    if 'add_Usuario' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        rol = request.POST.get('rol')  # Obtener el rol (admin o usuario)
        
        if username and password:
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, "El nombre de usuario ya está registrado. Por favor, elige otro.")
                return redirect('admin_panel_usuarios')  # Cambio realizado aquí

            usuario = Usuario.objects.create_user(username=username, email=email, password=password)
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.rol = rol  # Asignar el rol al usuario
            usuario.save()
            messages.success(request, f"{usuario.username} agregado correctamente.")
        
        return redirect('admin_panel_usuarios')  # Cambio realizado aquí
                
    # Eliminar usuario
    if 'delete_user' in request.POST:
        usuario_id = request.POST.get('user_id')  # Obtener el id del usuario
        if usuario_id:
            try:
                usuario = Usuario.objects.get(id=usuario_id)  # Buscar al usuario por id
                usuario.delete()  # Eliminar usuario
                messages.success(request, f"Usuario {usuario.username} eliminado correctamente.")
            except Usuario.DoesNotExist:
                messages.error(request, f"El usuario no existe.")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al eliminar el usuario: {str(e)}")
        return redirect('admin_panel_usuarios')  # Cambio realizado aquí
    
    # Cambiar contraseña
    if "change_password" in request.POST:
        usuario_id = request.POST.get("usuario_id")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if usuario_id and new_password and confirm_password:
            if new_password == confirm_password:
                try:
                    usuario = Usuario.objects.get(id=usuario_id)
                    usuario.set_password(new_password)
                    usuario.save()
                    messages.success(request, f"La contraseña para {usuario.username} ha sido cambiada exitosamente.")
                except Usuario.DoesNotExist:
                    messages.error(request, "El usuario no existe.")
            else:
                messages.error(request, "Las contraseñas no coinciden.")
        else:
            messages.error(request, "Todos los campos son obligatorios.")
        
        return redirect('admin_panel_usuarios')  # Cambio realizado aquí
    
    return render(request, 'admin_panel_usuarios.html', {'usuarios': usuarios})

####
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
        
        intervalo_horas = timedelta(minutes=60) #intervalo hora 

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
                 
                    if (reserva_item.horaInicio < slot_end and reserva_item.horaFin > slot_start): 
                        break 

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


    
@login_required
def mis_reservas(request):
    
    reservas_usuario = Reserva.objects.filter(usuario=request.user).order_by('-fecha_Reserva', '-horaInicio')

    context = {
        'reservas': reservas_usuario
    }
    return render(request, 'reservas.html', context)
   

def confirmar_reserva(request):
    usuario = request.user

    if usuario.tiene_sancion_activa():
        return JsonResponse({'success': False, 'message': 'No puedes hacer reservas mientras tengas una sanción activa.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            espacio_id = data.get('espacio_id')
            fecha_str = data.get('fecha_Reserva')
            hora_inicio_str = data.get('horaInicio')
            hora_fin_str = data.get('horaFin')

            if not (espacio_id and fecha_str and hora_inicio_str and hora_fin_str):
                return JsonResponse({'success': False, 'message': 'Datos incompletos para la reserva.'}, status=400)

            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()

            espacio = Espacio.objects.get(id=espacio_id)
            espacio = Espacio.objects.filter(id=espacio_id).first()
            if espacio is None:
                return JsonResponse({'success': False, 'message': 'El espacio seleccionado no existe.'}, status=404)

            # Validar que el horario solicitado esté dentro de un horario disponible para ese día de la semana
            dia_semana = fecha.weekday()
            horarios_disponibles = HorarioDisponible.objects.filter(
                espacio=espacio,
                dia_semana=dia_semana,
                hora_inicio__lte=hora_inicio,
                hora_fin__gte=hora_fin
            )

            if not horarios_disponibles.exists():
                return JsonResponse({'success': False, 'message': 'El horario seleccionado no está disponible en la franja general.'}, status=400)

            # Validar conflictos: reservas que se cruzan con el horario solicitado
            conflictos = Reserva.objects.filter(
                espacio=espacio,
                fecha_Reserva=fecha
            ).filter(
                Q(horaInicio__lt=hora_fin) & Q(horaFin__gt=hora_inicio)
            )

            if conflictos.exists():
                print(f"Conflictos encontrados: {list(conflictos)}") # Imprime los conflictos
                return JsonResponse({'success': False, 'message': 'El horario seleccionado ya está reservado.'}, status=409)
            print(f"Espacio obtenido: {espacio}")
            print(f"Espacio ID recibido: {espacio_id}")
            print(f"Tipo de espacio: {type(espacio)}, Valor de espacio: {espacio}")
            Reserva.objects.create(
                usuario=request.user if request.user.is_authenticated else None, 
                espacio=espacio,
                fecha_Reserva=fecha,
                horaInicio=hora_inicio,
                horaFin=hora_fin,
            )
            #DEBUG
            print(f"Email: {request.user.email}, Usuario: {request.user.username}, Espacio: {espacio.nombre}, Fecha: {fecha}, Hora Inicio: {hora_inicio}, Hora Fin: {hora_fin}")  
            enviar_correo_confirmacion.apply_async(args=[
                request.user.email,
                request.user.username,
                espacio.nombre,
                fecha,
                hora_inicio,
                hora_fin
            ])


            return JsonResponse({'success': True, 'message': 'Reserva confirmada exitosamente.'})

        except Espacio.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Espacio no encontrado.'}, status=404)
        except ValueError as ve:
            return JsonResponse({'success': False, 'message': f'Formato de fecha u hora inválido: {ve}'}, status=400)
        except Exception as e:
            # Esto debería forzar la impresión del traceback
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'Error inesperado del servidor: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

    

def aplicar_sancion(request):
    if request.method == 'POST':
        form = SancionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_sanciones')  # o donde prefieras
    else:
        form = SancionForm()
    return render(request, 'aplicar_sancion.html', {'form': form})

def ver_sanciones(request):
    sanciones = Sancion.objects.select_related('usuario').all()
    return render(request, 'ver_sanciones.html', {'sanciones': sanciones})

@property
def esta_activa(self):
    if self.fecha_levantamiento is None:
        return True
    return self.fecha_levantamiento > timezone.now()




@login_required
@require_GET
def detalle_reserva_ajax(request, reserva_id):
    try:
        reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)

        fecha_formateada = reserva.fecha_Reserva.strftime("%d %b %Y")
        hora_inicio_formateada = reserva.horaInicio.strftime("%H:%M") # <-- Usar horaInicio de Reserva
        hora_fin_formateada = reserva.horaFin.strftime("%H:%M")       # <-- Usar horaFin de Reserva

        data = {
            'success': True,
            'espacio_nombre': reserva.espacio.nombre,
            'tipo_espacio': reserva.espacio.get_tipoEspacio_display(),
            'fecha_reserva': fecha_formateada,
            'hora_inicio': hora_inicio_formateada,
            'hora_fin': hora_fin_formateada,
            'estado': reserva.get_estado_display(),
            'recurrente': 'Sí' if reserva.recurrente else 'No' # Asumiendo que tienes un campo 'recurrente'
        }
        return JsonResponse(data)
    except Reserva.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Reserva no encontrada o no pertenece al usuario.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Error al obtener detalles: {str(e)}'}, status=500)


# Vista AJAX para cancelar una reserva
@login_required
@require_POST
def cancelar_reserva(request, reserva_id):
    try:
        reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)

        if reserva.estado == 'cancelada':
            return JsonResponse({'success': False, 'message': 'Esta reserva ya ha sido cancelada.'}, status=400)

       
        reserva.estado = 'cancelada'
        reserva.save()

        messages.success(request, 'La reserva ha sido cancelada exitosamente.')

        return JsonResponse({
            'success': True,
            'message': 'Reserva cancelada exitosamente.',
            'new_status': reserva.get_estado_display()
        })

    except Reserva.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Reserva no encontrada o no pertenece al usuario.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Error al cancelar la reserva: {str(e)}'}, status=500)

def editar_sancion(request, sancion_id):
    sancion = get_object_or_404(Sancion, id=sancion_id)
    if request.method == 'POST':
        form = SancionForm(request.POST, instance=sancion)
        if form.is_valid():
            form.save()
            return redirect('ver_sanciones')
    else:
        form = SancionForm(instance=sancion)
    return render(request, 'editar_sancion.html', {'form': form, 'sancion': sancion})


def eliminar_sancion(request, sancion_id):
    sancion = get_object_or_404(Sancion, id=sancion_id)
    sancion.delete()
    return redirect('ver_sanciones')



def enviar_notificaciones():
    reservas = Reserva.objects.filter(fecha_Reserva=timezone.now().date())  # Obtiene reservas del día
    for reserva in reservas:
        mensaje = f"Hola {reserva.usuario.username}, recuerda que tienes una reserva hoy en {reserva.espacio.nombre} de {reserva.horaInicio} a {reserva.horaFin}."
        send_mail(
            'Recordatorio de Reserva',
            mensaje,
            'teamwareproject@gmail.com',  # Remitente
            [reserva.usuario.email],  # Destinatario
            fail_silently=False,
        )