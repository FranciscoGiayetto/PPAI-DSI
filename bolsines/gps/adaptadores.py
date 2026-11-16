"""
Objetivo (IAdaptadorGPSTracker) y Adaptadores del patrón Adapter (GoF).

Formatos de la matriz de entrada y salida (una fila por bolsín):
  entrada  `datos_bolsines`: [nro_bolsin, codigo_cm_origen, codigo_cm_destino]
  salida   `localizaciones`: [nro_bolsin, latitud, longitud, fecha_hora_ultima_actualizacion]
Si el GPS no informa un bolsín, ese bolsín no aparece en la salida (el Gestor lo trata como A3).
Los adaptadores solo traducen interfaces; no contienen lógica de negocio.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod

from .excepciones import GPSBolsinSinLocalizacion
from .servicios import (ServicioGPSTrackerGeoPulseMTR900, ServicioGPSTrackerNavTrackQX7A,
                        ServicioGPSTrackerXTR4500L)

Matriz = list[list[str]]


class IAdaptadorGPSTracker(ABC):
    """Interfaz objetivo: lo único que conoce la InterfazGPS."""

    @abstractmethod
    def adaptar_localizacion(self) -> None:
        """Transforma lo recibido del servicio al formato común."""

    @abstractmethod
    def obtener_localizacion_bolsines(self, datos_bolsines: Matriz) -> Matriz:
        """Pide y adapta la localización de los bolsines (template method: solicitar + adaptar)."""

    @abstractmethod
    def solicitar_localizacion(self, datos_bolsines: Matriz) -> None:
        """Adapta el pedido al formato del servicio y lo invoca."""


class _AdaptadorBase(IAdaptadorGPSTracker):
    def __init__(self, clave_api: str) -> None:
        self._clave_api = clave_api
        self._localizaciones_adaptadas: Matriz = []
        self._localizaciones_recibidas: list = []

    def obtener_localizacion_bolsines(self, datos_bolsines: Matriz) -> Matriz:
        self._localizaciones_adaptadas = []
        self._localizaciones_recibidas = []
        self.solicitar_localizacion(datos_bolsines)
        self.adaptar_localizacion()
        return self._localizaciones_adaptadas


class AdaptadorGPSXTR4500L(_AdaptadorBase):
    """Adapta el XTR-4500L (nro int + CM origen -> JSON) a la interfaz común."""

    def __init__(self, clave_api: str, servicio: ServicioGPSTrackerXTR4500L | None = None) -> None:
        super().__init__(clave_api)
        self._servicio = servicio or ServicioGPSTrackerXTR4500L()

    def solicitar_localizacion(self, datos_bolsines: Matriz) -> None:
        for nro, cm_origen, _cm_destino in datos_bolsines:
            try:
                self._localizaciones_recibidas.append(
                    self._servicio.getBolsinLocation(self._clave_api, int(nro), cm_origen))
            except GPSBolsinSinLocalizacion:
                continue

    def adaptar_localizacion(self) -> None:
        for texto in self._localizaciones_recibidas:
            for item in json.loads(texto)['items']:
                self._localizaciones_adaptadas.append([
                    str(item['numeroBolsin']), str(item['latitud']), str(item['longitud']),
                    str(item['fechaHoraUltimaActualizacion'])])


class AdaptadorGPSNavTrackQX7A(_AdaptadorBase):
    """Adapta el NavTrack QX-7A (nro int + CM destino -> CSV) a la interfaz común."""

    def __init__(self, clave_api: str, servicio: ServicioGPSTrackerNavTrackQX7A | None = None) -> None:
        super().__init__(clave_api)
        self._servicio = servicio or ServicioGPSTrackerNavTrackQX7A()

    def solicitar_localizacion(self, datos_bolsines: Matriz) -> None:
        for nro, _cm_origen, cm_destino in datos_bolsines:
            try:
                self._localizaciones_recibidas.append(
                    self._servicio.retrieveTrackingData(self._clave_api, int(nro), cm_destino))
            except GPSBolsinSinLocalizacion:
                continue

    def adaptar_localizacion(self) -> None:
        for linea in self._localizaciones_recibidas:
            nro, lat, lng, fecha_hora = linea.strip().split(',')
            self._localizaciones_adaptadas.append([nro, lat, lng, fecha_hora])


class AdaptadorGPSGeoPulseMTR900(_AdaptadorBase):
    """Adapta el GeoPulse MTR-900 (solo nro int -> matriz de objetos) a la interfaz común."""

    def __init__(self, clave_api: str, servicio: ServicioGPSTrackerGeoPulseMTR900 | None = None) -> None:
        super().__init__(clave_api)
        self._servicio = servicio or ServicioGPSTrackerGeoPulseMTR900()

    def solicitar_localizacion(self, datos_bolsines: Matriz) -> None:
        for nro, _cm_origen, _cm_destino in datos_bolsines:
            try:
                self._localizaciones_recibidas.append(self._servicio.fetchCargoPositions(self._clave_api, int(nro)))
            except GPSBolsinSinLocalizacion:
                continue

    def adaptar_localizacion(self) -> None:
        for matriz in self._localizaciones_recibidas:
            for nro, lat, lng, fecha_hora in matriz:
                self._localizaciones_adaptadas.append([str(nro), str(lat), str(lng), str(fecha_hora)])
