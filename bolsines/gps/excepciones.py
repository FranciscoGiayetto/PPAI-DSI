"""Excepciones del subsistema GPS."""


class GPSTrackerError(Exception):
    """Error genérico al consultar un GPS Tracker (flujo alternativo A3)."""


class GPSServicioNoDisponible(GPSTrackerError):
    """El servicio GPS no responde (caído, timeout, sin red)."""


class GPSBolsinSinLocalizacion(GPSTrackerError):
    """El servicio GPS respondió, pero no informa la ubicación de ese bolsín (404, 401, 400...)."""
