from django.db import models
from django.utils import timezone
from .comision_medica import ComisionMedica


class Bolsin(models.Model):
    """
    Bolsín: contenedor físico (bolsa resistente) que agrupa remitos de documentación
    para ser enviados desde una CM origen a una CM destino.

    Estados válidos:
        Creado → Cerrado → Enviado → RecibidoEnCMDestino
        Creado | Cerrado → DeBaja
    """
    ESTADO_CREADO = 'Creado'
    ESTADO_CERRADO = 'Cerrado'
    ESTADO_ENVIADO = 'Enviado'
    ESTADO_RECIBIDO = 'RecibidoEnCMDestino'
    ESTADO_BAJA = 'DeBaja'
    ESTADO_CHOICES = [
        (ESTADO_CREADO, 'Creado'),
        (ESTADO_CERRADO, 'Cerrado'),
        (ESTADO_ENVIADO, 'Enviado'),
        (ESTADO_RECIBIDO, 'Recibido en CM Destino'),
        (ESTADO_BAJA, 'De Baja'),
    ]

    # Número secuencial único — asignado automáticamente al crear el bolsín
    nro_bolsin = models.PositiveIntegerField(unique=True, verbose_name='Nro. Bolsín')
    fecha = models.DateField(verbose_name='Fecha de armado')
    peso_gramos = models.PositiveIntegerField(verbose_name='Peso (gramos)')
    nro_precinto = models.CharField(max_length=50, unique=True, verbose_name='Nro. Precinto')
    cm_origen = models.ForeignKey(
        ComisionMedica,
        on_delete=models.PROTECT,
        related_name='bolsines_origen',
        verbose_name='CM Origen',
    )
    cm_destino = models.ForeignKey(
        ComisionMedica,
        on_delete=models.PROTECT,
        related_name='bolsines_destino',
        verbose_name='CM Destino',
    )
    estado_actual = models.CharField(
        max_length=25,
        choices=ESTADO_CHOICES,
        default=ESTADO_CREADO,
        verbose_name='Estado actual',
    )

    class Meta:
        verbose_name = 'Bolsín'
        verbose_name_plural = 'Bolsines'
        ordering = ['-nro_bolsin']

    def __str__(self):
        return f'Bolsín #{self.nro_bolsin} [{self.estado_actual}] → {self.cm_destino.codigo}'

    def registrar_cambio_estado(self, nuevo_estado: str, empleado) -> 'CambioEstadoBolsin':
        """Registra el cambio de estado con auditoría (empleado + fecha/hora)."""
        cambio = CambioEstadoBolsin.objects.create(
            bolsin=self,
            estado_anterior=self.estado_actual,
            estado_nuevo=nuevo_estado,
            empleado=empleado,
            fecha_hora=timezone.now(),
        )
        self.estado_actual = nuevo_estado
        self.save()
        return cambio


class CambioEstadoBolsin(models.Model):
    """Historial de cambios de estado del bolsín. Garantiza trazabilidad completa."""
    bolsin = models.ForeignKey(Bolsin, on_delete=models.CASCADE, related_name='cambios_estado')
    estado_anterior = models.CharField(max_length=25)
    estado_nuevo = models.CharField(max_length=25)
    empleado = models.ForeignKey(
        'Empleado',
        on_delete=models.PROTECT,
        verbose_name='Empleado responsable',
    )
    fecha_hora = models.DateTimeField(verbose_name='Fecha y hora del cambio')

    class Meta:
        verbose_name = 'Cambio de Estado (Bolsín)'
        verbose_name_plural = 'Cambios de Estado (Bolsines)'
        ordering = ['fecha_hora']

    def __str__(self):
        return f'Bolsín #{self.bolsin.nro_bolsin}: {self.estado_anterior} → {self.estado_nuevo}'
