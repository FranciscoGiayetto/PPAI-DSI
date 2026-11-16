# Decisiones estéticas y de implementación de la interfaz

Registro de lo que se hizo al aplicar el design system (`docs/design-system/`) a los templates,
y de las decisiones que se tomaron donde el design system no decía nada.
Fecha: 16/11/2026.

---

## 1. Qué se hizo

| Pieza | Archivo | Qué tiene |
|---|---|---|
| Tokens y componentes | `bolsines/static/css/tokens.css`, `componentes.css` | Copia **sin cambios** de `docs/design-system/`. Si cambian los tokens, se vuelven a copiar. |
| Layout de pantallas | `bolsines/static/css/app.css` | Solo dónde va cada cosa (paneles, login, hoja móvil). Ningún color hex: todo con `var(--token)`. |
| Layout global | `bolsines/templates/base.html` | Fuentes, Tailwind mapeado a las variables, script anti-parpadeo del tema, carga de CSS y JS. |
| Tema | `bolsines/static/js/tema.js` + `templates/parciales/interruptor.html` | Oscuro por defecto, se guarda en `localStorage` (`bolsines-tema`). |
| Barra de navegación | `templates/parciales/nav.html` | Vidrio flotante arriba con el **logotipo animado**; en móvil, tab bar abajo. |
| Login | `templates/login.html` | Panel de marca inclinado con la **bolsa animada**, formulario con legajo. |
| Seguimiento CU 36 | `templates/seguimiento/index.html` + `static/js/seguimiento.js` | Mapa, master-detail, filtros, estados A1/A2/A3/cargando, diálogo, aviso, hoja móvil. |
| Inicio | `templates/dashboard.html` | Pantalla simple de accesos (no estaba especificada en `pantallas.md`). |
| Íconos y logos | `templates/iconos/*.svg`, `templates/logos/*.svg` | Los SVG de la carpeta de diseño con `#16324F` cambiado a `currentColor`, para usarlos con `{% include %}` y que tomen el color del texto. |

## 2. Decisiones que tomamos (el design system no las cubría)

### Tailwind
- Se usa la versión fija del CDN (`cdn.tailwindcss.com/3.4.16`) para que no cambie sola.
- Además de los colores del README, se mapearon `tinta-debil`, `sobre-marca`, `sobre-marca-texto` y `superficie-suave`, que también se usan.
- Tailwind se usa solo para espaciado y utilidades chicas (`mt-6`, `flex`, `text-tinta-tenue`). Los componentes son siempre las clases `bol-*`, así el marcado queda igual que en `componentes.html`.

### Tema
- Al cambiar de tema hay un **círculo que se expande desde la perilla** (View Transitions API, 500 ms), como recomienda `InterruptorTema.md`. Si el navegador no lo soporta o la persona pidió menos movimiento, el cambio es directo.
- El tema se lee en un `<script>` inline en el `<head>`, antes de pintar, así no hay parpadeo.

### Login
- **Barrido de entrada:** el panel arranca más ancho que la pantalla y se cierra hasta el corte inclinado, manteniendo el mismo ángulo durante toda la animación (los keyframes mueven los dos puntos del borde juntos).
- En móvil el corte inclinado queda abajo del panel, como pide la especificación.
- Se ingresa con **legajo**: la vista busca el `Empleado` por legajo y autentica a su usuario de Django. Si no hay un empleado con ese legajo, prueba el texto como nombre de usuario, así el superusuario del admin también puede entrar.

### Barra de navegación
- Se agregó un botón **Salir** (ícono `salir`) al final: no estaba en la especificación, pero sin él no hay forma de cerrar la sesión.
- "Bolsines" y "Remitos" quedan como enlaces sin destino (`#`) hasta que existan esas pantallas.
- En móvil, arriba quedan solo el logotipo y el interruptor; la navegación pasa a la tab bar de abajo.

