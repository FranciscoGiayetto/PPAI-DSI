#!/bin/sh
# Arranque en Render: GPS de la cátedra (Java, puerto 8080 interno) + Django (gunicorn, puerto $PORT).
set -e

# Memoria acotada: el plan gratis de Render tiene 512 MB para Java + Python juntos.
JAVA_OPTS="${JAVA_OPTS:--Xmx160m -Xss512k -XX:+UseSerialGC -XX:MaxMetaspaceSize=96m -XX:ReservedCodeCacheSize=32m -XX:TieredStopAtLevel=1}"
echo "Levantando servidor GPS de la cátedra..."
java $JAVA_OPTS -jar /app/gps.jar --server.port=8080 --server.address=127.0.0.1 > /tmp/gps.log 2>&1 &

# La base SQLite se crea en cada arranque (el disco de Render gratis no es persistente).
python manage.py migrate --noinput
python manage.py seed_db

# Esperar al GPS hasta 120 s; si Java no arranca (p. ej. falta memoria), usar el mock en Python.
i=0
until python -c "import socket; socket.create_connection(('127.0.0.1', 8080), 1)" 2>/dev/null; do
  i=$((i + 1))
  if [ "$i" -ge 120 ]; then
    echo "El GPS en Java no respondió; se usa el servidor GPS simulado en Python."
    tail -n 20 /tmp/gps.log || true
    python -c "from bolsines.gps.mock_server import iniciar_servidor_mock_hilo; import time; iniciar_servidor_mock_hilo('127.0.0.1', 8080); time.sleep(10**9)" &
    break
  fi
  sleep 1
done
echo "Servidor GPS listo."

exec gunicorn bolsines_system.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 1 --threads 4 --timeout 60
