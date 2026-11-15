# 📦 CONTEXT.md — PPAI 2026 · Grupo 5 · Sistema Bolsines
> **Archivo de contexto compartido para IAs del equipo.**
> Leer este archivo antes de generar cualquier código, diseño o documentación.

---

## 1. Identificación del Proyecto

| Campo | Valor |
|---|---|
| **Materia** | Diseño de Sistemas I (DSI) — PPAI |
| **Universidad** | UTN — Facultad Regional |
| **Año** | 2026 |
| **Grupo** | 5 (grupo **impar**) |
| **Entrega actual** | **Entrega 2 — Diseño e Implementación** |
| **Sistema** | Sistema Bolsines (gestión de bolsines documentales entre Comisiones Médicas) |

---

## 2. Caso de Uso Asignado

> ⚠️ El Grupo 5 es **impar** → le corresponde el **CU 36**.

### CU 36 — Consultar seguimiento de bolsines

**Actor principal**: Encargado de Bolsines (EB)
**Actores secundarios**: GPS Tracker (3 modelos), Servidor Google Maps

#### Flujo Principal
1. EB selecciona "Consultar ubicación de bolsines".
2. Sistema muestra la Comisión Médica (CM) del usuario logueado.
3. Sistema busca bolsines en estado **"Enviado"** cuya CM origen coincida con la del usuario.
4. Sistema solicita al GPS Tracker los datos de localización de cada bolsín enviado.
5. Sistema recibe datos (latitud, longitud, fecha/hora última actualización).
6. Sistema muestra los bolsines sobre un mapa (Google Maps) con filtro por nro. precinto o CM destino.
7. EB selecciona un bolsín.
8. Sistema consulta si enviar email al Gerente de CM destino con la ubicación.
9. EB confirma → Sistema ejecuta CU 30 (Notificar ubicación de bolsín).

#### Flujos Alternativos
| Código | Situación |
|---|---|
| A1 | No hay bolsines en estado "Enviado" para la CM del usuario |
| A2 | No se encuentra bolsín por nro. precinto o CM destino (filtro vacío) |
| A3 | GPS Tracker no puede informar la ubicación (error de servicio externo) |
| A4 | EB cancela la operación en cualquier punto |
| A5 | EB decide no enviar el email de notificación al GCM |

---

## 3. Patrón de Diseño — Adapter (GoF/Gamma)

### Problema que resuelve
Existen **3 modelos distintos de dispositivos GPS Tracker** con interfaces incompatibles. El sistema necesita una interfaz uniforme para obtener la ubicación de un bolsín sin importar qué modelo físico está usando esa CM.

### Tres modelos GPS a adaptar

| Modelo | Método externo | Parámetros | Respuesta |
|---|---|---|---|
| **XTR-4500L** | `getBolsinLocation()` | `api_key`, `nro_bolsin: int`, `codigo_cm_origen: str` | JSON `{nro_bolsin, latitud, longitud, fecha_hora}` |
| **NavTrack QX-7A** | `retrieveTrackingData()` | `api_key`, `nro_bolsin: int`, `codigo_cm_destino: str` | String CSV: `"nro_bolsin,lat,long,fecha_hora"` |
| **GeoPulse MTR-900** | `fetchCargoPositions()` | `api_key`, `nro_bolsin: int` _(sin cm_codigo)_ | Matriz: `[[nro_bolsin, lat, long, fecha_hora]]` |

### Estructura del patrón (en el código)
```
bolsines/gps/
├── interface.py         → IGPSTracker (ABC) + UbicacionBolsin (DTO)
├── exceptions.py        → GPSTrackerError
├── adapter_xtr4500l.py  → AdapterXTR4500L    (TODO: implementar)
├── adapter_navtrack.py  → AdapterNavTrackQX7A (TODO: implementar)
├── adapter_geopulse.py  → AdapterGeoPulseMTR900 (TODO: implementar)
└── factory.py           → get_gps_adapter(modelo) → IGPSTracker
```

> ⚠️ Los adapters están en estado **stub** (NotImplementedError).
> Se implementan cuando se suba el diseño (diagrama de clases y secuencia de la Entrega 2).

