from django.core.mail import send_mail
from django.utils import timezone
from sistema.models import Reserva

def enviar_notificaciones_reservas():
    # Filtra reservas para el día siguiente
    fecha_objetivo = timezone.now().date() + timezone.timedelta(days=1)
    reservas = Reserva.objects.filter(fecha_Reserva=fecha_objetivo)

    for reserva in reservas:
        mensaje = f"""
        Hola {reserva.usuario.username},

        Recuerda que tienes una reserva programada mañana ({reserva.fecha_Reserva}) en {reserva.espacio.nombre}.
        Horario: {reserva.horaInicio} - {reserva.horaFin}

        ¡Te esperamos!

        """
        send_mail(
            'Recordatorio de Reserva',
            mensaje,
            'teamwareproyect@gmail.com',  # Remitente
            [reserva.usuario.email],  # Destinatario
            fail_silently=False,
        )