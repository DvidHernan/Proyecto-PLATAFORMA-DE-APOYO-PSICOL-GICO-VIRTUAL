from django.db import models
from django.contrib.auth.models import User

class Funcionalidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thread_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('user', 'Usuario'), ('assistant', 'Asistente')])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Cita(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')], default='pendiente')

    def __str__(self):
        return f"Cita de {self.usuario.username} el {self.fecha} a las {self.hora}"