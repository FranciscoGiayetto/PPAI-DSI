"""InterfazGPS: clase boundary y *Cliente* del patrón Adapter."""
from __future__ import annotations

from django.conf import settings

from .adaptadores import (AdaptadorGPSGeoPulseMTR900, AdaptadorGPSNavTrackQX7A, AdaptadorGPSXTR4500L,
                          IAdaptadorGPSTracker, Matriz)

_ADAPTADORES = {
    'XTR4500L': AdaptadorGPSXTR4500L,
    'NAVTRACKQX7A': AdaptadorGPSNavTrackQX7A,
    'GEOPULSEMTR900': AdaptadorGPSGeoPulseMTR900,
}


class InterfazGPS:
    """
    Según el modelo de GPS Tracker en uso crea el adaptador concreto (con su clave API) y le
    delega la obtención y adaptación de los datos. Solo conoce `IAdaptadorGPSTracker`.
    """

    def __init__(self, modelo_gps_tracker: str | None = None) -> None:
        self._modelo_gps_tracker = (modelo_gps_tracker or settings.GPS_MODEL_DEFAULT).upper().replace('-', '')
        if self._modelo_gps_tracker not in _ADAPTADORES:
            raise ValueError(f'Modelo de GPS Tracker desconocido: {self._modelo_gps_tracker}')
        self._claves_api_gps_tracker: dict[str, str] = settings.GPS_API_KEYS
        self._datos_localizacion: Matriz = []

    @property
    def modelo_gps_tracker(self) -> str:
        return self._modelo_gps_tracker

    def _crear_adaptador(self) -> IAdaptadorGPSTracker:
        clave = self._claves_api_gps_tracker[self._modelo_gps_tracker]
        return _ADAPTADORES[self._modelo_gps_tracker](clave)

    def obtener_localizacion(self, datos_bolsines: Matriz) -> Matriz:
        """Devuelve [[nro, lat, lng, fecha_hora], ...] (la entrega al Gestor es `enviarDatosLocalizacion`)."""
        adaptador = self._crear_adaptador()
        self._datos_localizacion = adaptador.obtener_localizacion_bolsines(datos_bolsines)
        return self._datos_localizacion
