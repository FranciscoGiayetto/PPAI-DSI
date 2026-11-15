from django.db import models
from django.contrib.auth.models import User
from .comision_medica import ComisionMedica


class Empleado(models.Model):
    """
    Empleado del organismo. Vinculado a un usuario Django (auth) y a una CM.
    Los roles definen qué funcionalidades puede usar.
    """
    ROL_ENCARGADO_BOLSINES = 'EB'
    ROL_ENCARGADO_DOCUMENTACION = 'ED'
    ROL_GERENTE_CM = 'GCM'
    ROL_PARAMETRIZADOR = 'PAR'
    ROL_CHOICES = [
        (ROL_ENCARGADO_BOLSINES, 'Encargado de Bolsines'),
        (ROL_ENCARGADO_DOCUMENTACION, 'Encargado de Documentación'),
        (ROL_GERENTE_CM, 'Gerente de Comisión Médica'),
        (ROL_PARAMETRIZADOR, 'Parametrizador del Sistema'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado')
    legajo = models.CharField(max_length=20, unique=True, verbose_name='Legajo')
    rol = models.CharField(max_length=3, choices=ROL_CHOICES, verbose_name='Rol')
    cm_asignada = models.ForeignKey(
        ComisionMedica,
        on_delete=models.PROTECT,
        related_name='empleados',
        verbose_name='Comisión Médica asignada',
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f'{self.legajo} — {self.user.get_full_name()} ({self.get_rol_display()})'
