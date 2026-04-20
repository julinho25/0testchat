/**
 * Auto click de números em elementos de uma grade (ex.: roleta online).
 *
 * Uso no DevTools (Console):
 * 1) Cole este arquivo no console OU importe em uma extensão/userscript.
 * 2) Execute:
 *    const stop = startAutoClickNumbers({
 *      containerSelector: '.sua-div-com-numeros',
 *      numberSelector: '.seletor-do-numero',
 *      numbersToClick: [12, 28, 35],
 *      intervalMs: 450,
 *      debug: true,
 *    });
 * 3) Para parar: stop();
 */

function parseNumber(text) {
  if (!text) return null;
  const value = Number(String(text).replace(/[^0-9-]/g, ''));
  return Number.isFinite(value) ? value : null;
}

function findNumberElements(container, numberSelector) {
  if (!container) return [];

  const candidates = numberSelector
    ? Array.from(container.querySelectorAll(numberSelector))
    : Array.from(container.querySelectorAll('*'));

  return candidates.filter((el) => parseNumber(el.textContent) !== null);
}

function clickElement(el) {
  ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach((eventName) => {
    el.dispatchEvent(
      new MouseEvent(eventName, {
        bubbles: true,
        cancelable: true,
        view: window,
      }),
    );
  });
}

export function startAutoClickNumbers({
  containerSelector,
  numberSelector = '',
  numbersToClick,
  intervalMs = 500,
  debug = false,
}) {
  if (!containerSelector) {
    throw new Error('containerSelector é obrigatório.');
  }

  const targets = new Set((numbersToClick || []).map((n) => Number(n)));
  if (!targets.size) {
    throw new Error('Informe pelo menos um número em numbersToClick.');
  }

  const timer = setInterval(() => {
    const container = document.querySelector(containerSelector);
    if (!container) {
      if (debug) console.log('[auto-click] container não encontrado');
      return;
    }

    const elements = findNumberElements(container, numberSelector);
    elements.forEach((el) => {
      const value = parseNumber(el.textContent);
      if (targets.has(value)) {
        clickElement(el);
        if (debug) console.log(`[auto-click] clicado: ${value}`, el);
      }
    });
  }, intervalMs);

  return function stopAutoClickNumbers() {
    clearInterval(timer);
    if (debug) console.log('[auto-click] parado');
  };
}

// Exposição opcional para uso direto no console do navegador.
if (typeof window !== 'undefined') {
  window.startAutoClickNumbers = startAutoClickNumbers;
}
