"""
Adaptables del patrón Adapter: un cliente HTTP por modelo de GPS Tracker.

Cada uno expone la interfaz *propia* (incompatible con las otras) del dispositivo, tal como
la publica el servidor GPS de la cátedra (`gps-api/`). No contienen lógica de negocio.
"""
from __future__ import annotations

import requests
from django.conf import settings

from .excepciones import GPSBolsinSinLocalizacion, GPSServicioNoDisponible

TIMEOUT_SEGUNDOS = 5


def _get(ruta: str, api_key: str, **params):
    """GET autenticado contra el servidor GPS; traduce los errores de transporte."""
    url = f'{settings.GPS_API_BASE_URL.rstrip("/")}{ruta}'
    try:
        resp = requests.get(url, params=params, headers={'X-API-Key': api_key}, timeout=TIMEOUT_SEGUNDOS)
    except requests.RequestException as exc:
        raise GPSServicioNoDisponible(f'No se pudo contactar al servidor GPS: {exc}') from exc
    if resp.status_code >= 500:
        raise GPSServicioNoDisponible(f'El servidor GPS respondió {resp.status_code}')
    if resp.status_code >= 400:
        raise GPSBolsinSinLocalizacion(f'El GPS no informa el bolsín {params.get("numeroBolsin")} ({resp.status_code})')
    return resp


class ServicioGPSTrackerXTR4500L:
    """XTR-4500L: recibe nro. de bolsín + CM origen y responde un JSON (texto)."""

    def getBolsinLocation(self, apiKey: str, numeroBolsin: int, codigoCMOrigen: str) -> str:  # noqa: N802,N803
        return _get('/api/xtr-4500l/getBolsinLocation', apiKey,
                    numeroBolsin=numeroBolsin, codigoComisionMedicaOrigen=codigoCMOrigen).text


class ServicioGPSTrackerNavTrackQX7A:
    """NavTrack QX-7A: recibe nro. de bolsín + CM destino y responde una línea CSV."""

    def retrieveTrackingData(self, apiKey: str, numeroBolsin: int, codigoCMDestino: str) -> str:  # noqa: N802,N803
        return _get('/api/navtrack-qx-7a/retrieveTrackingData', apiKey,
                    numeroBolsin=numeroBolsin, codigoComisionMedicaDestino=codigoCMDestino).text


class ServicioGPSTrackerGeoPulseMTR900:
    """GeoPulse MTR-900: recibe solo el nro. de bolsín y responde una matriz."""

    def fetchCargoPositions(self, apiKey: str, numeroBolsin: int) -> list[list]:  # noqa: N802,N803
        return _get('/api/geopulse-mtr-900/fetchCargoPositions', apiKey, numeroBolsin=numeroBolsin).json()
