"""
GestorSeguimientoBolsines — clase de control del CU 36 (Consultar seguimiento de bolsines).

Sigue el diagrama de clases/secuencia de diseño (patrón Adapter). El Gestor obtiene los bolsines
de la base, le pide la localización a la InterfazGPS y arma los datos para la pantalla.
La vista nunca habla con el GPS: siempre pasa por el Gestor.
"""
from __future__ import annotations

from datetime import datetime

from django.core.mail import send_mail
from django.utils import timezone

from ..gps import GPSTrackerError, InterfazGPS
from ..models import Bolsin, ComisionMedica, Empleado

# Coordenadas aproximadas de cada CM (el modelo de dominio no guarda ubicación); solo para dibujar el destino.
COORDENADAS_CM = {
    'CM-CBA-01': (-31.4201, -64.1888), 'CM-CBA-02': (-31.4167, -64.1833),
    'CM-ROS-02': (-32.9442, -60.6505), 'CM-MDZ-03': (-32.8895, -68.8458),
    'CM-BA-01': (-34.6037, -58.3816), 'CM-TUC-01': (-26.8083, -65.2176),
    'CM-SLA-01': (-24.7821, -65.4232), 'CM-JUJ-01': (-24.1858, -65.2995),
    'CM-NQN-01': (-38.9516, -68.0591), 'CM-MDQ-01': (-38.0055, -57.5426),
    'CM-LPL-01': (-34.9215, -57.9545),
}
_POR_DEFECTO = (-34.6037, -58.3816)


def _coord(cm: ComisionMedica) -> tuple[float, float]:
    return COORDENADAS_CM.get(cm.codigo, _POR_DEFECTO)


def _nombre_corto(cm: ComisionMedica) -> str:
    return cm.nombre.replace('Comisión Médica Jurisdiccional', 'CMJ').replace('Comisión Médica Central', 'CMC')


