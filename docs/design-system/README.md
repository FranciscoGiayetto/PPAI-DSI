# Design system de Bolsines

Todo lo visual del sistema sale de esta carpeta. **Leer esto antes de tocar templates, CSS o JS de interfaz.**

Fuente original (editable, en claude.ai): design system "Bolsines" y canvas "Bolsines — Interfaces CU 36" (pedirle acceso a Berni). Esta carpeta es la copia que usa el código.

## Qué hay acá

| Archivo | Qué es | Cómo se usa |
|---|---|---|
| `manual-de-marca.md` | Principios, color, tipografía, logo, íconos, movimiento, voz y tono | Leer primero |
| `tokens.css` | Variables CSS de los dos temas (`oscuro` por defecto, `claro`) + clases de texto `.t-*` | Copiar a `bolsines/static/css/` y cargar en `base.html` |
| `tokens.json` | La fuente de los tokens | Para la config de Tailwind |
| `componentes.css` | Estilos de todos los componentes (clases `bol-*`) | Copiar a `static/css/` y cargar después de `tokens.css` |
| `componentes.html` | **HTML de referencia de cada componente**, en los dos temas | Abrir en el navegador y copiar el marcado a los templates |
| `componentes/*.md` | Reglas de uso de cada componente | Consultar al implementar cada uno |
| `pantallas.md` | Especificación de cada pantalla (login y seguimiento, escritorio y móvil) | Guía para armar los templates |
| `logos/`, `iconos/` | SVG de una tinta | Inline en los templates con `fill/stroke="currentColor"` |
| `animaciones/` | `logotipo-animado.js`, `bolsa-animada.js` y `demo.html` | Copiar los `.js` a `static/js/` |

## Reglas para implementar

1. **Nunca un color hex en un template.** Siempre `var(--token)` o una clase de Tailwind mapeada a la variable.
2. **El tema** se controla con `data-theme="oscuro|claro"` en `<html>`. Oscuro por defecto; el botón de tema lo cambia y lo guarda en `localStorage` (`bolsines-tema`). Para evitar el parpadeo, leerlo en un `<script>` inline en el `<head>` antes de pintar.
3. **Tailwind** (CDN, en `base.html`):
   ```html
   <script>
     tailwind.config = { theme: { extend: {
       colors: { fondo:'var(--fondo)', tinta:'var(--tinta)', 'tinta-suave':'var(--tinta-suave)', 'tinta-tenue':'var(--tinta-tenue)',
                 acento:'var(--acento)', 'sobre-acento':'var(--sobre-acento)', sello:'var(--sello)', 'sobre-sello':'var(--sobre-sello)',
                 marca:'var(--marca)', error:'var(--error)', ok:'var(--ok)', info:'var(--info)', linea:'var(--linea)' },
       fontFamily: { display:['Bebas Neue','sans-serif'], sans:['Roboto','system-ui','sans-serif'], mono:['Roboto Mono','monospace'] },
       borderRadius: { xl2:'28px' } } } };
   </script>
   ```
4. **Fuentes** (Google Fonts, en `base.html`): Bebas Neue, Roboto 400/500/700, Roboto Mono 500.
5. **Componentes**: usar el marcado de `componentes.html` con las clases `bol-*`. Si hace falta algo nuevo, armarlo con los mismos tokens.
6. **Textos** con la voz del manual: voseo, frases cortas, decir qué pasó y qué puede hacer la persona.
7. **Accesibilidad**: botones de verdad (`<button>`), `aria-label` en botones de solo ícono, foco visible (`--acento`), contraste ya verificado en los tokens.