### Seguimiento
- **Datos de demostración.** El Gestor y los Adapters GPS todavía son stubs (esperan el diseño de la Entrega 2). Mientras tanto, `views/seguimiento_views.py` lee de la base los bolsines **Enviados** de la CM del usuario y les **simula** la ubicación (a mitad de camino entre las coordenadas aproximadas de cada CM). Cuando el Gestor esté listo, solo cambia esa función: el template y el JS esperan los mismos datos.
- **Modos para mostrar los estados en la defensa:** `?demo=vacio` (A1, sin bolsines) y `?demo=cargando`. El A3 se ve siempre con el bolsín **1041**, cuyo GPS "no contesta". El A2 aparece buscando un precinto que no existe.
- **Mapa sin clave de Google.** Si `GOOGLE_MAPS_API_KEY` está vacía, se dibuja un **mapa de reemplazo**: el fondo `bol-demo-mapa` del design system, con los puntos ubicados por una proyección simple de latitud y longitud. Así la pantalla se puede mostrar sin clave. Con clave se usa Google Maps con `AdvancedMarkerElement` (necesita un Map ID: `GOOGLE_MAPS_MAP_ID`, por defecto `DEMO_MAP_ID`) y el esquema de color oscuro o claro según el tema.
  - Con un Map ID no se pueden aplicar los estilos `mapa-*` a mano; se usa `colorScheme` de Google. Para los colores exactos hay que crear un estilo en la consola de Google Cloud y usar ese Map ID.
  - Google Maps no cambia de esquema en caliente, así que al cambiar de tema el mapa se vuelve a crear.
- **Bolsín sin señal (A3):** no aparece en el mapa porque no tiene coordenadas, y el botón "Avisarle al gerente" queda desactivado, porque no hay ubicación para mandar. "Reintentar" vuelve a consultar; en la demo sigue sin contestar y lo avisa con un `bol-aviso` rojo.
- **Diálogo:** "Enviar correo" todavía **no manda nada**: muestra el aviso de éxito. Falta conectarlo al CU 30 (hay un `TODO` en `seguimiento.js`). Se le agregó foco atrapado y cierre con Esc o clic afuera (`Dialogo.md`).
- **Selección inicial:** en escritorio se selecciona solo el primer bolsín con señal, para que el panel derecho no arranque vacío. En móvil no, para no tapar el mapa.
- **Panel derecho:** se le agregó un botón para cerrarlo (×).
- **Hoja inferior móvil:** se arrastra desde el agarre (o se toca para abrirla o cerrarla). Al tocar un bolsín, la hoja muestra el detalle; si se arrastra hacia abajo, vuelve a la lista.
- Los paneles arrancan **debajo de la barra de navegación** (top 96 px) y no a alto completo: con la barra de navegación entera (CM, tema, avatar) no entran los tres en un ancho de 1440 px.

### Favicon y logo
- **Favicon** (`static/img/favicon.svg`): el isotipo en `--azul` sobre un cuadrado redondeado `--amarillo`. Es un archivo estático, así que lleva los hex de la marca (no puede leer variables CSS).
- **Logo animado:** durante la animación la B salta por encima del `viewBox` y el script la recortaba (`overflow:hidden`). En `app.css` se pisa con `overflow: visible` para que no se corte la parte de arriba. Conviene corregirlo también en `docs/design-system/animaciones/logotipo-animado.js`.

### Zoom del mapa de reemplazo
- El fondo decorativo se escala junto con los puntos al hacer zoom. Es solo una aproximación visual: el mapa real llega con Google Maps.

## 3. Archivos de Django que se crearon (faltaban en el repo)

`CONTEXT.md` los daba por hechos, pero no estaban: `bolsines/urls.py`, `bolsines/admin.py`, `bolsines/models/__init__.py`, `bolsines/views/auth_views.py`, `bolsines/views/seguimiento_views.py`, `bolsines/management/commands/seed_db.py` y la migración inicial.
**No** se crearon `gps/` ni `services/gestor_seguimiento.py`: esos salen del diseño de la Entrega 2.

Otros cambios:
- `requirements.txt`: `Pillow==10.3.0` → `Pillow>=11.3.0`, porque la 10.3 no instala en Python 3.13/3.14.
- `settings.py`: nueva variable `GOOGLE_MAPS_MAP_ID`.

## 4. Pendientes

- [ ] Conectar `seguimiento_views.py` al `GestorConsultaSeguimiento` cuando esté diseñado.
- [ ] Conectar "Enviar correo" al CU 30 (POST al servidor).
- [ ] Link "Ver historial de estados" (hoy no hace nada).
- [ ] Estilo de mapa propio en Google Cloud con los colores `mapa-*`.
- [ ] Pantallas Bolsines y Remitos (hoy son enlaces vacíos en la barra de navegación).
