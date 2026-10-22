"""Tira screenshots do app para conferência visual (não é parte do jogo).

Precisa do Playwright, que é dependência de desenvolvimento::

    pip install -r requirements-dev.txt
    playwright install chromium
"""

import sys

from playwright.sync_api import sync_playwright  # pyright: ignore[reportMissingImports]

URL = "http://localhost:8501"
SAIDA = "shots"


def main():
    with sync_playwright() as p:
        nav = p.chromium.launch()
        page = nav.new_page(viewport={"width": 1500, "height": 1000})

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(4000)
        page.screenshot(path=f"{SAIDA}/01_inicio.png", full_page=True)

        # escolher Flamengo
        page.get_by_role("button", name="Escolher FLA").first.click()
        page.wait_for_timeout(4000)
        page.screenshot(path=f"{SAIDA}/02_painel.png", full_page=True)

        def nav_page(label, arquivo, depois=None):
            page.get_by_role("button", name=label).first.click()
            page.wait_for_timeout(2500)
            if depois:
                depois()
            page.wait_for_timeout(1500)
            page.screenshot(path=f"{SAIDA}/{arquivo}", full_page=True)

        nav_page("👥 Elenco", "03_elenco.png")
        nav_page("📋 Tática", "04_tatica.png")

        def simular():
            page.get_by_role("button", name="⚽ SIMULAR RODADA!").first.click()
            page.wait_for_timeout(3500)

        nav_page("⚽ Jogar Rodada", "05_jogar.png", depois=simular)
        nav_page("🏆 Classificação", "06_classificacao.png")
        nav_page("🏪 Mercado", "07_mercado.png")
        nav_page("📰 Notícias", "08_noticias.png")

        nav.close()
        print("screenshots salvos em", SAIDA)


if __name__ == "__main__":
    sys.exit(main())
