from django.db import models
from django.utils import timezone
from .bolsin import Bolsin
from .comision_medica import ComisionMedica


class Remito(models.Model):
    """
    Remito: detalla la documentación a enviar a una CM destino específica.
    Se genera uno por cada CM destino diferente dentro de un mismo bolsín.

    Estados válidos:
        Generado → EnBolsinSaliente → EnBolsinEnviado →
        RecibidoYAceptado | RecibidoYAceptadoParcial | Cancelado
    """
    ESTADO_GENERADO = 'Generado'
    ESTADO_EN_BOLSIN_SALIENTE = 'EnBolsinSaliente'
    ESTADO_EN_BOLSIN_ENVIADO = 'EnBolsinEnviado'
    ESTADO_RECIBIDO_ACEPTADO = 'RecibidoYAceptado'
    ESTADO_RECIBIDO_PARCIAL = 'RecibidoYAceptadoParcial'
    ESTADO_CANCELADO = 'Cancelado'
    ESTADO_CHOICES = [
        (ESTADO_GENERADO, 'Generado'),
        (ESTADO_EN_BOLSIN_SALIENTE, 'En Bolsín Saliente'),
        (ESTADO_EN_BOLSIN_ENVIADO, 'En Bolsín Enviado'),
        (ESTADO_RECIBIDO_ACEPTADO, 'Recibido y Aceptado'),
        (ESTADO_RECIBIDO_PARCIAL, 'Recibido y Aceptado Parcialmente'),
        (ESTADO_CANCELADO, 'Cancelado'),
    ]

    nro_remito = models.PositiveIntegerField(unique=True, verbose_name='Nro. Remito')
    bolsin = models.ForeignKey(
        Bolsin,
        on_delete=models.CASCADE,
        related_name='remitos',
        verbose_name='Bolsín',
    )
    cm_destino = models.ForeignKey(
        ComisionMedica,
        on_delete=models.PROTECT,
        related_name='remitos_destino',
        verbose_name='CM Destino',
    )
    estado_actual = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default=ESTADO_GENERADO,
        verbose_name='Estado actual',
    )

    class Meta:
        verbose_name = 'Remito'
        verbose_name_plural = 'Remitos'
        ordering = ['-nro_remito']

    def __str__(self):
        return f'Remito #{self.nro_remito} [{self.estado_actual}]'

    def registrar_cambio_estado(self, nuevo_estado: str, empleado) -> 'CambioEstadoRemito':
        cambio = CambioEstadoRemito.objects.create(
            remito=self,
            estado_anterior=self.estado_actual,
            estado_nuevo=nuevo_estado,
            empleado=empleado,
            fecha_hora=timezone.now(),
        )
        self.estado_actual = nuevo_estado
        self.save()
        return cambio


class CambioEstadoRemito(models.Model):
    """Historial de cambios de estado del remito."""
    remito = models.ForeignKey(Remito, on_delete=models.CASCADE, related_name='cambios_estado')
    estado_anterior = models.CharField(max_length=30)
    estado_nuevo = models.CharField(max_length=30)
    empleado = models.ForeignKey('Empleado', on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField()

    class Meta:
        verbose_name = 'Cambio de Estado (Remito)'
        ordering = ['fecha_hora']

    def __str__(self):
        return f'Remito #{self.remito.nro_remito}: {self.estado_anterior} → {self.estado_nuevo}'