---

## 4. Stack Tecnológico

> **Decisión de arquitectura: Django monolítico.**
>
> Razón principal: menor complejidad operacional en la defensa oral.
> Con Django solo se necesitan 2 terminales (GPS server + Django).
> FastAPI + React requeriría 3 (GPS + API + npm), con riesgo de CORS, JWT y
> dependencias de Node en la defensa. ORM, auth, admin y migraciones vienen
> incluidos en Django — no hay valor académico en construirlos desde cero.
> El patrón Adapter se evalúa igual independientemente del framework web.

| Capa | Tecnología |
|---|---|
| **Framework** | Python + **Django 5.x** (monolítico) |
| **Frontend** | Django Templates + **Tailwind CSS** (CDN) + vanilla JS |
| **Base de datos** | SQLite (desarrollo) |
| **ORM + migraciones** | Django ORM + `manage.py migrate` |
| **Mapas** | Google Maps JavaScript API (integrado en templates) |
| **API externa GPS** | Repositorio de la cátedra (levantar localmente en puerto 8001) |
| **Email** | Microsoft Graph API / Outlook (notificaciones CU 30) |
| **Control de versiones** | Git + GitHub |

---

## 5. Modelo de Dominio — Clases y Estados

### Bolsín
```
Estados válidos:
  Creado → Cerrado → Enviado → RecibidoEnCMDestino
  Creado | Cerrado → DeBaja
```

### Remito
```
Estados válidos:
  Generado → EnBolsinSaliente → EnBolsinEnviado →
  RecibidoYAceptado | RecibidoYAceptadoParcial | Cancelado
```

### Documentación
```
Estados válidos:
  Registrada → EnRemito → EnBolsinSaliente → EnBolsinEnviado →
  RecibidaYAceptada | RecibidaYRechazada | NoRecibida | ParaRedirigir | DeBaja
```

### Regla de trazabilidad
Todo cambio de estado registra: empleado responsable + fecha/hora exacta (`CambioEstado*`).

---

## 6. Diseño UX/UI — Lineamientos

### Principios
- Diseño **web**, orientado a escritorio (pantallas de oficina estatal).
- **Tailwind CSS** para estilos (ya configurado en `base.html`).
- Paleta: azul institucional (`blue-700/800`), blanco, grises neutros.

### Patrones de GUI a implementar (obligatorio para Entrega 2)
| Patrón | Dónde aplicarlo |
|---|---|
| **Master-Detail** | Lista de bolsines (izq.) + detalle del bolsín (der.) |
| **Filtro/Búsqueda** | Filtrar bolsines por nro. precinto o CM destino |
| **Mapa integrado** | Google Maps con pins por bolsín en estado "Enviado" |
| **Modal de confirmación** | Confirmar envío de email al GCM (CU 30) |
| **Estado visual (badges)** | Color por estado del bolsín |
| **Empty State** | Cuando no hay bolsines enviados (flujo A1) |
| **Error State** | Cuando el GPS Tracker no responde (flujo A3) |

### Pantallas a implementar
1. **Login** (`/login/`) — ✅ template creado
2. **Dashboard** (`/dashboard/`) — ✅ template creado
3. **Seguimiento CU 36** (`/seguimiento/`) — 🔲 placeholder, pendiente diseño
4. Error GPS (flujo A3) — 🔲 pendiente
5. Empty state sin bolsines (flujo A1) — 🔲 pendiente

---

## 7. API de GPS Tracker — Servidor Local (Cátedra)

### ⚠️ Requisito crítico de ejecución
El servidor GPS de la cátedra **DEBE estar corriendo** en `http://localhost:8001`
antes de levantar el sistema. Los adapters se conectan a ese servidor.

### Cómo levantar (completar con URL real de la cátedra)
```bash
# Terminal 1: Servidor GPS de la cátedra
git clone <URL_REPO_GPS_CATEDRA>   # TODO: completar con URL real
cd <repo-gps>
pip install -r requirements.txt
python server.py
# Escucha en http://localhost:8001
```

