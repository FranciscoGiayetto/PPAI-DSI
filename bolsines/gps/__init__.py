"""Patrón Adapter para los GPS Tracker (XTR-4500L, NavTrack QX-7A, GeoPulse MTR-900)."""
from .excepciones import GPSTrackerError
from .interfaz_gps import InterfazGPS

__all__ = ['InterfazGPS', 'GPSTrackerError']