class GestorSeguimientoBolsines:
    def __init__(self, empleado_logueado: Empleado | None, interfaz_gps: InterfazGPS | None = None) -> None:
        self._empleado_logueado = empleado_logueado
        self._interfaz_gps = interfaz_gps
        self._comision_origen_empleado: ComisionMedica | None = None
        self._bolsines_enviados: list[Bolsin] = []
        self._datos_ubicaciones: list[list[str]] = []
        self._bolsin_seleccionado: Bolsin | None = None
        self.gps_no_disponible = False  # A3 global: el servicio GPS no respondió

    # ── pasos 2 a 6 ────────────────────────────────────────────────────────────
    def nuevo_seguimiento_bolsin(self) -> list[dict]:
        """Paso 1-6: CM del usuario, bolsines Enviados, localización y mapeo para la pantalla."""
        self.obtener_comision_medica_de_empleado_logueado()
        self.buscar_bolsines_enviados_de_comision_medica()          # A1 si queda vacío
        if self._bolsines_enviados:
            self.buscar_datos_localizacion()
        return self.mapeo_bolsin()

    def obtener_comision_medica_de_empleado_logueado(self) -> ComisionMedica | None:
        self._comision_origen_empleado = self._empleado_logueado.cm_asignada if self._empleado_logueado else None
        return self._comision_origen_empleado

    @property
    def nombre_comision_medica(self) -> str:
        cm = self._comision_origen_empleado
        return _nombre_corto(cm) if cm else 'Sin CM asignada'

    @property
    def coordenadas_origen(self) -> tuple[float, float]:
        return _coord(self._comision_origen_empleado) if self._comision_origen_empleado else _POR_DEFECTO

    def buscar_bolsines_enviados_de_comision_medica(self) -> list[Bolsin]:
        if self._comision_origen_empleado is None:
            self._bolsines_enviados = []
        else:
            self._bolsines_enviados = list(
                Bolsin.objects.filter(estado_actual=Bolsin.ESTADO_ENVIADO, cm_origen=self._comision_origen_empleado)
                .select_related('cm_origen', 'cm_destino').prefetch_related('remitos').order_by('nro_bolsin'))
        return self._bolsines_enviados

    def buscar_datos_localizacion(self) -> None:
        """Crea la InterfazGPS y le pide la localización (matriz: nro, CM origen, CM destino)."""
        self._interfaz_gps = self._interfaz_gps or InterfazGPS()
        datos_bolsines = [[str(b.nro_bolsin), b.cm_origen.codigo, b.cm_destino.codigo] for b in self._bolsines_enviados]
        try:
            self.enviar_datos_localizacion(self._interfaz_gps.obtener_localizacion(datos_bolsines))
        except GPSTrackerError:
            self.gps_no_disponible = True                             # A3
            self.enviar_datos_localizacion([])

    def enviar_datos_localizacion(self, datos_localizacion: list[list[str]]) -> None:
        self._datos_ubicaciones = datos_localizacion

    # ── mapeo para la pantalla ────────────────────────────────────────────────
    def mapeo_bolsin(self) -> list[dict]:
        ahora = timezone.localtime()
        por_nro = {int(f[0]): f for f in self._datos_ubicaciones}
        modelo = self._interfaz_gps.modelo_gps_tracker if self._interfaz_gps else ''
        return [self._ubicacion(b, por_nro.get(b.nro_bolsin), ahora, modelo) for b in self._bolsines_enviados]

    @staticmethod
    def _ubicacion(b: Bolsin, fila: list[str] | None, ahora: datetime, modelo: str) -> dict:
        o_lat, o_lng = _coord(b.cm_origen)
        d_lat, d_lng = _coord(b.cm_destino)
        destino = _nombre_corto(b.cm_destino)
        base = {
            'nro': b.nro_bolsin, 'precinto': b.nro_precinto, 'destino': destino,
            'destino_codigo': b.cm_destino.codigo, 'destino_ciudad': destino.split(' ', 1)[-1],
            'peso_kg': round(b.peso_gramos / 1000, 1), 'remitos': len(b.remitos.all()),
            'salio': b.fecha.strftime('%d/%m'), 'gps': modelo,
            'destino_lat': d_lat, 'destino_lng': d_lng,
        }
        if fila is None:   # el GPS no informó este bolsín (A3)
            return {**base, 'avance': 0, 'sin_senal': True, 'lat': None, 'lng': None,
                    'ultima_senal': '—', 'hace_min': 0}
        lat, lng = float(fila[1]), float(fila[2])
        fecha = datetime.fromisoformat(fila[3])
        if timezone.is_naive(fecha):
            fecha = timezone.make_aware(fecha)
        # Avance aproximado sobre la recta origen→destino (para la barra de trayecto).
        total = ((d_lat - o_lat) ** 2 + (d_lng - o_lng) ** 2) ** 0.5 or 1
        hecho = ((lat - o_lat) ** 2 + (lng - o_lng) ** 2) ** 0.5
        return {**base, 'avance': round(min(hecho / total, 1), 2), 'sin_senal': False,
                'lat': round(lat, 4), 'lng': round(lng, 4),
                'ultima_senal': timezone.localtime(fecha).strftime('%d/%m %H:%M'),
                'hace_min': max(int((ahora - fecha).total_seconds() // 60), 0)}

    # ── pasos 7 a 9 ───────────────────────────────────────────────────────────
    def tomar_seleccion_bolsin(self, nro_bolsin: int) -> Bolsin | None:
        self._bolsin_seleccionado = next((b for b in self._bolsines_enviados if b.nro_bolsin == nro_bolsin), None)
        return self._bolsin_seleccionado

    def tomar_confirmacion_enviar_correo(self, nro_bolsin: int) -> bool:
        """El EB confirmó (paso 9): ejecuta el CU 30. Devuelve False si no hay ubicación o gerente."""
        bolsin = self.tomar_seleccion_bolsin(nro_bolsin)
        fila = next((f for f in self._datos_ubicaciones if int(f[0]) == nro_bolsin), None)
        if bolsin is None or fila is None:
            return False
        return self.notificar_ubicacion_de_bolsin(bolsin, fila)

    def notificar_ubicacion_de_bolsin(self, bolsin: Bolsin, fila: list[str]) -> bool:
        """CU 30 (simplificado): correo al/los Gerente(s) de la CM destino con la ubicación."""
        gerentes = Empleado.objects.filter(rol=Empleado.ROL_GERENTE_CM, cm_asignada=bolsin.cm_destino,
                                           activo=True).select_related('user')
        destinatarios = [g.user.email for g in gerentes if g.user.email]
        if not destinatarios:
            return False
        send_mail(
            subject=f'Ubicación del bolsín N.º {bolsin.nro_bolsin}',
            message=(f'El bolsín N.º {bolsin.nro_bolsin} (precinto {bolsin.nro_precinto}) enviado desde '
                     f'{bolsin.cm_origen.nombre} está en latitud {fila[1]}, longitud {fila[2]} '
                     f'(última actualización: {fila[3]}).'),
            from_email=None, recipient_list=destinatarios)
        return True
