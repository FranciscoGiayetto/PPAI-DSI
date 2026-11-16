/*
 * Bolsines · bolsa animada en loop (vector, sin dependencias).
 * La bolsa de pie se da vuelta, las manijas se vuelven ruedas, sale por la derecha,
 * entra por la izquierda y vuelve a quedar de pie. Empieza y termina igual (5,4 s por vuelta).
 *
 * Uso:  <div data-bolsa-animada data-color="var(--sobre-marca)" style="width:620px;height:384px"></div>
 *       <script src="{% static 'js/bolsa-animada.js' %}" defer></script>
 * Pensada para el panel de marca del login y la pantalla "Cargando ubicaciones".
 * Con prefers-reduced-motion queda la bolsa quieta. Se pausa si la pestaña no está visible.
 */
(function () {
  var NS = 'http://www.w3.org/2000/svg', STEM = 233, R = 46, RI = 19;
  var B = [{ y0: 0, y1: 124, L: 183, rx: 91, yi0: 42, yi1: 82, Li: 141, rxi: 66 }, { y0: 82, y1: 229, L: 265, rx: 136, yi0: 124, yi1: 187, Li: 223, rxi: 115 }];
  function wheel(c) { return { y0: c - R, y1: c + R, L: R, rx: R, yi0: c - RI, yi1: c + RI, Li: RI, rxi: RI }; }
  var W = [wheel(48), wheel(182)];
  function clamp(x) { return Math.max(0, Math.min(1, x)); }
  function lerp(a, b, u) { return a + (b - a) * u; }
  function io(u) { return u * u * (3 - 2 * u); }
  function inC(u) { return u * u * u; }
  function outC(u) { return 1 - Math.pow(1 - u, 3); }
  function back(u, k) { var v = u - 1; return 1 + (k + 1) * v * v * v + k * v * v; }
  function bowl(b) {
    var ry = (b.y1 - b.y0) / 2, rx = Math.min(b.rx, b.L), cx = STEM + b.L - rx, ryi = (b.yi1 - b.yi0) / 2, rxi = Math.min(b.rxi, b.Li), cxi = STEM + b.Li - rxi;
    return 'M' + (STEM - 8) + ' ' + b.y0 + 'L' + cx + ' ' + b.y0 + 'A' + rx + ' ' + ry + ' 0 0 1 ' + cx + ' ' + b.y1 + 'L' + (STEM - 8) + ' ' + b.y1 + 'Z' +
      'M' + STEM + ' ' + b.yi0 + 'L' + cxi + ' ' + b.yi0 + 'A' + rxi + ' ' + ryi + ' 0 0 1 ' + cxi + ' ' + b.yi1 + 'L' + STEM + ' ' + b.yi1 + 'Z';
  }
  function frame(t) {
    var seg = function (a, b) { return clamp((t - a) / (b - a)); };
    var theta = -90, m = 0, tx = 0, ty = 0, lines = 0;
    if (t < 1.7) ty = 6 * Math.sin(t * 3);
    else if (t < 2.25) { var u = seg(1.7, 2.25); theta = -90 + 180 * back(u, 1.2); ty = -46 * Math.sin(Math.PI * u); }
    else {
      theta = 90;
      if (t < 4.25) {
        m = t < 2.6 ? back(seg(2.25, 2.6), 1.6) : (t < 3.9 ? 1 : 1 - io(seg(3.9, 4.25)));
        if (t >= 2.6 && t < 2.8) tx = -34 * outC(seg(2.6, 2.8));
        else if (t >= 2.8 && t < 3.3) { tx = -34 + 940 * inC(seg(2.8, 3.3)); lines = 1; }
        else if (t >= 3.3 && t < 3.9) { tx = -940 + 940 * back(seg(3.3, 3.9), 1.1); lines = 1 - seg(3.75, 3.9); }
      } else if (t < 4.85) { var v = seg(4.25, 4.85); theta = 90 + 180 * back(v, 1.2); ty = -46 * Math.sin(Math.PI * v); }
      else { theta = 270; ty = 6 * Math.sin((t - 4.85) * 3); }
    }
    var mix = function (a, b) { var o = {}; for (var k in a) o[k] = lerp(a[k], b[k], m); return o; };
    return { tf: 'translate(' + tx.toFixed(1) + ' ' + ty.toFixed(1) + ') rotate(' + theta.toFixed(2) + ') translate(-116 -148)', b0: bowl(mix(B[0], W[0])), b1: bowl(mix(B[1], W[1])), lines: lines, left: tx - 160 };
  }
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  function montar(host) {
    var svg = el('svg', { viewBox: '-500 -330 1000 620', role: 'img', 'aria-label': 'Bolsines', style: 'width:100%;height:100%;display:block;overflow:visible' }, host);
    var g = el('g', { fill: host.getAttribute('data-color') || 'currentColor' }, svg);
    var ls = [-40, 6, 52].map(function (y) { return el('rect', { y: y, height: 22, rx: 2, width: 0 }, g); });
    var mk = el('g', {}, g);
    el('path', { d: 'M0 0L233 0L233 229L0 296Z' }, mk);
    var p0 = el('path', { 'fill-rule': 'evenodd' }, mk), p1 = el('path', { 'fill-rule': 'evenodd' }, mk);
    function pintar(t) {
      var o = frame(t);
      mk.setAttribute('transform', o.tf); p0.setAttribute('d', o.b0); p1.setAttribute('d', o.b1);
      var L = 150 * o.lines;
      [[-20], [-4], [12]].forEach(function (d, i) { ls[i].setAttribute('x', (o.left + d[0] - L).toFixed(1)); ls[i].setAttribute('width', L.toFixed(1)); });
    }
    pintar(0);
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var t0 = performance.now(), pausa = 0;
    function tick(now) { if (!document.hidden) pintar(((now - t0) / 1000) % 5.4); requestAnimationFrame(tick); }
    requestAnimationFrame(tick);
  }
  function iniciar() { document.querySelectorAll('[data-bolsa-animada]').forEach(montar); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
