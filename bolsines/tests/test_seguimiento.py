"""Tests del patrón Adapter, el Gestor y la vista del CU 36 (sin servidor GPS real: servicios simulados)."""
import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings

from bolsines.gps import GPSTrackerError, InterfazGPS
from bolsines.gps.adaptadores import (AdaptadorGPSGeoPulseMTR900, AdaptadorGPSNavTrackQX7A, AdaptadorGPSXTR4500L)
from bolsines.gps.excepciones import GPSBolsinSinLocalizacion, GPSServicioNoDisponible
from bolsines.models import Bolsin, ComisionMedica, Empleado
from bolsines.services.gestor_seguimiento import GestorSeguimientoBolsines

DATOS = [['101', 'CM-CBA-01', 'CM-ROS-02']]
ESPERADO = [['101', '-31.4201', '-64.1888', '2026-03-07T12:30:00']]


class AdaptadoresTests(TestCase):
    """Los 3 adaptadores devuelven la misma estructura aunque el servicio responda distinto."""

    def test_xtr4500l(self):
        srv = MagicMock()
        srv.getBolsinLocation.return_value = json.dumps({'items': [{
            'numeroBolsin': 101, 'latitud': -31.4201, 'longitud': -64.1888,
            'fechaHoraUltimaActualizacion': '2026-03-07T12:30:00'}]})
        res = AdaptadorGPSXTR4500L('k', srv).obtener_localizacion_bolsines(DATOS)
        srv.getBolsinLocation.assert_called_once_with('k', 101, 'CM-CBA-01')
        self.assertEqual(res, ESPERADO)

    def test_navtrack(self):
        srv = MagicMock()
        srv.retrieveTrackingData.return_value = '101,-31.4201,-64.1888,2026-03-07T12:30:00'
        res = AdaptadorGPSNavTrackQX7A('k', srv).obtener_localizacion_bolsines(DATOS)
        srv.retrieveTrackingData.assert_called_once_with('k', 101, 'CM-ROS-02')
        self.assertEqual(res, ESPERADO)

    def test_geopulse(self):
        srv = MagicMock()
        srv.fetchCargoPositions.return_value = [[101, -31.4201, -64.1888, '2026-03-07T12:30:00']]
        res = AdaptadorGPSGeoPulseMTR900('k', srv).obtener_localizacion_bolsines(DATOS)
        srv.fetchCargoPositions.assert_called_once_with('k', 101)
        self.assertEqual(res, ESPERADO)

    def test_bolsin_sin_localizacion_se_omite(self):
        srv = MagicMock()
        srv.fetchCargoPositions.side_effect = GPSBolsinSinLocalizacion('404')
        self.assertEqual(AdaptadorGPSGeoPulseMTR900('k', srv).obtener_localizacion_bolsines(DATOS), [])

    def test_servicio_caido_propaga_error(self):
        srv = MagicMock()
        srv.fetchCargoPositions.side_effect = GPSServicioNoDisponible('caído')
        with self.assertRaises(GPSTrackerError):
            AdaptadorGPSGeoPulseMTR900('k', srv).obtener_localizacion_bolsines(DATOS)


class InterfazGPSTests(TestCase):
    def test_modelo_desconocido(self):
        with self.assertRaises(ValueError):
            InterfazGPS('OTRO')

    def test_crea_adaptador_segun_modelo(self):
        self.assertIsInstance(InterfazGPS('NavTrack-QX7A')._crear_adaptador(), AdaptadorGPSNavTrackQX7A)
        self.assertIsInstance(InterfazGPS('XTR4500L')._crear_adaptador(), AdaptadorGPSXTR4500L)
        self.assertIsInstance(InterfazGPS('GEOPULSEMTR900')._crear_adaptador(), AdaptadorGPSGeoPulseMTR900)


@override_settings(EMAIL_REDIRIGIR_A='')
class BaseDatos(TestCase):
    def setUp(self):
        self.orig = ComisionMedica.objects.create(codigo='CM-CBA-01', nombre='Comisión Médica Jurisdiccional Córdoba', tipo='CMJ')
        self.dest = ComisionMedica.objects.create(codigo='CM-ROS-02', nombre='Comisión Médica Jurisdiccional Rosario', tipo='CMJ')
        user = User.objects.create_user('eb', password='x')
        self.eb = Empleado.objects.create(user=user, legajo='1', rol=Empleado.ROL_ENCARGADO_BOLSINES, cm_asignada=self.orig)
        g = User.objects.create_user('gcm', password='x', email='g@test.com')
        Empleado.objects.create(user=g, legajo='2', rol=Empleado.ROL_GERENTE_CM, cm_asignada=self.dest)
        self.b = Bolsin.objects.create(nro_bolsin=101, fecha='2026-03-07', peso_gramos=1000, nro_precinto='P1',
                                       cm_origen=self.orig, cm_destino=self.dest, estado_actual=Bolsin.ESTADO_ENVIADO)

    def interfaz_falsa(self, filas=None, error=None):
        gps = MagicMock(modelo_gps_tracker='XTR4500L')
        if error:
            gps.obtener_localizacion.side_effect = error
        else:
            gps.obtener_localizacion.return_value = filas
        return gps


