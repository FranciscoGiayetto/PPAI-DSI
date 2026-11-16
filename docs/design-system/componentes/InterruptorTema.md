# InterruptorTema
Interruptor de tema (`role="switch"`). La perilla toma `marca` con el ícono en `sobre-marca`: luna en oscuro, sol en claro.

Al cambiar, la app pone `data-theme="oscuro|claro"` en `<html>` y guarda la preferencia. **Transición recomendada**: View Transitions API con un círculo que se expande desde la perilla (≈500ms, `cubic-bezier(.7,0,.2,1)`); sin soporte, cambio directo.
