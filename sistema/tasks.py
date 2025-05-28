from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def enviar_correo_confirmacion(email_destino, usuario, espacio, fecha, hora_inicio, hora_fin):
    print(f"Tarea Celery: Email: {email_destino}, Usuario: {usuario}, Espacio: {espacio}, Fecha: {fecha}, Inicio: {hora_inicio}, Fin: {hora_fin}")
    # Crear contenido del mensaje usando una plantilla HTML
    contexto = {
        "usuario": usuario,
        "espacio": espacio,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin
    }
    mensaje_html = render_to_string("correo_confirmacion.html", contexto)
    mensaje_texto = strip_tags(mensaje_html)  # Versión de texto por si el cliente de email no admite HTML

    send_mail(
        "Confirmación de Reserva - TeamWare",
        mensaje_texto,
        "teamwareproject@gmail.com",
        [email_destino],
        html_message=mensaje_html,
        fail_silently=False,
    )