class GestorTests(BaseDatos):
    def test_flujo_principal(self):
        g = GestorSeguimientoBolsines(self.eb, self.interfaz_falsa(ESPERADO))
        res = g.nuevo_seguimiento_bolsin()
        self.assertEqual(len(res), 1)
        self.assertFalse(res[0]['sin_senal'])
        self.assertEqual(res[0]['lat'], -31.4201)

    def test_a1_sin_bolsines_enviados(self):
        self.b.estado_actual = Bolsin.ESTADO_CERRADO
        self.b.save()
        self.assertEqual(GestorSeguimientoBolsines(self.eb, self.interfaz_falsa([])).nuevo_seguimiento_bolsin(), [])

    def test_solo_cm_origen_del_usuario(self):
        otro = Empleado.objects.get(legajo='2')
        self.assertEqual(GestorSeguimientoBolsines(otro, self.interfaz_falsa([])).nuevo_seguimiento_bolsin(), [])

    def test_a3_gps_caido(self):
        g = GestorSeguimientoBolsines(self.eb, self.interfaz_falsa(error=GPSServicioNoDisponible('x')))
        res = g.nuevo_seguimiento_bolsin()
        self.assertTrue(g.gps_no_disponible)
        self.assertTrue(res[0]['sin_senal'])

    def test_a3_bolsin_no_informado(self):
        res = GestorSeguimientoBolsines(self.eb, self.interfaz_falsa([])).nuevo_seguimiento_bolsin()
        self.assertTrue(res[0]['sin_senal'])

    def test_cu30_envia_correo_al_gerente(self):
        g = GestorSeguimientoBolsines(self.eb, self.interfaz_falsa(ESPERADO))
        g.nuevo_seguimiento_bolsin()
        self.assertTrue(g.tomar_confirmacion_enviar_correo(101))
        correo = mail.outbox[0]
        self.assertEqual(correo.to, ['g@test.com'])
        html = correo.alternatives[0][0]
        self.assertEqual(correo.alternatives[0][1], 'text/html')
        # número de bolsín, fecha/hora, coordenadas y CM destino (ERS, CU 36 paso 11)
        for dato in ('101', '-31.4201', '-64.1888', '2026-03-07T12:30:00', self.dest.nombre):
            self.assertIn(dato, html)
            self.assertIn(dato, correo.body)
        # wordmark + camioncito de marca, embebidos inline (cid)
        self.assertEqual(correo.mixed_subtype, 'related')
        cids = {a.get('Content-ID') for a in correo.attachments}
        self.assertEqual(cids, {'<bolsines-wordmark>', '<bolsines-camioncito>'})
        # fuera de modo prueba no debe aparecer el aviso de desvío
        self.assertNotIn('[Modo prueba]', html)
        self.assertNotIn('[Modo prueba]', correo.body)

    @override_settings(EMAIL_REDIRIGIR_A='prueba@test.com')
    def test_cu30_modo_prueba_desvia_correo(self):
        g = GestorSeguimientoBolsines(self.eb, self.interfaz_falsa(ESPERADO))
        g.nuevo_seguimiento_bolsin()
        self.assertTrue(g.tomar_confirmacion_enviar_correo(101))
        correo = mail.outbox[0]
        self.assertEqual(correo.to, ['prueba@test.com'])
        self.assertIn('[PRUEBA]', correo.subject)
        self.assertIn('g@test.com', correo.alternatives[0][0])
        self.assertIn('g@test.com', correo.body)


class VistaTests(BaseDatos):
    def test_requiere_login(self):
        self.assertEqual(self.client.get('/seguimiento/').status_code, 302)

    @patch('bolsines.services.gestor_seguimiento.InterfazGPS')
    def test_vista_ok(self, interfaz):
        interfaz.return_value = self.interfaz_falsa(ESPERADO)
        self.client.login(username='eb', password='x')
        r = self.client.get('/seguimiento/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'CMJ Córdoba')

    @patch('bolsines.services.gestor_seguimiento.InterfazGPS')
    def test_notificar(self, interfaz):
        interfaz.return_value = self.interfaz_falsa(ESPERADO)
        self.client.login(username='eb', password='x')
        r = self.client.post('/seguimiento/101/notificar/')
        self.assertEqual(r.json(), {'ok': True})
        self.assertEqual(len(mail.outbox), 1)
