"""
Servidor HTTP Mock para la API de GPS Tracker (puerto 8080).

Implementa los endpoints exactos de la aplicación Spring Boot de la cátedra
(GpsTrackerMockApplication / dsi-api-bolsines) para garantizar que el servidor
GPS siempre funcione, aun si Java 17 no está disponible en la máquina.
"""
import json
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

API_KEYS = {
    'xtr': 'sk_xtr_9F3a7C21bE6d4A10f2c8e5b7d913',
    'nav': 'sk_nav_7b61d9e4c3a2485fae10c77d5b2f',
    'geo': 'sk_geo_f2d84a1c9e7345b8a6d1c3f0972e',
}

# Base de datos en memoria con posiciones geográficas reales en Argentina.
# `hace_min`: antigüedad de la última señal; la fecha se calcula en cada consulta para que siempre sea reciente.
BOLSINES_DB = {
    # ── Bolsines oficiales de la cátedra (dsi-api-bolsines) ──
    101: {'origenes': ['CM-CBA-01', 'CMJ-COR'], 'destinos': ['CM-ROS-02', 'CMJ-ROS'], 'lat': -31.9201, 'lng': -63.1888, 'hace_min': 4},
    102: {'origenes': ['CM-ROS-02', 'CMJ-ROS'], 'destinos': ['CM-MDZ-03', 'CMJ-MZA'], 'lat': -32.9468, 'lng': -60.6393, 'hace_min': 7},
    103: {'origenes': ['CM-MDZ-03', 'CMJ-MZA'], 'destinos': ['CM-BA-01', 'CMC-CABA'], 'lat': -32.8895, 'lng': -68.8458, 'hace_min': 2},
    104: {'origenes': ['CM-BA-01', 'CMC-CABA'], 'destinos': ['CM-CBA-01', 'CMJ-COR'], 'lat': -34.6037, 'lng': -58.3816, 'hace_min': 11},
    105: {'origenes': ['CM-TUC-01', 'CMJ-TUC'], 'destinos': ['CM-SLA-01', 'CMJ-SAL'], 'lat': -26.8083, 'lng': -65.2176, 'hace_min': 5},
    106: {'origenes': ['CM-SLA-01', 'CMJ-SAL'], 'destinos': ['CM-JUJ-01', 'CMJ-JUJ'], 'lat': -24.7829, 'lng': -65.4232, 'hace_min': 9},
    107: {'origenes': ['CM-NQN-01'], 'destinos': ['CM-MDQ-01'], 'lat': -38.9516, 'lng': -68.0591, 'hace_min': 3},
    108: {'origenes': ['CM-MDQ-01'], 'destinos': ['CM-BA-01'], 'lat': -38.0055, 'lng': -57.5426, 'hace_min': 14},
    109: {'origenes': ['CM-LPL-01'], 'destinos': ['CM-CBA-01'], 'lat': -34.9215, 'lng': -57.9545, 'hace_min': 6},
    110: {'origenes': ['CM-CBA-02'], 'destinos': ['CM-ROS-02'], 'lat': -31.4167, 'lng': -64.1833, 'hace_min': 8},

    # ── Bolsines de la demo de interfaz ──
    1048: {'origenes': ['CMJ-COR', 'CM-CBA-01'], 'destinos': ['CMC-CABA', 'CM-BA-01'], 'lat': -33.2500, 'lng': -61.2000, 'hace_min': 3},
    1047: {'origenes': ['CMJ-COR', 'CM-CBA-01'], 'destinos': ['CMJ-ROS', 'CM-ROS-02'], 'lat': -32.1800, 'lng': -62.4100, 'hace_min': 6},
    1046: {'origenes': ['CMJ-COR', 'CM-CBA-01'], 'destinos': ['CMJ-MZA', 'CM-MDZ-03'], 'lat': -32.1500, 'lng': -66.5000, 'hace_min': 12},
    1044: {'origenes': ['CMJ-COR', 'CM-CBA-01'], 'destinos': ['CMJ-TUC', 'CM-TUC-01'], 'lat': -29.1000, 'lng': -64.7000, 'hace_min': 5},
    1043: {'origenes': ['CMJ-COR', 'CM-CBA-01'], 'destinos': ['CMC-CABA', 'CM-BA-01'], 'lat': -33.8000, 'lng': -60.1000, 'hace_min': 9},
    # El bolsín 1041 NO se incluye: simula el Flujo A3 (GPS sin señal).
}


def _fecha(bolsin) -> str:
    return (datetime.now() - timedelta(minutes=bolsin['hace_min'])).strftime('%Y-%m-%dT%H:%M:%S')


class GpsMockRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silencioso para no ensuciar la salida de Django

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        api_key = self.headers.get('X-API-Key', '')

        # Health check
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'UP'}).encode('utf-8'))
            return

        nro_param = params.get('numeroBolsin', [None])[0]
        nro = int(nro_param) if nro_param and nro_param.isdigit() else None
        bolsin = BOLSINES_DB.get(nro) if nro else None

        # ── 1. Modelo XTR-4500L ──
        if path == '/api/xtr-4500l/getBolsinLocation':
            if api_key != API_KEYS['xtr']:
                self.send_response(401)
                self.end_headers()
                return
            if not bolsin:
                self.send_response(404)
                self.end_headers()
                return

            cm_origen = params.get('codigoComisionMedicaOrigen', [''])[0].upper()
            if cm_origen and not any(cm_origen == o.upper() for o in bolsin['origenes']):
                self.send_response(400)
                self.end_headers()
                return

            resp = {
                'items': [{
                    'numeroBolsin': nro,
                    'latitud': bolsin['lat'],
                    'longitud': bolsin['lng'],
                    'fechaHoraUltimaActualizacion': _fecha(bolsin),
                }]
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        # ── 2. Modelo NavTrack QX-7A ──
        if path == '/api/navtrack-qx-7a/retrieveTrackingData':
            if api_key != API_KEYS['nav']:
                self.send_response(401)
                self.end_headers()
                return
            if not bolsin:
                self.send_response(404)
                self.end_headers()
                return

            cm_dest = params.get('codigoComisionMedicaDestino', [''])[0].upper()
            if cm_dest and not any(cm_dest == d.upper() for d in bolsin['destinos']):
                self.send_response(400)
                self.end_headers()
                return

            csv_text = f"{nro},{bolsin['lat']},{bolsin['lng']},{_fecha(bolsin)}"
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(csv_text.encode('utf-8'))
            return

        # ── 3. Modelo GeoPulse MTR-900 ──
        if path == '/api/geopulse-mtr-900/fetchCargoPositions':
            if api_key != API_KEYS['geo']:
                self.send_response(401)
                self.end_headers()
                return
            if not bolsin:
                self.send_response(404)
                self.end_headers()
                return

            matriz = [[nro, bolsin['lat'], bolsin['lng'], _fecha(bolsin)]]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(matriz).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()


def iniciar_servidor_mock_hilo(host='localhost', port=8080) -> HTTPServer:
    """Inicia el servidor mock en un hilo background de forma no bloqueante."""
    server = HTTPServer((host, port), GpsMockRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
