from celery import shared_task
from sistema.utils import enviar_notificaciones_reservas

@shared_task
def tarea_enviar_notificaciones_reservas():
    enviar_notificaciones_reservas()


@shared_task
def tarea_prueba():
    print("✅ Celery está funcionando correctamente 🚀")
    return "Prueba exitosa"