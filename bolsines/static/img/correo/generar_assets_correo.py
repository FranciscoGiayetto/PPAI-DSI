"""
Genera las imágenes de marca embebidas (cid) en el correo del CU 30, a partir de los SVG del
design system (docs/design-system/logos, docs/design-system/iconos). No se ejecuta en runtime:
los PNG resultantes quedan versionados en esta misma carpeta. Volver a correr solo si cambia el
logo/ícono fuente. Requiere `pip install svglib reportlab` (no están en requirements.txt porque
son solo de build, no de runtime).

Uso: python bolsines/static/img/correo/generar_assets_correo.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

RAIZ = Path(__file__).resolve().parent.parent.parent.parent.parent
SALIDA = Path(__file__).resolve().parent


def _render(src: Path, color_hex: str, destino: Path, alto_px: int) -> None:
    """Sustituye currentColor por `color_hex`, rasteriza y vuelve transparente el fondo blanco."""
    svg = src.read_text(encoding='utf-8').replace('currentColor', color_hex)
    tmp = destino.with_suffix('.tmp.svg')
    tmp.write_text(svg, encoding='utf-8')
    try:
        dibujo = svg2rlg(str(tmp))
        escala = alto_px / dibujo.height
        dibujo.width *= escala
        dibujo.height *= escala
        dibujo.scale(escala, escala)
        renderPM.drawToFile(dibujo, str(destino), fmt='PNG')
    finally:
        tmp.unlink(missing_ok=True)

    imagen = Image.open(destino).convert('RGBA')
    pixeles = [(r, g, b, 0) if (r > 245 and g > 245 and b > 245) else (r, g, b, a)
               for r, g, b, a in imagen.getdata()]
    imagen.putdata(pixeles)
    imagen.save(destino)
    print(f'{destino.relative_to(RAIZ)}  {imagen.size}')


if __name__ == '__main__':
    # Wordmark (bolsa + OLSINES) en amarillo #FDBD4F: color "sobre-marca" sobre el header azul
    # (regla del Logo.md: "amarillo sobre azul en claro").
    _render(RAIZ / 'bolsines/templates/logos/bolsines-logotipo.svg', '#FDBD4F',
            SALIDA / 'wordmark.png', alto_px=64)

    # Camioncito en azul-noche #16324F: texto sobre la cinta amarilla "sello" (giro de la bolsa
    # que, según el manual de marca, significa "en viaje").
    _render(RAIZ / 'bolsines/templates/iconos/camioncito.svg', '#16324F',
            SALIDA / 'camioncito.png', alto_px=40)
