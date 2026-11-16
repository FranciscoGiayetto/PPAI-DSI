"""
CU 36 — Consultar seguimiento de bolsines (vista).

⚠️ DEMO DE INTERFAZ. Las ubicaciones de acá son simuladas: sirven para ver la pantalla
mientras el GestorConsultaSeguimiento y los Adapters GPS esperan el diseño de la Entrega 2.
Cuando estén, esta vista solo tiene que pedirle al Gestor la lista y pasarla al template
con la misma forma de `bolsines_json` (ver `_ubicacion_demo`).
"""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from ..models import Bolsin

# Coordenadas aproximadas de cada CM (solo para la demo; el modelo no guarda ubicación).
COORDENADAS_CM = {
    'CMJ-COR': (-31.4201, -64.1888),
    'CMC-CABA': (-34.6037, -58.3816),
    'CMJ-ROS': (-32.9442, -60.6505),
    'CMJ-MZA': (-32.8895, -68.8458),
    'CMJ-TUC': (-26.8083, -65.2176),
    'CMJ-SAL': (-24.7821, -65.4232),
}
MODELOS_GPS = ['XTR-4500L', 'NavTrack QX-7A', 'GeoPulse MTR-900']
SIN_SENAL = {1041}  # bolsines cuyo GPS "no contesta" (flujo A3) en la demo


def _nombre_corto(cm) -> str:
    """'CMJ Córdoba' a partir del nombre largo de la CM."""
    return cm.nombre.replace('Comisión Médica Jurisdiccional', 'CMJ').replace('Comisión Médica Central', 'CMC')


def _ubicacion_demo(bolsin: Bolsin, ahora) -> dict:
    """Arma el dato que hoy devolvería el Gestor (UbicacionBolsin + datos del bolsín)."""
    origen = COORDENADAS_CM.get(bolsin.cm_origen.codigo, COORDENADAS_CM['CMJ-COR'])
    destino = COORDENADAS_CM.get(bolsin.cm_destino.codigo, COORDENADAS_CM['CMC-CABA'])
    avance = 0.25 + (bolsin.nro_bolsin * 37 % 60) / 100  # entre 25 % y 85 %, estable por bolsín
    minutos = 2 + bolsin.nro_bolsin * 7 % 40
    senal = ahora - timedelta(minutes=minutos)
    sin_senal = bolsin.nro_bolsin in SIN_SENAL
    return {
        'nro': bolsin.nro_bolsin,
        'precinto': bolsin.nro_precinto,
        'destino': _nombre_corto(bolsin.cm_destino),
        'destino_codigo': bolsin.cm_destino.codigo,
        'destino_ciudad': _nombre_corto(bolsin.cm_destino).split(' ', 1)[-1],
        'peso_kg': round(bolsin.peso_gramos / 1000, 1),
        'remitos': bolsin.remitos.count(),
        'salio': bolsin.fecha.strftime('%d/%m'),
        'gps': MODELOS_GPS[bolsin.nro_bolsin % 3],
        'avance': round(avance, 2),
        'sin_senal': sin_senal,
        'lat': None if sin_senal else round(origen[0] + (destino[0] - origen[0]) * avance, 4),
        'lng': None if sin_senal else round(origen[1] + (destino[1] - origen[1]) * avance, 4),
        'ultima_senal': senal.strftime('%d/%m %H:%M'),
        'hace_min': minutos,
        'destino_lat': destino[0],
        'destino_lng': destino[1],
    }


@login_required
def seguimiento_view(request: HttpRequest) -> HttpResponse:
    """
    Pasos 2–6 del CU 36: CM del usuario, bolsines Enviados con esa CM origen y su ubicación.
    `?demo=vacio` fuerza el flujo A1 y `?demo=cargando` deja el estado de carga, para mostrarlos.
    """
    empleado = getattr(request.user, 'empleado', None)
    cm = empleado.cm_asignada if empleado else None
    ahora = timezone.localtime()

    bolsines = []
    if cm and request.GET.get('demo') != 'vacio':
        enviados = (Bolsin.objects.filter(estado_actual=Bolsin.ESTADO_ENVIADO, cm_origen=cm)
                    .select_related('cm_origen', 'cm_destino'))
        bolsines = [_ubicacion_demo(b, ahora) for b in enviados]

    origen = COORDENADAS_CM.get(cm.codigo, COORDENADAS_CM['CMJ-COR']) if cm else COORDENADAS_CM['CMJ-COR']
    contexto = {
        'nav_activo': 'seguimiento',
        'cm_nombre': _nombre_corto(cm) if cm else 'Sin CM asignada',
        'cm_ciudad': _nombre_corto(cm).split(' ', 1)[-1] if cm else '',
        'actualizado': ahora.strftime('%H:%M'),
        'destinos': sorted({b['destino'] for b in bolsines}),
        'datos': {
            'bolsines': bolsines,
            'origen': {'lat': origen[0], 'lng': origen[1], 'nombre': _nombre_corto(cm) if cm else ''},
            'cargando': request.GET.get('demo') == 'cargando',
        },
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY if settings.GOOGLE_MAPS_API_KEY not in ('', 'tu_clave_aqui') else '',
        'google_maps_map_id': getattr(settings, 'GOOGLE_MAPS_MAP_ID', 'DEMO_MAP_ID'),
    }
    return render(request, 'seguimiento/index.html', contexto)
