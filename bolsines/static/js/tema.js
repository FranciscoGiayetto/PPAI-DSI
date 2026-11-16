/*
 * Bolsines · interruptor de tema.
 * Pone data-theme="oscuro|claro" en <html>, lo guarda en localStorage (bolsines-tema)
 * y avisa con el evento "bolsines:tema" (lo usa el mapa). El tema inicial lo lee un
 * script inline en el <head> de base.html para que no parpadee.
 * Transición: círculo que se expande desde la perilla (View Transitions API); sin soporte, cambio directo.
 */
(function () {
  var html = document.documentElement;
  var CLAVE = 'bolsines-tema';

  function temaActual() { return html.getAttribute('data-theme') === 'claro' ? 'claro' : 'oscuro'; }

  function sincronizar() {
    var claro = temaActual() === 'claro';
    document.querySelectorAll('[data-interruptor-tema]').forEach(function (btn) {
      btn.classList.toggle('is-claro', claro);
      btn.setAttribute('aria-checked', String(claro));
    });
  }

  function aplicar(tema) {
    html.setAttribute('data-theme', tema);
    try { localStorage.setItem(CLAVE, tema); } catch (e) {}
    sincronizar();
    document.dispatchEvent(new CustomEvent('bolsines:tema', { detail: { tema: tema } }));
  }

  function alternar(btn) {
    var nuevo = temaActual() === 'claro' ? 'oscuro' : 'claro';
    var reducir = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!document.startViewTransition || reducir) { aplicar(nuevo); return; }

    var r = btn.querySelector('.bol-interruptor__perilla').getBoundingClientRect();
    var x = r.left + r.width / 2, y = r.top + r.height / 2;
    var radio = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    var t = document.startViewTransition(function () { aplicar(nuevo); });
    t.ready.then(function () {
      html.animate(
        { clipPath: ['circle(0 at ' + x + 'px ' + y + 'px)', 'circle(' + radio + 'px at ' + x + 'px ' + y + 'px)'] },
        { duration: 500, easing: 'cubic-bezier(.7,0,.2,1)', pseudoElement: '::view-transition-new(root)' }
      );
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-interruptor-tema]');
    if (btn) alternar(btn);
  });
  sincronizar();
})();
