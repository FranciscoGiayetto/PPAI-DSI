# Sistema Bolsines — PPAI 2026
### UTN · Diseño de Sistemas I · Grupo 5

---

## ¿Por qué Django monolítico?

### Contexto

- Equipo chico con fecha de entrega fija.
- Lo que se evalúa es el **patrón Adapter**, la **consistencia entre diagramas y código** y que el sistema **funcione** en la defensa.
- El servidor GPS lo provee la cátedra (Java/Spring Boot); nuestro sistema solo lo consume por HTTP.

**Principio guía:** la complejidad técnica solo se justifica si aporta a lo que se evalúa.

### Criterios y cómo los cubre Django

| Criterio | Django |
|---|---|
| Poco tiempo de configuración | Login, sesiones, base de datos, migraciones y panel de administración ya incluidos |
| Arranque simple en la defensa | Un solo comando (`python manage.py runserver`) levanta la app y el servidor GPS |
| Sin frontend separado | Las páginas se generan en el servidor: sin CORS, sin build, sin `npm install` |
| Mapa de seguimiento | Google Maps se integra con JavaScript en la plantilla |
| Patrón Adapter | Se implementa en clases Python puras (`bolsines/gps/`), independientes del framework |

### Costo aceptado y cómo lo mitigamos

Los modelos de Django combinan la clase del dominio con su persistencia en la base de datos.
Esto puede alejar el código del diagrama de clases si la lógica termina escrita como consultas sueltas en las vistas.

Para evitarlo:
- Los métodos que aparecen en los diagramas (por ejemplo, los de `Bolsin` o `ComisionMedica`) se escriben como métodos de los modelos.
- La lógica del caso de uso vive en el gestor (`services/gestor_seguimiento.py`), siguiendo el diagrama de secuencia.
- Las vistas solo reciben la interacción del usuario y delegan en el gestor.

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

### Ver la interfaz rápido (Windows, sin el GPS)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_db
python manage.py runserver --sin-gps
```

Entrar a http://localhost:8000 con **legajo `40211`** y **contraseña `bolsines2026`** (Encargada de Bolsines de CMJ Córdoba).

| URL | Qué muestra |
|---|---|
| `/login/` | Login con el panel de marca y la bolsa animada |
| `/seguimiento/` | CU 36: mapa, lista, detalle, diálogo (el bolsín 1041 muestra el flujo A3) |
| `/seguimiento/?demo=vacio` | Flujo A1: no hay bolsines en viaje |
| `/seguimiento/?demo=cargando` | Estado "Buscando tus bolsines…" |
| `/dashboard/` | Inicio |

Las ubicaciones son **simuladas** hasta que estén el Gestor y los Adapters. Sin `GOOGLE_MAPS_API_KEY` se ve un mapa de reemplazo.
Las decisiones de la interfaz están en [`docs/decisiones-esteticas.md`](docs/decisiones-esteticas.md).

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
DJANGO_DEBUG=True
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

Sigue el diagrama de clases de la Entrega 2 (`ConsignasyDiagramas/PPAI2026_3K2_G5_E2_Adapter_CU36*.drawio`):

```
GestorSeguimientoBolsines (services/gestor_seguimiento.py)   ← control
└── InterfazGPS (gps/interfaz_gps.py)                        ← Cliente (elige el adaptador según GPS_MODEL_DEFAULT)
    └── IAdaptadorGPSTracker (gps/adaptadores.py)            ← Objetivo
        ├── AdaptadorGPSXTR4500L      → ServicioGPSTrackerXTR4500L      getBolsinLocation()     (JSON)
        ├── AdaptadorGPSNavTrackQX7A  → ServicioGPSTrackerNavTrackQX7A  retrieveTrackingData()  (CSV)
        └── AdaptadorGPSGeoPulseMTR900→ ServicioGPSTrackerGeoPulseMTR900 fetchCargoPositions()  (matriz)
```

Servicios en `gps/servicios.py`. Probar otro modelo: `GPS_MODEL_DEFAULT=NAVTRACKQX7A` (o `GEOPULSEMTR900`) en `.env`.
Con los datos del servidor GPS de la cátedra, el XTR-4500L valida la CM origen (en el mock solo el 101 sale de CM-CBA-01, se ve 1 bolsín); NavTrack y GeoPulse muestran 101 y 102. El bolsín 150 no existe en el GPS (flujo A3).

Tests: `python manage.py test bolsines`. Documento de la entrega: `docs/entrega2/`.

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
