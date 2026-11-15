from django.db import models
from django.utils import timezone
from .comision_medica import ComisionMedica
from .remito import Remito


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'

    def __str__(self):
        return self.nombre


class Documentacion(models.Model):
    """
    Documentación individual a ser enviada en un bolsín.

    Estados válidos:
        Registrada → EnRemito → EnBolsinSaliente → EnBolsinEnviado →
        RecibidaYAceptada | RecibidaYRechazada | NoRecibida | ParaRedirigir | DeBaja
    """
    ESTADO_REGISTRADA = 'Registrada'
    ESTADO_EN_REMITO = 'EnRemito'
    ESTADO_EN_BOLSIN_SALIENTE = 'EnBolsinSaliente'
    ESTADO_EN_BOLSIN_ENVIADO = 'EnBolsinEnviado'
    ESTADO_RECIBIDA_ACEPTADA = 'RecibidaYAceptada'
    ESTADO_RECIBIDA_RECHAZADA = 'RecibidaYRechazada'
    ESTADO_NO_RECIBIDA = 'NoRecibida'
    ESTADO_PARA_REDIRIGIR = 'ParaRedirigir'
    ESTADO_BAJA = 'DeBaja'
    ESTADO_CHOICES = [
        (ESTADO_REGISTRADA, 'Registrada'),
        (ESTADO_EN_REMITO, 'En Remito'),
        (ESTADO_EN_BOLSIN_SALIENTE, 'En Bolsín Saliente'),
        (ESTADO_EN_BOLSIN_ENVIADO, 'En Bolsín Enviado'),
        (ESTADO_RECIBIDA_ACEPTADA, 'Recibida y Aceptada'),
        (ESTADO_RECIBIDA_RECHAZADA, 'Recibida y Rechazada'),
        (ESTADO_NO_RECIBIDA, 'No Recibida'),
        (ESTADO_PARA_REDIRIGIR, 'Para Redirigir'),
        (ESTADO_BAJA, 'De Baja'),
    ]

    nro_documento = models.PositiveIntegerField(unique=True, verbose_name='Nro. Documento')
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT)
    fecha_pase = models.DateField(verbose_name='Fecha de pase')
    cm_origen = models.ForeignKey(
        ComisionMedica,
        on_delete=models.PROTECT,
        related_name='documentaciones_origen',
    )
    asunto = models.CharField(max_length=500, verbose_name='Asunto')
    archivo = models.FileField(
        upload_to='documentacion/',
        blank=True,
        null=True,
        verbose_name='Archivo adjunto',
    )
    remito = models.ForeignKey(
        Remito,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentaciones',
    )
    estado_actual = models.CharField(
        max_length=25,
        choices=ESTADO_CHOICES,
        default=ESTADO_REGISTRADA,
        verbose_name='Estado actual',
    )

    class Meta:
        verbose_name = 'Documentación'
        verbose_name_plural = 'Documentaciones'
        ordering = ['-nro_documento']

    def __str__(self):
        return f'Doc #{self.nro_documento} — {self.asunto[:50]}'

    def registrar_cambio_estado(self, nuevo_estado: str, empleado) -> 'CambioEstadoDocumentacion':
        cambio = CambioEstadoDocumentacion.objects.create(
            documentacion=self,
            estado_anterior=self.estado_actual,
            estado_nuevo=nuevo_estado,
            empleado=empleado,
            fecha_hora=timezone.now(),
        )
        self.estado_actual = nuevo_estado
        self.save()
        return cambio


class CambioEstadoDocumentacion(models.Model):
    """Historial de cambios de estado de la documentación."""
    documentacion = models.ForeignKey(
        Documentacion,
        on_delete=models.CASCADE,
        related_name='cambios_estado',
    )
    estado_anterior = models.CharField(max_length=25)
    estado_nuevo = models.CharField(max_length=25)
    empleado = models.ForeignKey('Empleado', on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField()

    class Meta:
        verbose_name = 'Cambio de Estado (Documentación)'
        ordering = ['fecha_hora']