### Endpoints que el servidor expone (según ERS)
```
GET /xtr4500l/getBolsinLocation
    ?api_key=...&nro_bolsin=...&codigo_cm_origen=...
    → JSON: {nro_bolsin, latitud, longitud, fecha_hora}

GET /navtrack/retrieveTrackingData
    ?api_key=...&nro_bolsin=...&codigo_cm_destino=...
    → CSV: "nro_bolsin,lat,long,fecha_hora"

GET /geopulse/fetchCargoPositions
    ?api_key=...&nro_bolsin=...
    → Matriz: [[nro_bolsin, lat, long, fecha_hora]]
```

### Variables de entorno (`.env`)
```env
GPS_API_BASE_URL=http://localhost:8001
GPS_API_KEY=test_api_key
GPS_MODEL_DEFAULT=XTR4500L
GOOGLE_MAPS_API_KEY=tu_clave_aqui
SECRET_KEY=cambiar-en-produccion
DEBUG=True
```

---

## 8. Estructura del Proyecto

```
PPAI-DSI/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── CONTEXT.md                             ← este archivo
│
├── bolsines_system/                       ← configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── bolsines/                              ← app principal
    ├── admin.py                           ← todos los modelos en /admin
    ├── urls.py
    │
    ├── models/
    │   ├── comision_medica.py             ← ComisionMedica (CMJ | CMC)
    │   ├── empleado.py                    ← Empleado (vinculado a User Django)
    │   ├── bolsin.py                      ← Bolsin + CambioEstadoBolsin
    │   ├── remito.py                      ← Remito + CambioEstadoRemito
    │   └── documentacion.py              ← Documentacion + TipoDocumento + CambioEstado
    │
    ├── gps/                               ← PATRÓN ADAPTER (GoF)
    │   ├── interface.py                   ← IGPSTracker (ABC) + UbicacionBolsin (DTO)
    │   ├── exceptions.py                  ← GPSTrackerError
    │   ├── adapter_xtr4500l.py            ← stub — TODO implementar
    │   ├── adapter_navtrack.py            ← stub — TODO implementar
    │   ├── adapter_geopulse.py            ← stub — TODO implementar
    │   └── factory.py                     ← get_gps_adapter(modelo)
    │
    ├── services/
    │   └── gestor_seguimiento.py          ← GestorConsultaSeguimiento — TODO implementar
    │
    ├── views/
    │   ├── auth_views.py                  ← login / logout / dashboard ✅
    │   └── seguimiento_views.py           ← CU 36 — TODO implementar
    │
    ├── templates/
    │   ├── base.html                      ← layout global (Tailwind) ✅
    │   ├── login.html                     ← ✅
    │   ├── dashboard.html                 ← ✅
    │   └── seguimiento/
    │       └── index.html                 ← placeholder — TODO implementar
    │
    ├── management/commands/
    │   └── seed_db.py                     ← python manage.py seed_db
    │
    ├── migrations/
    └── tests/
        └── test_adapters.py               ← tests del patrón Adapter
```

---

## 9. Reglas de Negocio Críticas

1. Solo se muestran bolsines en estado **"Enviado"** cuya **CM origen = CM del usuario logueado**.
2. El Adapter GPS debe devolver siempre `UbicacionBolsin` sin importar el modelo físico.
3. Si el GPS Tracker no responde → flujo alternativo A3 (error visible en UI, nunca crash).
4. El email de notificación (CU 30) se envía **solo con confirmación explícita** del EB.
5. Todo cambio de estado **registra el empleado responsable y la fecha/hora** (trazabilidad).
6. Un bolsín pertenece siempre a **una única CM destino**.
7. El filtro por precinto / CM destino es **opcional**; sin filtro se muestran todos los enviados.

---

## 10. Correcciones de la Entrega 1 a Corregir

