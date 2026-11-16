# Bolsines

Sistema de seguimiento de bolsines entre Comisiones Médicas. Este design system define cómo se ve y cómo habla la interfaz del **CU 36 · Consultar seguimiento de bolsines** (PPAI · Diseño de Sistemas de Información · UTN FRC · 2026 · Grupo 5) y de todo lo que se sume después.

> **Sabé dónde está cada bolsín.**

## Principios

1. **El mapa es el protagonista.** El seguimiento es geográfico: el mapa ocupa toda la pantalla y todo lo demás flota encima.
2. **Vidrio sobre el mapa.** Barra, lista y detalle son paneles de vidrio (`superficie-vidrio` + desenfoque). El vidrio solo se usa donde hay algo detrás que mostrar.
3. **El amarillo es el sello.** `sello` (amarillo) es la firma de la marca: la cinta de estado, los camioncitos, el botón principal. Siempre como **relleno**, nunca como texto ni línea fina. Lo funcional (sección activa, links, ruta, foco) usa `acento`, que es amarillo en oscuro y azul en claro.
4. **Oscuro por defecto.** Por compromiso de software verde: menos energía en pantallas OLED y menos brillo en oficinas. El claro existe y es cálido (crema intenso, no blanco).
5. **Hablamos como personas.** "¿Le avisamos dónde está?", "El GPS no contesta". Nada de "Operación exitosa" ni códigos de error.

## Color

Dos temas: `oscuro` (por defecto) y `claro`. Se activan con `data-theme` en `<html>`.

| Rol | Oscuro | Claro | Para qué |
|---|---|---|---|
| `fondo` | #242424 gris carbón | #F3E4C6 crema intenso | Página y mapa |
| `tinta` | #FFF7EB crema | #16324F azul noche | Texto principal |
| `acento` | #FDBD4F amarillo | #0C5EBC azul | Activo, links, ruta, selección, foco |
| `sello` | #FDBD4F amarillo | #FDBD4F amarillo | Cinta, camioncitos, botón principal |
| `marca` | #FDBD4F amarillo | #0C5EBC azul | Panel del login |
| `info` | #A8DADC celeste | #0C5EBC azul | CM del usuario |
| `error` | #FF7A8A | #B5233A | GPS sin señal |
| `ok` | #5FD39A | #17694A | Correo enviado |

**Paleta de marca (fija):** amarillo #FDBD4F · azul #0C5EBC · azul noche #16324F · crema #FFF7EB · gris #242424 · celeste #A8DADC · rojo #FF4F63 (solo como relleno de error).

**Reglas**
- Todo texto cumple 4,5:1 en los dos temas (verificado). `sobre-marca` (logo azul sobre amarillo, 3,8:1) es solo para el logo y textos de 24px o más; para texto chico sobre `marca` va `sobre-marca-texto`.
- Nunca amarillo sobre crema: no se ve. En claro, el amarillo siempre lleva texto `azul-noche` encima o un borde azul noche alrededor.
- Estados que hay que distinguir (en viaje / sin señal) cambian también de forma e ícono, no solo de color.

## Tipografía

| Familia | Uso |
|---|---|
| **High Cruiser** (display de marca) | Títulos, números de bolsín, contadores, la cinta. *Pendiente el archivo de la fuente: mientras tanto se usa **Bebas Neue** como reemplazo.* |
| **Roboto** | Todo el texto de interfaz. |
| **Roboto Mono** | Precintos y coordenadas (datos que se leen carácter por carácter). |

Los números grandes son parte de la identidad: el "N.º 1048" en `display-l` es lo primero que se lee en el detalle.

## Forma y espacio

- Radios: píldora (`radius-pill`) para todo lo que se toca —barra, botones, inputs, chips—; `radius-xl` (28px) para paneles; `radius-m` para marcadores.
- Espaciado en pasos de 4px (`space-1` … `space-12`). Paneles con `space-6` de padding y de margen a la pantalla.
- Áreas táctiles de 44px como mínimo (los botones miden 48–52px).
- **El ángulo de la bolsa**: el costado inclinado de la bolsa (≈16°) es el ángulo de la marca. Lo usa el borde del panel del login y la cinta (−2,5° es su versión sutil).

## Logo

Ver `assets/Logos`. La B del logo son las **manijas** de la bolsa: por eso el isotipo va **de pie**. Girada 90° hacia el otro lado es el **camioncito**, y ese giro solo se usa para decir "en viaje".

## Iconografía

Set propio en `assets/Iconos` y en el componente `Icono`. Los de marca (camioncito, bolsa, bolsa-alerta) salen del mismo dibujo que el logo; los de interfaz son de trazo 2px. Sin emojis.

## Movimiento

| Momento | Qué pasa | Duración |
|---|---|---|
| Entrada del login | El color de `marca` cubre la pantalla y su borde barre hasta el ángulo de la bolsa | 0,9 s, `cubic-bezier(.7,0,.2,1)` |
| Bolsa en loop | De pie → se da vuelta → camioncito → sale por la derecha → entra por la izquierda → vuelve a ser bolsa | 5,4 s por vuelta |
| Cambio de tema | Círculo que se expande desde la perilla (View Transitions API) | 0,5 s |
| Selección en el mapa | El camioncito crece y aparece su ruta | 0,2 s |
| Avisos | Entran desde arriba, se van solos | 5 s visibles |

Con `prefers-reduced-motion: reduce` todo queda quieto (la bolsa de pie, sin loop).

## Voz y tono

| En vez de | Decimos |
|---|---|
| Bolsines en estado Enviado | En viaje |
| No se encontraron resultados | Ese bolsín no está acá |
| Error de conexión con el dispositivo | El GPS no contesta |
| ¿Confirma el envío de la notificación? | ¿Le avisamos dónde está? |
| Notificación enviada exitosamente | Listo, la Gerencia de CMC CABA ya tiene la ubicación |

Voseo, frases cortas, siempre decir **qué pasó** y **qué puede hacer** la persona.

## Implementación (Django + Tailwind)

- Copiar `tokens.css` al proyecto y poner `data-theme="oscuro"` en `<html>` (el botón de tema lo cambia y lo guarda en `localStorage`).
- En `tailwind.config` mapear los colores a las variables: `colors: { fondo: 'var(--fondo)', tinta: 'var(--tinta)', acento: 'var(--acento)', sello: 'var(--sello)', … }`. Así `bg-fondo text-tinta` funciona en los dos temas sin duplicar clases.
- Los componentes de este sistema son la referencia visual: en los templates se replican con las clases de `bundle.css` o con utilidades de Tailwind que usen los mismos tokens.
- Google Maps: estilo de mapa con `mapa-agua`, `mapa-calle`, `mapa-limite` y `fondo`; marcadores con `AdvancedMarkerElement` usando el HTML de `Marcador`.
