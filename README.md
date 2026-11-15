# Sistema Bolsines — PPAI 2026
### UTN · Diseño de Sistemas I · Grupo 5

---

## ¿Por qué Django monolítico?

Esta decisión de arquitectura no es casual: responde a un análisis concreto del problema, el equipo y las restricciones del proyecto.

### El problema de FastAPI + React para este caso

Una arquitectura separada (API REST + SPA) implica **tres procesos corriendo al mismo tiempo**:

```
Terminal 1 → Servidor GPS de la cátedra   (puerto 8001)  ← externo, obligatorio
Terminal 2 → FastAPI backend               (puerto 8000)
Terminal 3 → React (npm start)             (puerto 3000)
```

Esto introduce riesgos que no aportan valor académico:
- CORS mal configurado → la app no funciona
- `npm install` lento en la defensa oral → tiempo perdido
- Tres ambientes a sincronizar → tres puntos de falla
- JWT manual → complejidad que el docente no evalúa
- El patrón Adapter vive igual en Python, independientemente del framework web

### Por qué Django es la decisión correcta de diseño

**Principio de diseño central: la complejidad debe justificarse con valor entregado.**

FastAPI + React resuelve el problema de escalar equipos grandes con frontend desacoplado.
Nosotros somos un equipo pequeño con un deadline académico, donde lo que se califica es:
el **patrón Adapter**, la **consistencia diagrama ↔ código**, y la **funcionalidad ejecutable**.

| Criterio | Django monolítico | FastAPI + React |
|---|---|---|
| Servidores en defensa | **2** (GPS + Django) | 3 (GPS + API + React) |
| Auth, sesiones | **Incluido** | Manual (JWT) |
| ORM + migraciones | **Incluido** | SQLAlchemy + Alembic |
| Admin para datos de prueba | **Incluido** | No existe |
| Google Maps (mapa) | JS nativo en template | JS nativo en React |
| Valor agregado sobre Adapter | Ninguno | Ninguno |
| Tiempo de setup | **Bajo** | Alto |

> Django no es la herramienta "más moderna" — es la herramienta **correcta para este problema**.
> Un buen diseñador elige la herramienta que minimiza el riesgo y maximiza el tiempo
> disponible para lo que importa.

---

## Caso de Uso implementado

**CU 36 — Consultar seguimiento de bolsines** (Grupo impar → Grupo 5)

Actor principal: Encargado de Bolsines (EB)
Actores secundarios: GPS Tracker (3 modelos) · Google Maps · Servidor de Correo

Patrón de diseño aplicado: **Adapter (GoF)** — unifica la interfaz de los 3 modelos GPS.

---

## Requisitos previos

```bash
python --version    # Python 3.11 o superior
pip --version
```

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPO>
cd PPAI-DSI

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores (ver sección Variables de Entorno)

# 5. Aplicar migraciones
python manage.py migrate

# 6. Cargar datos de prueba
python manage.py seed_db

# 7. Crear superusuario (opcional, para admin)
python manage.py createsuperuser
```

---

## Ejecución

El servidor GPS de la cátedra ([dsi-api-bolsines](https://github.com/LiberaeMentis/dsi-api-bolsines), Spring Boot)
está incluido como submódulo en `gps-api/` y **se levanta solo** al correr `runserver`.

Requisito extra: **Java 17 JDK** (`sudo apt install openjdk-17-jdk-headless` en Ubuntu).

```bash
git submodule update --init      # solo la primera vez (o clonar con --recurse-submodules)
source venv/bin/activate
python manage.py runserver
# GPS en http://localhost:8080 (log en gps-api.log) · App en http://localhost:8000
```

- La primera vez Maven descarga dependencias y puede tardar un par de minutos.
- Si el GPS ya está corriendo en el puerto 8080, no se lanza otro.
- `python manage.py runserver --sin-gps` arranca solo Django.
- Al cortar con Ctrl+C se detienen ambos.

Abrir el navegador en: **http://localhost:8000**

---

## Variables de entorno (`.env`)

```env
# GPS Tracker — servidor local de la cátedra
GPS_API_BASE_URL=http://localhost:8001
GPS_API_KEY=test_api_key

# Modelo GPS activo por defecto
# Opciones: XTR4500L | NAVTRACKQX7A | GEOPULSEMTR900
GPS_MODEL_DEFAULT=XTR4500L

# Google Maps (clave de la API)
GOOGLE_MAPS_API_KEY=tu_clave_aqui

# Django
SECRET_KEY=cambiar-esto-en-produccion
DEBUG=True
```

---

## Estructura del proyecto

```
PPAI-DSI/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── CONTEXT.md                          ← contexto para IAs del equipo
│
├── bolsines_system/                    ← configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── bolsines/                           ← app principal
    ├── admin.py                        ← modelos registrados en /admin
    ├── urls.py
    │
    ├── models/                         ← dominio del sistema
    │   ├── comision_medica.py
    │   ├── empleado.py
    │   ├── bolsin.py                   ← estados: Creado→Cerrado→Enviado→...
    │   ├── remito.py
    │   └── documentacion.py
    │
    ├── gps/                            ← PATRÓN ADAPTER (GoF)
    │   ├── interface.py                ← IGPSTracker (ABC) + UbicacionBolsin (DTO)
    │   ├── exceptions.py               ← GPSTrackerError
    │   ├── adapter_xtr4500l.py         ← adapta getBolsinLocation()
    │   ├── adapter_navtrack.py         ← adapta retrieveTrackingData()
    │   ├── adapter_geopulse.py         ← adapta fetchCargoPositions()
    │   └── factory.py                  ← get_gps_adapter(modelo) → IGPSTracker
    │
    ├── services/
    │   └── gestor_seguimiento.py       ← lógica de negocio CU 36 (TODO)
    │
    ├── views/
    │   ├── auth_views.py               ← login / logout
    │   └── seguimiento_views.py        ← CU 36 (TODO — pendiente diseño)
    │
    ├── templates/
    │   ├── base.html                   ← layout global (Tailwind CSS)
    │   ├── login.html
    │   ├── dashboard.html
    │   └── seguimiento/
    │       └── index.html              ← mapa + lista (TODO)
    │
    ├── static/js/
    │   └── mapa.js                     ← Google Maps JS (TODO)
    │
    ├── migrations/
    └── tests/
        ├── test_adapters.py            ← tests del patrón Adapter
        └── test_gestor.py
```

---

## Patrón Adapter — cómo está organizado

```
IGPSTracker (interface.py)
│   └── obtener_ubicacion(nro_bolsin, cm_codigo) → UbicacionBolsin
│
├── AdapterXTR4500L      llama a getBolsinLocation()     → JSON
├── AdapterNavTrackQX7A  llama a retrieveTrackingData()  → CSV string
└── AdapterGeoPulseMTR900 llama a fetchCargoPositions()  → Matriz

factory.py → get_gps_adapter("XTR4500L") devuelve el adapter correcto
```

Los adapters aún no están implementados — se implementan cuando se suba el diseño (diagrama de clases y secuencia de la Entrega 2).

---

## Comandos útiles

```bash
# Migraciones
python manage.py makemigrations
python manage.py migrate

# Tests
python manage.py test bolsines.tests

# Admin Django
python manage.py createsuperuser
# → http://localhost:8000/admin

# Seed de datos de prueba
python manage.py seed_db

# Shell interactivo
python manage.py shell
```

---

## Integrantes — Grupo 5

| Nombre | Legajo | Email |
|---|---|---|
| (completar) | | |
| (completar) | | |
| (completar) | | |
| (completar) | | |
