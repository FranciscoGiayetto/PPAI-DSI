from django.contrib import admin

from .models import (
    Bolsin, CambioEstadoBolsin, CambioEstadoDocumentacion, CambioEstadoRemito,
    ComisionMedica, Documentacion, Empleado, Remito, TipoDocumento,
)

admin.site.site_header = 'Sistema Bolsines'
admin.site.site_title = 'Bolsines Admin'
admin.site.index_title = 'Panel de administración'


@admin.register(ComisionMedica)
class ComisionMedicaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo',)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('legajo', 'user', 'rol', 'cm_asignada', 'activo')
    search_fields = ('legajo', 'user__username', 'user__first_name', 'user__last_name')
    list_filter = ('rol', 'activo', 'cm_asignada')


@admin.register(Bolsin)
class BolsinAdmin(admin.ModelAdmin):
    list_display = ('nro_bolsin', 'nro_precinto', 'estado_actual', 'cm_origen', 'cm_destino', 'fecha', 'peso_gramos')
    search_fields = ('nro_bolsin', 'nro_precinto')
    list_filter = ('estado_actual', 'cm_origen', 'cm_destino')


@admin.register(CambioEstadoBolsin)
class CambioEstadoBolsinAdmin(admin.ModelAdmin):
    list_display = ('bolsin', 'estado_anterior', 'estado_nuevo', 'empleado', 'fecha_hora')
    list_filter = ('estado_nuevo',)
    search_fields = ('bolsin__nro_bolsin',)


@admin.register(Remito)
class RemitoAdmin(admin.ModelAdmin):
    list_display = ('nro_remito', 'bolsin', 'cm_destino', 'estado_actual')
    search_fields = ('nro_remito',)
    list_filter = ('estado_actual', 'cm_destino')


@admin.register(CambioEstadoRemito)
class CambioEstadoRemitoAdmin(admin.ModelAdmin):
    list_display = ('remito', 'estado_anterior', 'estado_nuevo', 'empleado', 'fecha_hora')
    list_filter = ('estado_nuevo',)


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Documentacion)
class DocumentacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_documento', 'estado_actual')
    list_filter = ('estado_actual', 'tipo_documento')


@admin.register(CambioEstadoDocumentacion)
class CambioEstadoDocumentacionAdmin(admin.ModelAdmin):
    list_display = ('documentacion', 'estado_anterior', 'estado_nuevo', 'empleado', 'fecha_hora')
    list_filter = ('estado_nuevo',)