| Área | Corrección pendiente |
|---|---|
| Vista estática | Agregar asociación `Bolsín ↔ ComisionMedica` y `Remito → ComisionMedica` |
| Vista estática | Agregar multiplicidades faltantes |
| Vista estática | Ajustar `IGPSTracker`: solo los métodos usados en la dinámica |
| Vista dinámica | `obtenerNombreComisionMedica()` debe llamarse desde el Gestor |
| Vista dinámica | Un `CambioDeEstado` NO conoce otro `CambioDeEstado` |
| Vista dinámica | El Bolsín puede consultar directamente su CM origen |
| Vista dinámica | Completar las secciones incompletas (3.4) |
| Vista dinámica | Justificar para qué se obtiene fecha y hora (3.5) |
| Vista dinámica | Corregir notación incorrecta (3.6) |
| Máquina de estados | `Generado→EnBolsinSaliente`: agregar CU Modificar Bolsín |
| Máquina de estados | `EnBolsinSaliente→Generado`: agregar CU Eliminar Bolsín |

---

## 11. Convenciones de Código

- **Idioma**: español para nombres de dominio (`bolsin`, `remito`, `cm_origen`), inglés para infraestructura.
- **Python**: PEP 8, type hints obligatorios, docstrings en clases y métodos públicos.
- **Commits**: en español, formato `[tipo]: descripción` → ej: `[feat]: implementar adapter XTR-4500L`.
- **Variables de entorno**: nunca hardcodear API keys. Usar `.env` + `.env.example`.
- **Modelos Django**: siempre definir `Meta`, `__str__`, `verbose_name`.

---

## 12. Checklist Entrega 2

### Documento PDF (`PPAI2026_3K5_G5_E2_Diseño.pdf`)
- [ ] Carátula con datos del grupo
- [ ] Identificación del patrón Adapter + justificación del problema que resuelve
- [ ] Vista estática (diagrama de clases de diseño) con tipos, parámetros, visibilidad
- [ ] Vista dinámica (diagrama de secuencia de diseño)
- [ ] Descripción del framework y tecnologías (Django + Tailwind + SQLite)
- [ ] Capturas de pantalla del sistema funcionando
- [ ] MoodBoard UX (fotografía del afiche)

### Implementación (código ejecutable)
- [ ] Flujo principal del CU 36 funcionando
- [ ] Al menos 2 flujos alternativos (A1 y A3 recomendados)
- [ ] Los 3 adapters GPS implementados (hoy son stubs)
- [ ] Servidor GPS de la cátedra levantándose correctamente
- [ ] Persistencia a base de datos funcionando
- [ ] Interfaz web con patrones GUI (Master-Detail, mapa, filtros, modal)
- [ ] README con instrucciones de ejecución

---

## 13. Estado actual del código

| Componente | Estado |
|---|---|
| Modelos Django (Bolsin, Remito, Documentacion, etc.) | ✅ Implementados |
| Migraciones | ✅ Listas para aplicar |
| Admin Django | ✅ Todos los modelos registrados |
| GPS Interface (`IGPSTracker`, `UbicacionBolsin`) | ✅ Implementada |
| GPS Factory | ✅ Implementada |
| GPS Adapters (3 modelos) | 🔲 Stubs — pendiente diseño |
| GestorConsultaSeguimiento | 🔲 Stub — pendiente diseño |
| Vista CU 36 | 🔲 Placeholder — pendiente diseño |
| Template seguimiento | 🔲 Placeholder — pendiente diseño |
| Login / Dashboard / Base template | ✅ Implementados |
| Tests adapters | ✅ Escritos (prueban stubs y factory) |
| Seed DB | ✅ `python manage.py seed_db` |

---

## 14. Notas para la IA

- **Siempre leer este archivo** antes de generar código o documentación.
- El patrón central es **Adapter (GoF)** — no Strategy, no Factory, no Observer.
- Los adapters **solo traducen interfaces**, no tienen lógica de negocio.
- El **Gestor** coordina: obtiene bolsines de la DB, llama al adapter, retorna a la vista.
- El frontend (templates) **nunca llama directamente** a la API GPS — siempre pasa por el Gestor.
- Los diagramas deben ser consistentes entre sí: clases ↔ secuencia ↔ código.
- Respetar los estados de Bolsín, Remito y Documentación del Modelo de Dominio.
- Mantener trazabilidad: todo cambio de estado guarda empleado + fecha/hora.
- El servidor GPS de la cátedra es **externo y obligatorio** — documentar su arranque claramente.
