from django.db import models


class ComisionMedica(models.Model):
    """
    Comisión Médica: puede ser CMJ (Jurisdiccional) o CMC (Central).
    Existen más de 80 CMJ en el país y una CMC en C.A.B.A.
    """
    TIPO_CMJ = 'CMJ'
    TIPO_CMC = 'CMC'
    TIPO_CHOICES = [
        (TIPO_CMJ, 'Comisión Médica Jurisdiccional'),
        (TIPO_CMC, 'Comisión Médica Central'),
    ]

    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES, verbose_name='Tipo')
    direccion = models.CharField(max_length=300, blank=True, verbose_name='Dirección')
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Comisión Médica'
        verbose_name_plural = 'Comisiones Médicas'
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} — {self.nombre}'
