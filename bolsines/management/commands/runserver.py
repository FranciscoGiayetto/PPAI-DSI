"""
runserver que además levanta el servidor GPS de la cátedra (gps-api/, Spring Boot).
Usar --sin-gps para no levantarlo.
"""
import atexit
import os
import signal
import socket
import subprocess
import sys
import time
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand

GPS_DIR = settings.BASE_DIR / 'gps-api'


def _puerto_en_uso(host, port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


class Command(RunserverCommand):
    help = 'Levanta Django y el servidor GPS de la cátedra.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--sin-gps', action='store_true', help='No levantar el servidor GPS.')

    def handle(self, *args, **options):
        # El autoreloader re-ejecuta este comando en un proceso hijo (RUN_MAIN=true): solo el padre lanza el GPS.
        if not options['sin_gps'] and os.environ.get('RUN_MAIN') != 'true':
            self._iniciar_gps()
        super().handle(*args, **options)

    def _iniciar_gps(self):
        url = urlparse(settings.GPS_API_BASE_URL)
        host, port = url.hostname or 'localhost', url.port or 8080

        if _puerto_en_uso(host, port):
            self.stdout.write(f'Servidor GPS ya corriendo en {settings.GPS_API_BASE_URL}')
            return
        if not (GPS_DIR / 'pom.xml').exists():
            self.stderr.write('No se encontró gps-api/. Ejecutá: git submodule update --init')
            return

        windows = sys.platform == 'win32'
        # mvnw trae un BOM antes del shebang, por eso se invoca vía sh
        mvnw = [str(GPS_DIR / 'mvnw.cmd')] if windows else ['sh', str(GPS_DIR / 'mvnw')]

        log = open(settings.BASE_DIR / 'gps-api.log', 'w')
        proc = subprocess.Popen(
            [*mvnw, '-q', 'spring-boot:run', f'-Dspring-boot.run.arguments=--server.port={port}'],
            cwd=GPS_DIR, stdout=log, stderr=subprocess.STDOUT,
            start_new_session=not windows,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if windows else 0,
        )

        def detener():
            if proc.poll() is None:
                if windows:
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    os.killpg(proc.pid, signal.SIGTERM)
            log.close()

        atexit.register(detener)
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

        self.stdout.write(f'Levantando servidor GPS en {settings.GPS_API_BASE_URL} (log: gps-api.log)...')
        for _ in range(180):
            if _puerto_en_uso(host, port):
                self.stdout.write(self.style.SUCCESS('Servidor GPS listo.'))
                return
            if proc.poll() is not None:
                self.stderr.write('El servidor GPS terminó con error. Revisá gps-api.log (¿Java 17 instalado?).')
                return
            time.sleep(1)
        self.stderr.write('El servidor GPS no respondió a tiempo; Django arranca igual.')
