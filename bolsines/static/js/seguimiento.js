/*
 * Bolsines · pantalla de seguimiento (CU 36).
 * Lee los bolsines que manda la vista (json_script "datos-seguimiento"), arma la lista (master),
 * el detalle (detail), los filtros, el mapa y el diálogo de aviso al gerente.
 * El mapa usa Google Maps si hay clave; si no, un mapa de reemplazo con proyección simple.
 * El frontend nunca le pregunta al GPS: todo viene del servidor (Gestor).
 */
(function () {
  'use strict';

  var datos = JSON.parse(document.getElementById('datos-seguimiento').textContent);
  var cfg = window.BOLSINES_CONFIG || {};
  var bolsines = datos.bolsines;
  var origen = datos.origen;
  var movil = window.matchMedia('(max-width: 767px)');

  var $ = function (sel, raiz) { return (raiz || document).querySelector(sel); };
  var estado = { texto: '', destino: '', sel: null };

  var hoja = $('[data-hoja]');
  var lista = $('[data-lista]');
  var panelDetalle = $('[data-detalle]');
  var detalleMovil = $('[data-detalle-movil]');

  /* ───── utilidades ───── */
  function nro(n) { return 'N.º ' + n; }
  function hace(b) { return b.sin_senal ? 'sin señal' : 'hace ' + b.hace_min + ' min'; }
  function dosDigitos(n) { return (n < 10 ? '0' : '') + n; }
  function texto(t) { var s = document.createElement('span'); s.textContent = t; return s.innerHTML; }
  var ZOOM_BOLSIN = 13;

  // Ruta por la red vial entre dos puntos [lat, lng] (servidor público de OSRM, sin clave).
  // Devuelve una lista de [lat, lng]; las rutas ya pedidas se reutilizan.
  var rutasCache = {};
  function rutaPorCalles(a, b) {
    var clave = a.join(',') + '|' + b.join(',');
    if (!rutasCache[clave]) {
      var url = 'https://router.project-osrm.org/route/v1/driving/' + a[1] + ',' + a[0] + ';' + b[1] + ',' + b[0] +
                '?overview=full&geometries=geojson';
      rutasCache[clave] = fetch(url)
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (j) {
          if (!j.routes || !j.routes.length) throw new Error('sin ruta');
          return j.routes[0].geometry.coordinates.map(function (c) { return [c[1], c[0]]; });
        })
        .catch(function (e) { delete rutasCache[clave]; throw e; });
    }
    return rutasCache[clave];
  }
  function filtrados() {
    var q = estado.texto.trim().toLowerCase();
    return bolsines.filter(function (b) {
      return (!estado.destino || b.destino === estado.destino) &&
             (!q || b.precinto.toLowerCase().indexOf(q) !== -1 || String(b.nro).indexOf(q) !== -1);
    });
  }
  function mostrarEstado(nombre) {
    document.querySelectorAll('[data-estado]').forEach(function (el) { el.hidden = el.getAttribute('data-estado') !== nombre; });
    lista.hidden = !!nombre;
  }

  /* ───── lista (master) ───── */
  function renderLista() {
    var visibles = filtrados();
    $('[data-contador]').textContent = dosDigitos(bolsines.length);

    if (datos.cargando) { mostrarEstado('cargando'); $('[data-filtros]').hidden = true; return; }
    if (!bolsines.length) { mostrarEstado('vacio'); $('[data-filtros]').hidden = true; return; }   // A1
    if (!visibles.length) { mostrarEstado('sin-resultados'); }                                    // A2
    else mostrarEstado('');

    lista.innerHTML = '';
    var tpl = $('#tpl-item');
    visibles.forEach(function (b) {
      var el = tpl.content.firstElementChild.cloneNode(true);
      $('[data-nro]', el).textContent = b.nro;
      $('[data-hace]', el).textContent = hace(b);
      $('[data-destino]', el).textContent = '→ ' + b.destino;
      $('[data-precinto]', el).textContent = b.precinto;
      $('[data-icono-ok]', el).hidden = b.sin_senal;
      $('[data-icono-error]', el).hidden = !b.sin_senal;
      el.classList.toggle('is-error', b.sin_senal);
      el.classList.toggle('is-sel', estado.sel === b.nro);
      el.setAttribute('aria-pressed', String(estado.sel === b.nro));
      el.setAttribute('aria-label', 'Bolsín ' + b.nro + ' hacia ' + b.destino + ', ' + hace(b));
      el.addEventListener('click', function () { seleccionar(b.nro); });
      lista.appendChild(el);
    });
    mapa.render(visibles);
  }

  /* ───── detalle (detail) ───── */
  function armarDetalle(b) {
    var el = $('#tpl-detalle').content.firstElementChild.cloneNode(true);
    var cinta = b.sin_senal ? 'SIN SEÑAL  ·  ' : 'BOLSINES  ·  EN VIAJE  ·  ';
    var c = $('[data-cinta]', el);
    c.textContent = new Array(9).join(cinta);
    c.classList.toggle('is-error', b.sin_senal);
    $('[data-nro]', el).textContent = nro(b.nro);
    $('[data-precinto]', el).textContent = b.precinto;
    $('[data-origen]', el).textContent = cfg.origenCiudad;
    $('[data-destino-ciudad]', el).textContent = b.destino_ciudad;
    var pct = Math.round(b.avance * 100);
    $('[data-trayecto]', el).classList.toggle('is-error', b.sin_senal);
    $('[data-hecho]', el).style.width = pct + '%';
    $('[data-marca]', el).style.left = pct + '%';
    $('[data-pista]', el).setAttribute('aria-label', 'Recorrido aproximado ' + pct + '%');
    $('[data-con-senal]', el).hidden = b.sin_senal;
    $('[data-sin-senal]', el).hidden = !b.sin_senal;
    if (b.sin_senal) {
      $('[data-alerta-texto]', el).textContent = 'El ' + b.gps + ' de este bolsín no informó su ubicación. ' +
        'Sigue en estado Enviado: probá de nuevo en unos minutos.';
    } else {
      $('[data-lat]', el).textContent = b.lat.toFixed(4);
      $('[data-lng]', el).textContent = b.lng.toFixed(4);
      $('[data-senal]', el).textContent = b.ultima_senal + ' · ' + hace(b);
    }
    $('[data-peso]', el).textContent = String(b.peso_kg).replace('.', ',') + ' kg';
    $('[data-remitos]', el).textContent = dosDigitos(b.remitos);
    $('[data-salio]', el).textContent = b.salio;
    $('[data-gps]', el).textContent = b.gps;
    var btnHistorial = $('[data-historial]', el);
    btnHistorial.addEventListener('click', function () { abrirHistorial(b, btnHistorial); });
    var avisar = $('[data-avisar]', el);
    avisar.disabled = b.sin_senal;   // sin ubicación no hay nada para avisar
    avisar.addEventListener('click', function () { abrirDialogo(b, avisar); });
    $('[data-reintentar]', el).addEventListener('click', function (e) { reintentar(b, e.currentTarget); });
    $('[data-cerrar-detalle]', el).addEventListener('click', function () { seleccionar(null); });
    return el;
  }

  function seleccionar(n) {
    estado.sel = n;
    var b = bolsines.filter(function (x) { return x.nro === n; })[0];
    panelDetalle.innerHTML = ''; detalleMovil.innerHTML = '';
    if (b) {
      if (movil.matches) { detalleMovil.appendChild(armarDetalle(b)); detalleMovil.hidden = false; hoja.classList.add('con-detalle'); }
      else { panelDetalle.appendChild(armarDetalle(b)); panelDetalle.hidden = false; }
      mapa.enfocar(b);
    } else {
      panelDetalle.hidden = true; detalleMovil.hidden = true; hoja.classList.remove('con-detalle');
    }
    renderLista();
  }

  /* A3: reintentar consultar al GPS. En la demo sigue sin contestar. */
  function reintentar(b, btn) {
    btn.disabled = true;
    btn.querySelector('span').textContent = 'Consultando…';
    window.location.reload();   // el servidor vuelve a consultar al GPS Tracker
  }

  /* ───── filtros ───── */
  $('[data-buscador]').addEventListener('input', function (e) { estado.texto = e.target.value; renderLista(); });
  document.querySelectorAll('[data-chip]').forEach(function (chip) {
    chip.addEventListener('click', function () { elegirDestino(chip.getAttribute('data-chip')); });
  });
  function elegirDestino(d) {
    estado.destino = d;
    document.querySelectorAll('[data-chip]').forEach(function (c) {
      var on = c.getAttribute('data-chip') === d;
      c.classList.toggle('is-activo', on); c.setAttribute('aria-pressed', String(on));
    });
    renderLista();
  }
  $('[data-limpiar]').addEventListener('click', function () {
    $('[data-buscador]').value = ''; estado.texto = ''; elegirDestino('');
  });

  /* ───── aviso ───── */
  var aviso = $('[data-aviso]'), avisoTimer;
  function avisar(texto, error) {
    $('[data-aviso-texto]').textContent = texto;
    aviso.classList.toggle('is-error', !!error);
    aviso.hidden = false;
    clearTimeout(avisoTimer);
    avisoTimer = setTimeout(function () { aviso.hidden = true; }, 6000);
  }
  $('[data-aviso-cerrar]').addEventListener('click', function () { aviso.hidden = true; });

  /* ───── diálogo (paso 8 → CU 30) ───── */
  var velo = $('[data-velo]'), dialogo = $('.bol-dialogo', velo), volverFoco = null, dialogoBolsin = null;
  function abrirDialogo(b, origenFoco) {
    dialogoBolsin = b; volverFoco = origenFoco;
    $('[data-dialogo-texto]').textContent = 'Mandamos un correo a la Gerencia de ' + b.destino +
      ' con la ubicación del bolsín N.º ' + b.nro + '.';
    $('[data-dialogo-resumen]').innerHTML = '';
    [['ÚLTIMA SEÑAL', b.ultima_senal + ' · ' + hace(b)], ['COORDENADAS', b.lat.toFixed(4) + ', ' + b.lng.toFixed(4)]]
      .forEach(function (par) {
        var dt = document.createElement('dt'); dt.textContent = par[0];
        var dd = document.createElement('dd'); dd.textContent = par[1];
        $('[data-dialogo-resumen]').append(dt, dd);
      });
    velo.hidden = false;
    $('[data-dialogo-no]').focus();
  }
  function cerrarDialogo() { velo.hidden = true; if (volverFoco) volverFoco.focus(); }
  $('[data-dialogo-no]').addEventListener('click', cerrarDialogo);                        // A5
  $('[data-dialogo-si]').addEventListener('click', function () {
    // CU 30: el servidor (Gestor) manda el correo al gerente de la CM destino.
    var b = dialogoBolsin;
    cerrarDialogo();
    fetch(cfg.urlNotificar.replace('/0/', '/' + b.nro + '/'), { method: 'POST', headers: { 'X-CSRFToken': cfg.csrf } })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        if (res.ok) avisar('Listo, la Gerencia de ' + b.destino + ' ya tiene la ubicación');
        else avisar(res.j.mensaje || 'No se pudo enviar el correo.', true);
      })
      .catch(function () { avisar('No se pudo enviar el correo.', true); });
  });
  velo.addEventListener('click', function (e) { if (e.target === velo) cerrarDialogo(); });

  /* ───── historial de estados ───── */
  var veloHistorial = $('[data-velo-historial]'), volverFocoHistorial = null;
  function abrirHistorial(b, origenFoco) {
    volverFocoHistorial = origenFoco;
    $('[data-historial-subtitulo]').textContent = 'Bolsín ' + nro(b.nro) + ' · precinto ' + b.precinto + ' · hacia ' + b.destino;
    var ol = $('[data-historial-lista]');
    ol.innerHTML = '';
    if (!b.historial.length) {
      ol.innerHTML = '<li class="t-cuerpo-s text-tinta-tenue">No hay cambios de estado registrados.</li>';
    }
    b.historial.forEach(function (h) {
      var li = document.createElement('li');
      li.className = 'historial__paso';
      li.innerHTML =
        '<div class="historial__cabecera"><span class="historial__estado">' + texto(h.estado_nuevo) + '</span>' +
        '<span class="historial__fecha">' + texto(h.fecha_hora) + '</span></div>' +
        '<p class="historial__detalle">' +
        (h.estado_anterior && h.estado_anterior !== '—' ? 'Desde ' + texto(h.estado_anterior) + ' · ' : 'Alta del bolsín · ') +
        texto(h.empleado) + '</p>';
      ol.appendChild(li);
    });
    veloHistorial.hidden = false;
    $('[data-historial-cerrar]').focus();
  }
  function cerrarHistorial() { veloHistorial.hidden = true; if (volverFocoHistorial) volverFocoHistorial.focus(); }
  $('[data-historial-cerrar]').addEventListener('click', cerrarHistorial);
  veloHistorial.addEventListener('click', function (e) { if (e.target === veloHistorial) cerrarHistorial(); });
  document.addEventListener('keydown', function (e) {
    if (!veloHistorial.hidden && e.key === 'Escape') cerrarHistorial();
  });
  document.addEventListener('keydown', function (e) {
    if (velo.hidden) return;
    if (e.key === 'Escape') { cerrarDialogo(); return; }
    if (e.key === 'Tab') {   // foco atrapado
      var f = dialogo.querySelectorAll('button:not([disabled])');
      var primero = f[0], ultimo = f[f.length - 1];
      if (e.shiftKey && document.activeElement === primero) { e.preventDefault(); ultimo.focus(); }
      else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primero.focus(); }
    }
  });

  /* ───── hoja inferior (móvil) ───── */
  (function () {
    var agarre = $('[data-hoja-agarre]'), y0 = null, alto0 = 0, movido = false;
    function expandir(si) {
      hoja.classList.toggle('is-expandida', si);
      agarre.setAttribute('aria-label', si ? 'Contraer lista' : 'Expandir lista');
    }
    agarre.addEventListener('pointerdown', function (e) {
      y0 = e.clientY; alto0 = hoja.getBoundingClientRect().height; movido = false;
      agarre.setPointerCapture(e.pointerId); hoja.classList.add('is-arrastrando');
    });
    agarre.addEventListener('pointermove', function (e) {
      if (y0 === null) return;
      var dy = y0 - e.clientY;
      if (Math.abs(dy) > 4) movido = true;
      hoja.style.height = Math.max(160, alto0 + dy) + 'px';
    });
    agarre.addEventListener('pointerup', function (e) {
      if (y0 === null) return;
      var dy = y0 - e.clientY;
      hoja.classList.remove('is-arrastrando'); hoja.style.height = '';
      y0 = null;
      if (hoja.classList.contains('con-detalle')) { if (movido && dy < -40) seleccionar(null); return; }
      if (!movido) expandir(!hoja.classList.contains('is-expandida'));
      else expandir(dy > 40 ? true : dy < -40 ? false : hoja.classList.contains('is-expandida'));
    });
    $('[data-buscador]').addEventListener('focus', function () { if (movil.matches) expandir(true); });
  })();

  /* ───── colapsar panel (escritorio) ───── */
  (function () {
    var boton = $('[data-panel-colapsar]');
    if (!boton) return;
    var CLAVE = 'bolsines-lista-colapsada';
    function fijar(colapsado) {
      hoja.classList.toggle('is-colapsada', colapsado);
      boton.setAttribute('aria-expanded', String(!colapsado));
      var etiqueta = colapsado ? 'Expandir lista' : 'Colapsar lista';
      boton.setAttribute('aria-label', etiqueta);
      boton.setAttribute('title', etiqueta);
      try { localStorage.setItem(CLAVE, colapsado ? '1' : '0'); } catch (e) {}
    }
    boton.addEventListener('click', function () { fijar(!hoja.classList.contains('is-colapsada')); });
    var guardado = null;
    try { guardado = localStorage.getItem(CLAVE); } catch (e) {}
    if (guardado === '1') fijar(true);
  })();

  /* ───── mapa ───── */
  var mapa = null;
  if (cfg.mapsKey) {
    mapa = crearMapaReemplazo();
    cargarGoogleMaps();
  } else if (window.L) {
    mapa = crearLeafletMapa();
  } else {
    mapa = crearMapaReemplazo();
  }

  document.querySelectorAll('[data-zoom]').forEach(function (btn) {
    btn.addEventListener('click', function () { mapa.zoom(parseInt(btn.getAttribute('data-zoom'), 10)); });
  });

  // Mapa con OpenStreetMap / CartoDB vía Leaflet (Opción sin API Key, interactivo y profesional)
  function crearLeafletMapa() {
    var raiz = $('#mapa');
    raiz.innerHTML = '';
    var div = document.createElement('div');
    div.style.cssText = 'position:absolute;inset:0;z-index:0;';
    raiz.appendChild(div);

    var lfMap = L.map(div, {
      center: [origen.lat, origen.lng],
      zoom: 6,
      zoomControl: false,
      attributionControl: true,
      // Zoom más fluido: no pedir/renderizar teselas nuevas mientras la animación de zoom está
      // en curso (se piden al terminar) y mantener un colchón de teselas ya descargadas alrededor
      // de la vista para que paneos/zooms cercanos no esperen red.
      zoomAnimation: true,
      markerZoomAnimation: true,
      wheelPxPerZoomLevel: 90
    });

    // Esri (gratis, sin API key): una capa de teselas por tema, en vez de una sola capa de
    // calles invertida con filtro CSS. Un filtro sobre todo el panel de teselas se tiene que
    // recalcular en cada frame de la animación de zoom —con decenas de teselas visibles eso es
    // el cuello de botella que lo pone trabado—, así que la solución es no filtrar nada: cada
    // tema carga su propia cartografía ya oscura o clara.
    var opcionesTiles = {
      maxZoom: 19, crossOrigin: true, updateWhenZooming: false, keepBuffer: 3
    };
    var tileClaro = L.layerGroup([
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
        Object.assign({ attribution: 'Tiles &copy; Esri &mdash; Esri, HERE, Garmin, &copy; OpenStreetMap' }, opcionesTiles))
    ]);
    var tileOscuro = L.layerGroup([
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        Object.assign({ maxZoom: 16, attribution: 'Tiles &copy; Esri &mdash; Esri, HERE, Garmin' }, opcionesTiles)),
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
        Object.assign({ maxZoom: 16 }, opcionesTiles))
    ]);
    var tileActual = null;

    function actualizarTiles() {
      var oscuro = document.documentElement.getAttribute('data-theme') !== 'claro';
      var siguiente = oscuro ? tileOscuro : tileClaro;
      if (siguiente === tileActual) return;
      if (tileActual) lfMap.removeLayer(tileActual);
      siguiente.addTo(lfMap);
      tileActual = siguiente;
    }
    actualizarTiles();
    document.addEventListener('bolsines:tema', actualizarTiles);

    var capaRutas = L.layerGroup().addTo(lfMap);
    var capaMarkers = L.layerGroup().addTo(lfMap);
    var actuales = [];

    function encuadrar() {
      var bounds = L.latLngBounds([[origen.lat, origen.lng]]);
      bolsines.forEach(function (b) {
        bounds.extend([b.destino_lat, b.destino_lng]);
        if (!b.sin_senal && b.lat && b.lng) {
          bounds.extend([b.lat, b.lng]);
        }
      });
      var pad = movil.matches
        ? { paddingTopLeft: [20, 90], paddingBottomRight: [20, 240] }
        : { paddingTopLeft: [380, 110], paddingBottomRight: [400, 100] };
      lfMap.fitBounds(bounds, pad);
    }

    function dibujarRutas(b, recorrida, restante, acento) {
      L.polyline(recorrida, { color: acento, weight: 5, opacity: 0.9, lineCap: 'round', lineJoin: 'round' }).addTo(capaRutas);
      L.polyline(restante, { color: acento, weight: 4, opacity: 0.6, dashArray: '2, 10', lineCap: 'round', lineJoin: 'round' }).addTo(capaRutas);
    }
    function render(lista) {
      actuales = lista;
      capaMarkers.clearLayers();
      capaRutas.clearLayers();

      var acento = getComputedStyle(document.documentElement).getPropertyValue('--acento').trim() || '#f43f5e';

      // 1. Origen
      var iconOrigen = L.divIcon({
        className: 'mapa__pin-leaflet',
        html: '<div class="mapa__pin" style="transform:translate(-50%,-50%);"><span class="mapa__origen"></span><span class="mapa__nombre">' + texto(origen.nombre) + '</span></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });
      L.marker([origen.lat, origen.lng], { icon: iconOrigen, interactive: false }).addTo(capaMarkers);

      // 2. Destinos
      var vistos = {};
      lista.forEach(function (b) {
        if (vistos[b.destino]) return;
        vistos[b.destino] = 1;
        var iconDest = L.divIcon({
          className: 'mapa__pin-leaflet',
          html: '<div class="mapa__pin" style="transform:translate(-50%,-50%);"><span class="mapa__destino"></span><span class="mapa__nombre">' + texto(b.destino) + '</span></div>',
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        });
        L.marker([b.destino_lat, b.destino_lng], { icon: iconDest, interactive: false }).addTo(capaMarkers);
      });

      // 3. Bolsines en viaje
      lista.forEach(function (b) {
        if (b.sin_senal || !b.lat || !b.lng) return;
        var es = b.nro === estado.sel;
        var btn = marcador(b, es);

        var contenedor = document.createElement('div');
        contenedor.className = 'mapa__pin' + (es ? ' is-sel' : '');
        contenedor.style.transform = 'translate(-50%,-50%)';
        contenedor.appendChild(btn);
        if (es) {
          contenedor.insertAdjacentHTML('beforeend', '<span class="mapa__etiqueta">' + nro(b.nro) + ' · ' + hace(b) + '</span>');

          // Mientras llega la ruta por calles se ven las rectas; después se reemplazan.
          dibujarRutas(b, [[origen.lat, origen.lng], [b.lat, b.lng]], [[b.lat, b.lng], [b.destino_lat, b.destino_lng]], acento);
          Promise.all([
            rutaPorCalles([origen.lat, origen.lng], [b.lat, b.lng]),
            rutaPorCalles([b.lat, b.lng], [b.destino_lat, b.destino_lng])
          ]).then(function (r) {
            if (estado.sel !== b.nro) return;   // el usuario ya eligió otro
            capaRutas.clearLayers();
            dibujarRutas(b, r[0], r[1], acento);
          }).catch(function () { /* sin ruteo quedan las rectas */ });
        }

        var iconBolsin = es
          ? L.divIcon({
              className: 'mapa__pin-leaflet',
              html: '<div class="mapa__gota"><span class="mapa__gota-cuerpo"></span>' +
                    '<span class="mapa__etiqueta mapa__gota-etiqueta">' + nro(b.nro) + ' · ' + hace(b) + '</span></div>',
              iconSize: [36, 48],
              iconAnchor: [18, 48]   // la punta de la gota marca la coordenada exacta
            })
          : L.divIcon({
              className: 'mapa__pin-leaflet',
              html: contenedor.outerHTML,
              iconSize: [40, 40],
              iconAnchor: [20, 20]
            });

        var marker = L.marker([b.lat, b.lng], { icon: iconBolsin, zIndexOffset: es ? 1000 : 100 }).addTo(capaMarkers);
        marker.on('click', function () { seleccionar(b.nro); });
      });
    }

    encuadrar();
    window.addEventListener('resize', function () { lfMap.invalidateSize(); });

    return {
      render: render,
      enfocar: function (b) {
        if (b.sin_senal || !b.lat || !b.lng) return;
        // en móvil la hoja tapa la parte de abajo: el punto se corre hacia arriba
        var destino = L.latLng(b.lat, b.lng);
        if (movil.matches) {
          var p = lfMap.project(destino, ZOOM_BOLSIN).add([0, 120]);
          destino = lfMap.unproject(p, ZOOM_BOLSIN);
        }
        lfMap.flyTo(destino, ZOOM_BOLSIN, { duration: 1.2 });
      },
      zoom: function (dir) {
        if (dir === 0) encuadrar();
        else if (dir > 0) lfMap.zoomIn();
        else lfMap.zoomOut();
      }
    };
  }

  // Mapa de reemplazo: proyección equirectangular de una caja alrededor de los puntos.
  function crearMapaReemplazo() {
    var raiz = $('[data-mapa-reemplazo]');
    var capa = document.createElement('div'); capa.className = 'mapa__capa'; raiz.appendChild(capa);
    var vista = { lat: origen.lat, lng: origen.lng, span: 0 };
    var actuales = [];

    function puntos() {
      var p = [[origen.lat, origen.lng]];
      bolsines.forEach(function (b) { p.push([b.destino_lat, b.destino_lng]); if (!b.sin_senal) p.push([b.lat, b.lng]); });
      return p;
    }
    function encuadrar() {
      var p = puntos(), lats = p.map(function (x) { return x[0]; }), lngs = p.map(function (x) { return x[1]; });
      vista.lat = (Math.max.apply(null, lats) + Math.min.apply(null, lats)) / 2;
      vista.lng = (Math.max.apply(null, lngs) + Math.min.apply(null, lngs)) / 2;
      vista.span = Math.max(Math.max.apply(null, lats) - Math.min.apply(null, lats),
                            Math.max.apply(null, lngs) - Math.min.apply(null, lngs), 2) * 1.35;
    }
    function aPantalla(lat, lng) {
      var w = raiz.clientWidth, h = raiz.clientHeight;
      // el centro útil queda entre los paneles en escritorio y arriba de la hoja en móvil
      var cx = movil.matches ? w / 2 : 360 + (w - 360 - 390) / 2 + 16;
      var cy = movil.matches ? (h - 210) / 2 + 40 : h / 2 + 30;
      var util = movil.matches ? Math.min(w, h - 260) : Math.min(w - 780, h - 140);
      var esc = Math.max(util, 200) / vista.span;
      return [cx + (lng - vista.lng) * esc, cy - (lat - vista.lat) * esc];
    }
    function pin(clase, lat, lng, html) {
      var el = document.createElement('div'); el.className = 'mapa__pin ' + clase;
      var xy = aPantalla(lat, lng); el.style.left = xy[0] + 'px'; el.style.top = xy[1] + 'px';
      if (html) el.innerHTML = html;
      capa.appendChild(el); return el;
    }

    var fondo = $('[data-mapa-fondo]'), spanBase = null;
    function render(lista) {
      actuales = lista; capa.innerHTML = '';
      // El fondo acompaña el zoom (escala respecto del encuadre inicial)
      if (spanBase === null) spanBase = vista.span;
      fondo.style.transform = 'scale(' + (spanBase / vista.span) + ')';
      var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('class', 'mapa__ruta');
      capa.appendChild(svg);
      var sel = bolsines.filter(function (b) { return b.nro === estado.sel; })[0];
      if (sel && !sel.sin_senal) {
        var a = aPantalla(origen.lat, origen.lng), m = aPantalla(sel.lat, sel.lng), d = aPantalla(sel.destino_lat, sel.destino_lng);
        svg.innerHTML = '<path class="hecho" d="M' + a + 'L' + m + '"/><path class="resto" d="M' + m + 'L' + d + '"/>';
      }
      var vistos = {};
      lista.forEach(function (b) {
        if (vistos[b.destino]) return; vistos[b.destino] = 1;
        pin('', b.destino_lat, b.destino_lng, '<span class="mapa__destino"></span><span class="mapa__nombre">' + texto(b.destino) + '</span>');
      });
      pin('', origen.lat, origen.lng, '<span class="mapa__origen"></span><span class="mapa__nombre">' + texto(origen.nombre) + '</span>');
      lista.forEach(function (b) {
        if (b.sin_senal) return;   // A3: sin coordenadas no se dibuja
        var es = b.nro === estado.sel;
        var p = pin(es ? 'is-sel' : '', b.lat, b.lng);
        var btn = marcador(b, es);
        p.appendChild(btn);
        if (es) p.insertAdjacentHTML('beforeend', '<span class="mapa__etiqueta">' + nro(b.nro) + ' · ' + hace(b) + '</span>');
      });
    }

    encuadrar();
    window.addEventListener('resize', function () { render(actuales); });
    return {
      render: render,
      enfocar: function (b) {
        if (!b.sin_senal) { vista.lat = b.lat; vista.lng = b.lng; vista.span = 0.6; }
        render(actuales);
      },
      zoom: function (dir) {
        if (dir === 0) encuadrar(); else vista.span *= dir > 0 ? 0.7 : 1.4;
        render(actuales);
      }
    };
  }

  function marcador(b, es) {
    var btn = $('#tpl-marcador').content.firstElementChild.cloneNode(true);
    btn.classList.toggle('is-sel', es);
    btn.setAttribute('aria-label', 'Bolsín ' + b.nro + ' hacia ' + b.destino);
    btn.addEventListener('click', function () { seleccionar(b.nro); });
    return btn;
  }

  // Google Maps (si hay GOOGLE_MAPS_API_KEY). Reemplaza al mapa de reemplazo con la misma interfaz.
  function cargarGoogleMaps() {
    window.__bolsinesMapsListo = function () {
      google.maps.importLibrary('marker').then(function (lib) { mapa = crearGoogleMapa(lib); renderLista(); });
    };
    var s = document.createElement('script');
    s.src = 'https://maps.googleapis.com/maps/api/js?key=' + encodeURIComponent(cfg.mapsKey) +
            '&v=weekly&loading=async&callback=__bolsinesMapsListo';
    s.async = true;
    s.onerror = function () { avisar('No pudimos cargar Google Maps. Te mostramos el mapa simplificado.', true); };
    document.head.appendChild(s);
  }

  function crearGoogleMapa(lib) {
    var raiz = $('#mapa');
    var div = document.createElement('div'); div.style.cssText = 'position:absolute;inset:0';
    raiz.innerHTML = ''; raiz.appendChild(div);
    var oscuro = document.documentElement.getAttribute('data-theme') !== 'claro';
    var gm = new google.maps.Map(div, {
      center: { lat: origen.lat, lng: origen.lng }, zoom: 5, mapId: cfg.mapId,
      disableDefaultUI: true, gestureHandling: 'greedy',
      colorScheme: oscuro ? google.maps.ColorScheme.DARK : google.maps.ColorScheme.LIGHT
    });
    var objetos = [], actuales = [];
    function punto(html) { var d = document.createElement('div'); d.className = 'mapa__pin'; d.style.position = 'relative'; d.style.transform = 'translateY(50%)'; d.innerHTML = html; return d; }
    function agregar(lat, lng, contenido) { objetos.push(new lib.AdvancedMarkerElement({ map: gm, position: { lat: lat, lng: lng }, content: contenido })); }
    function encuadrar() {
      var bounds = new google.maps.LatLngBounds();
      bounds.extend(origen);
      bolsines.forEach(function (b) { bounds.extend({ lat: b.destino_lat, lng: b.destino_lng }); });
      gm.fitBounds(bounds, movil.matches ? { top: 80, bottom: 260, left: 24, right: 24 } : { top: 110, bottom: 90, left: 400, right: 430 });
    }
    function render(lista) {
      actuales = lista;
      objetos.forEach(function (o) { o.map = null; if (o.setMap) o.setMap(null); }); objetos = [];
      var acento = getComputedStyle(document.documentElement).getPropertyValue('--acento').trim();
      agregar(origen.lat, origen.lng, punto('<span class="mapa__origen"></span>'));
      lista.forEach(function (b) { agregar(b.destino_lat, b.destino_lng, punto('<span class="mapa__destino"></span>')); });
      lista.forEach(function (b) {
        if (b.sin_senal) return;
        var es = b.nro === estado.sel, c = document.createElement('div'); c.className = 'mapa__pin' + (es ? ' is-sel' : '');
        c.style.position = 'relative'; c.style.transform = 'translateY(50%)';
        c.appendChild(marcador(b, es));
        if (es) {
          c.insertAdjacentHTML('beforeend', '<span class="mapa__etiqueta">' + nro(b.nro) + ' · ' + hace(b) + '</span>');
          objetos.push(new google.maps.Polyline({ map: gm, path: [origen, { lat: b.lat, lng: b.lng }], strokeColor: acento, strokeWeight: 4 }));
          objetos.push(new google.maps.Polyline({ map: gm, path: [{ lat: b.lat, lng: b.lng }, { lat: b.destino_lat, lng: b.destino_lng }],
            strokeOpacity: 0, icons: [{ icon: { path: 'M 0,-1 0,1', strokeOpacity: 1, strokeColor: acento, scale: 2 }, offset: '0', repeat: '12px' }] }));
        }
        agregar(b.lat, b.lng, c);
      });
    }
    encuadrar();
    // El esquema de color de Google Maps no cambia en caliente: se recrea el mapa.
    document.addEventListener('bolsines:tema', function () { mapa = crearGoogleMapa(lib); renderLista(); }, { once: true });
    return {
      render: render,
      enfocar: function (b) { if (!b.sin_senal) { gm.panTo({ lat: b.lat, lng: b.lng }); gm.setZoom(ZOOM_BOLSIN); } },
      zoom: function (dir) { if (dir === 0) encuadrar(); else gm.setZoom(gm.getZoom() + dir); }
    };
  }

  // El mapa de reemplazo usa colores de los tokens vía CSS, así que se redibuja solo al cambiar de tema.
  movil.addEventListener('change', function () { seleccionar(estado.sel); });

  /* ───── arranque ───── */
  var primero = bolsines.filter(function (b) { return !b.sin_senal; })[0];
  if (primero && !movil.matches && !datos.cargando) seleccionar(primero.nro);
  else renderLista();
})();
