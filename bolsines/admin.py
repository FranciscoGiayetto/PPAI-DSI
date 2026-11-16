from django.contrib import admin

from .models import (
    Bolsin, CambioEstadoBolsin, CambioEstadoDocumentacion, CambioEstadoRemito,
    ComisionMedica, Documentacion, Empleado, Remito, TipoDocumento,
)

for modelo in (ComisionMedica, Empleado, Bolsin, CambioEstadoBolsin, Remito,
               CambioEstadoRemito, TipoDocumento, Documentacion, CambioEstadoDocumentacion):
    admin.site.register(modelo)
