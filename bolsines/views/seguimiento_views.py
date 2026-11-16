"""CU 36 — Consultar seguimiento de bolsines (boundary web). Delega todo en GestorSeguimientoBolsines."""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from ..services.gestor_seguimiento import GestorSeguimientoBolsines


@login_required
def seguimiento_view(request: HttpRequest) -> HttpResponse:
    """Pasos 1–6 del CU 36: CM del usuario, bolsines Enviados con esa CM origen y su ubicación."""
    gestor = GestorSeguimientoBolsines(getattr(request.user, 'empleado', None))
    bolsines = gestor.nuevo_seguimiento_bolsin()
    origen = gestor.coordenadas_origen
    nombre = gestor.nombre_comision_medica
    clave = settings.GOOGLE_MAPS_API_KEY
    contexto = {
        'nav_activo': 'seguimiento',
        'cm_nombre': nombre,
        'cm_ciudad': nombre.split(' ', 1)[-1] if ' ' in nombre else '',
        'actualizado': timezone.localtime().strftime('%H:%M'),
        'destinos': sorted({b['destino'] for b in bolsines}),
        'gps_no_disponible': gestor.gps_no_disponible,
        'datos': {
            'bolsines': bolsines,
            'origen': {'lat': origen[0], 'lng': origen[1], 'nombre': nombre},
            'cargando': request.GET.get('demo') == 'cargando',
        },
        'google_maps_key': '' if clave in ('', 'tu_clave_aqui') else clave,
        'google_maps_map_id': getattr(settings, 'GOOGLE_MAPS_MAP_ID', 'DEMO_MAP_ID'),
    }
    return render(request, 'seguimiento/index.html', contexto)


@login_required
@require_POST
def notificar_ubicacion_view(request: HttpRequest, nro_bolsin: int) -> JsonResponse:
    """Paso 9 (EB confirma) → CU 30: el Gestor manda el correo al Gerente de la CM destino."""
    gestor = GestorSeguimientoBolsines(getattr(request.user, 'empleado', None))
    gestor.nuevo_seguimiento_bolsin()
    enviado = gestor.tomar_confirmacion_enviar_correo(nro_bolsin)
    if not enviado:
        return JsonResponse({'ok': False, 'mensaje': 'No se pudo avisar: sin ubicación o sin gerente con correo.'},
                            status=409)
    return JsonResponse({'ok': True})
