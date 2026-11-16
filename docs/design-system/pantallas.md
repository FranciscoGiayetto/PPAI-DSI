# Pantallas

Ver el canvas "Bolsines — Interfaces CU 36" para el diseño interactivo. Acá, lo que tiene que tener cada template.

## Login (`login.html`)

**Escritorio**
- Fondo `--fondo`. Panel de marca a la izquierda: `background: var(--marca)`, recortado con
  `clip-path: polygon(0 0, 40% 0, 58% 100%, 0 100%)` (el borde inclinado es el ángulo del costado de la bolsa, ~16°).
- Dentro del panel, centrada en el 49 % izquierdo: `<div data-bolsa-animada data-color="var(--sobre-marca)">` (bolsa en loop) y debajo el slogan "Sabé dónde está cada bolsín" en `.t-display-m` color `--sobre-marca`.
- Entrada: el panel arranca cubriendo toda la pantalla y barre hasta su lugar (0,9 s, `cubic-bezier(.7,0,.2,1)`, keyframes de `clip-path`).
- Derecha (≈520 px): logotipo SVG (190 px, `--tinta`), rótulo "COMISIONES MÉDICAS" (`.t-etiqueta`, `--tinta-tenue`), título "Hola de nuevo" (`.t-display-xl`), bajada "Ingresá con tu legajo para seguir tus bolsines.", campos Legajo y Contraseña (`bol-campo`, con botón "Mostrar contraseña"), link "¿La olvidaste?", botón `bol-boton bol-boton--marca bol-boton--ancho` "Ingresar →", nota "¿No podés entrar? Escribile al Parametrizador del Sistema de tu CM."
- Arriba a la derecha: `bol-interruptor` (tema).
- Errores de login con `bol-campo__error` ("Legajo o contraseña incorrectos").

**Móvil** (< 768 px): el panel de marca ocupa la parte de arriba (≈40 % del alto) con el corte inclinado abajo; la bolsa más chica; el formulario debajo, a todo el ancho.

## Seguimiento CU 36 (`seguimiento/index.html`)

**Escritorio**
- **Mapa a pantalla completa** detrás de todo (Google Maps con estilo `mapa-*`; en oscuro fondo `--gris`).
- **Barra de navegación** de vidrio flotante arriba al centro (`bol-vidrio bol-nav bol-nav--escritorio`): logotipo animado (`data-logo-animado`), Inicio · Bolsines · **Seguimiento** (activo, píldora `--acento` con ícono camioncito) · Remitos, separador, CM del usuario (`--info`), interruptor de tema, avatar.
- **Panel izquierdo** de vidrio (360 px, alto completo, `--radius-xl`):
  - "En viaje" (`.t-display-m`) + contador "06" en `--acento`; "Bolsines enviados desde CMJ Córdoba · actualizado 10:56".
  - Buscador por precinto (`bol-campo` con ícono buscar).
  - Chips de CM destino (`bol-chip`, "Todas" + cada destino).
  - Lista de `bol-item` (camioncito, número, "→ destino", precinto, "hace N min"). Sin señal: `is-error` con `bolsa-alerta`.
  - Sin resultados (A2): bolsa grande, "Ese bolsín no está acá", "Limpiar filtros".
- **Panel derecho** de vidrio (390 px) con el bolsín seleccionado:
  - `bol-cinta` arriba ("BOLSINES · EN VIAJE" o roja "SIN SEÑAL").
  - "Estado: Enviado", "N.º 1048" (`.t-display-l`), "Precinto PR-26-004812" (`.t-dato`).
  - `bol-trayecto` Córdoba → destino.
  - Latitud / Longitud (`.t-dato`), "Última señal 16/11 10:52 · hace 4 min".
  - Peso, Remitos, Salió (`.t-display-s`), "GPS Tracker XTR-4500L".
  - A3 (sin señal): `bol-alerta` "El GPS no contesta" + "Reintentar".
  - Botón `bol-boton--primario bol-boton--ancho` "Avisarle al gerente de destino" → abre el diálogo. Link "Ver historial de estados".
- **Mapa**: origen = punto `--azul` con aro crema y halo; cada bolsín Enviado = `bol-marcador` (camioncito); el seleccionado `is-sel` con etiqueta "N.º 1048 · hace 4 min" y ruta (tramo hecho sólido `--acento`, resto punteado). CM destino = aro `--info` + nombre.
- **Zoom** (−, centrar, +) en una píldora de vidrio abajo al centro.
- **Diálogo** (`bol-velo` + `bol-dialogo`): "¿Le avisamos dónde está?", "Mandamos un correo a la Gerencia de {CM} con la ubicación del bolsín N.º {nro}.", resumen (última señal, coordenadas), "No, gracias" (A5) / "Enviar correo" (CU 31).
- **Aviso** de éxito (`bol-aviso`) arriba al centro: "Listo, la Gerencia de {CM} ya tiene la ubicación".
- **Sin bolsines enviados (A1)**: mapa vacío y en el panel la bolsa de pie + "No hay bolsines en viaje" + "Cuando envíes uno, lo vas a ver acá".
- **Cargando** (mientras el Gestor consulta al GPS): bolsa animada chica en el panel + "Buscando tus bolsines…".

**Móvil**
- Mapa a pantalla completa; **tab bar de vidrio abajo** (`bol-nav--movil`).
- La lista es una **hoja inferior** que se arrastra (colapsada: "En viaje 06" + buscador; expandida: lista completa).
- Al tocar un bolsín, la hoja muestra el detalle (cinta, número, trayecto, datos, botón "Avisarle al gerente").
- El diálogo ocupa el ancho con margen de 16 px.
