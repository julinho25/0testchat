#!/usr/bin/env python3
"""
Bot de auto clique em números (Python + Selenium).

Exemplo de uso:
python tools/auto_click_bot.py \
  --url "https://bravo.bet.br/cassino-ao-vivo/roleta-brasileira/play" \
  --container ".racetrack-table" \
  --item ".table-cell" \
  --numbers 12 28 35 \
  --interval 0.45 \
  --debug

Pré-requisitos:
- Python 3.10+
- pip install selenium webdriver-manager
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass

from selenium import webdriver
from selenium.common.exceptions import JavascriptException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class BotConfig:
    url: str
    container_selector: str
    item_selector: str
    numbers: set[int]
    interval: float
    debug: bool
    headless: bool


def parse_args() -> BotConfig:
    parser = argparse.ArgumentParser(description="Auto clique em números dentro de uma div.")
    parser.add_argument("--url", required=True, help="URL da página alvo")
    parser.add_argument("--container", required=True, help="Seletor CSS da div principal")
    parser.add_argument("--item", default="*", help="Seletor CSS dos itens numéricos (default: *)")
    parser.add_argument("--numbers", nargs="+", required=True, type=int, help="Números a clicar")
    parser.add_argument(
        "--interval", type=float, default=0.5, help="Intervalo em segundos entre ciclos (default: 0.5)"
    )
    parser.add_argument("--debug", action="store_true", help="Ativa logs")
    parser.add_argument("--headless", action="store_true", help="Executa sem UI")

    args = parser.parse_args()
    return BotConfig(
        url=args.url,
        container_selector=args.container,
        item_selector=args.item,
        numbers=set(args.numbers),
        interval=args.interval,
        debug=args.debug,
        headless=args.headless,
    )


def build_driver(headless: bool) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1400,900")
    if headless:
        options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def click_targets(driver: webdriver.Chrome, config: BotConfig) -> int:
    script = r"""
const [containerSelector, itemSelector, numbers] = arguments;
const container = document.querySelector(containerSelector);
if (!container) {
  return { clicked: 0, reason: 'container_not_found' };
}

const numberSet = new Set(numbers.map(Number));
const items = Array.from(container.querySelectorAll(itemSelector || '*'));
let clicked = 0;

function parseNumber(text) {
  if (!text) return null;
  const clean = String(text).replace(/[^0-9-]/g, '');
  if (!clean) return null;
  const value = Number(clean);
  return Number.isFinite(value) ? value : null;
}

for (const el of items) {
  const value = parseNumber(el.textContent);
  if (value === null || !numberSet.has(value)) continue;

  ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach((eventName) => {
    el.dispatchEvent(new MouseEvent(eventName, { bubbles: true, cancelable: true, view: window }));
  });
  clicked += 1;
}

return { clicked, reason: 'ok' };
"""

    result = driver.execute_script(script, config.container_selector, config.item_selector, list(config.numbers))
    if not isinstance(result, dict):
        return 0

    if config.debug and result.get("reason") != "ok":
        print(f"[debug] ciclo sem clique: {result}")

    return int(result.get("clicked", 0))


def run_bot(config: BotConfig) -> None:
    driver = build_driver(config.headless)
    try:
        driver.get(config.url)
        print("Página aberta. Faça login/manual e deixe a grade visível.")
        print("Iniciando bot em 5 segundos...")
        time.sleep(5)

        total_clicks = 0
        while True:
            clicked_now = click_targets(driver, config)
            total_clicks += clicked_now

            if config.debug:
                print(f"[debug] clicados no ciclo: {clicked_now} | total: {total_clicks}")

            time.sleep(config.interval)
    except KeyboardInterrupt:
        print("\nBot interrompido pelo usuário (Ctrl+C).")
    except (WebDriverException, JavascriptException) as exc:
        print(f"Erro no WebDriver/JS: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.quit()


def main() -> None:
    config = parse_args()

    if config.interval < 0.05:
        print("--interval muito baixo; use pelo menos 0.05s", file=sys.stderr)
        sys.exit(2)

    if not config.numbers:
        print("Informe ao menos um número em --numbers", file=sys.stderr)
        sys.exit(2)

    invalid = [n for n in config.numbers if not re.match(r"^-?\d+$", str(n))]
    if invalid:
        print(f"Números inválidos em --numbers: {invalid}", file=sys.stderr)
        sys.exit(2)

    run_bot(config)


if __name__ == "__main__":
    main()
