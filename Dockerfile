# Imagen única para Render: Django (gunicorn) + servidor GPS oficial de la cátedra (Spring Boot).

# ── Etapa 1: compilar la API GPS de la cátedra (dsi-api-bolsines) ──
FROM maven:3.9-eclipse-temurin-17 AS gps
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
WORKDIR /src
# Mismo commit que el submódulo gps-api/ (se clona acá por si Render no baja submódulos).
RUN git clone https://github.com/LiberaeMentis/dsi-api-bolsines.git . \
    && git checkout bd457ed8349a08dad9f3533dd93530aebf844204 \
    && mvn -q -DskipTests package \
    && cp target/*.jar /gps.jar

# ── Etapa 2: aplicación Django + JRE 17 ──
FROM python:3.11-slim
COPY --from=eclipse-temurin:17-jre /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk \
    PATH="/opt/java/openjdk/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=False \
    GPS_API_BASE_URL=http://127.0.0.1:8080

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=gps /gps.jar /app/gps.jar
RUN python manage.py collectstatic --noinput && chmod +x deploy/start.sh

CMD ["sh", "deploy/start.sh"]
