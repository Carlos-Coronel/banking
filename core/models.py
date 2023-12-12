from django.db import models
from django.conf import settings

class Auditoria(models.Model):
    evento_choices = [
        ('login', 'Inicio de sesión'),
        ('transaccion', 'Transacción'),
        ('retiro', 'Retiro'),
        ('deposito', 'Deposito')

    ]
    EVENTO_NIVEL_CHOICES = [
        ('normal', 'Normal'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]

    nro = models.AutoField(primary_key=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    servidor = models.CharField(max_length=255)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evento = models.CharField(max_length=20, choices=evento_choices)
    nivel = models.CharField(max_length=20, choices=EVENTO_NIVEL_CHOICES)
    mac = models.CharField(max_length=17)
    origin = models.GenericIPAddressField()


    def __str__(self):
        return f'{self.fecha_hora} - {self.evento} - Usuario: {self.usuario.username}'
