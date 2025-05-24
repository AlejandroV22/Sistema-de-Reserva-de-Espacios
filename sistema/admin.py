from django.contrib import admin
from .models import Usuario, Espacio, HorarioDisponible, Reserva, Notificacion, Sancion

admin.site.register(Usuario)
admin.site.register(Espacio)
admin.site.register(HorarioDisponible)
admin.site.register(Reserva)
admin.site.register(Notificacion)
admin.site.register(Sancion)
# Register your models here.
