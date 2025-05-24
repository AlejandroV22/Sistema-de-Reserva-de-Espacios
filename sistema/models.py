from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


#MODELO DE USUARIO
class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('usuario', 'Usuario'),
    ]

    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='usuario')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
from django.db import models

#MODELO DE ESPACIOS

class Espacio(models.Model):
    TIPO_ESPACIO_CHOICES = [
        ('piscina', 'Piscina'),
        ('sauna', 'Sauna'),
        ('bbq', 'Zona BBQ'),
        ('cancha', 'Cancha Sintética'),
        ('salon', 'Salón Social'),
        ('cine', 'Cine'),
        ('turco', 'Turco'),
        ('gym' , 'Gimnasio'),

        
    ]
    nombre = models.CharField(max_length=100)
    tipoEspacio = models.CharField(max_length=20, choices=TIPO_ESPACIO_CHOICES)
    capacidadMaxima = models.IntegerField()
    
    def __str__(self):
        return self.nombre
    
#MODELO DE HORARIOS DISPONIBLES
class HorarioDisponible(models.Model):

    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]   

    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='disponibilidad')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.espacio.nombre} - {self.get_dia_semana_display()} {self.hora_inicio} - {self.hora_fin}"


#MODELO DE RESERVAS
class Reserva(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='reservas')
    fecha_Reserva = models.DateField()
    horaInicio = models.TimeField()
    horaFin = models.TimeField()
    ESTADOS = (
        ('confirmada', 'Confirmada'),
        ('no_asistida', 'No Asistida'),
        ('cancelada', 'Cancelada'),
        ('en_espera', 'En Espera'),
        ('finalizada', 'Finalizada'),
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='confirmada')
    recurrente = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserva de {self.usuario} en {self.espacio} para el {self.fecha} de {self.horaInicio} a {self.horaFin}"
    
#MODELO DE NOTIFICACIONES

class Notificacion(models.Model):
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    TIPOS = (
        ('recordatorio', 'Recordatorio'),
        ('cancelacion', 'Cancelación'),
        ('sancion', 'Sanción'),
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.destinatario} ({self.tipo})"

#MODELO DE SANCIÓN
class Sancion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sanciones')
    motivo = models.CharField(max_length=200)
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)
    fecha_levantamiento = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sanción de {self.usuario} por {self.motivo} ({self.duracion} días)"

    def esta_activa(self):
        if self.fecha_levantamiento is None:
            return True
        return self.fecha_levantamiento > timezone.now()