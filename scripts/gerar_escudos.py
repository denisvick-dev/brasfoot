"""
Gera escudos genéricos (SVG) para os clubes que ainda não têm imagem.

O banco usa ``assets/escudos/<SIGLA>.png`` (escudos reais) e cai para
``<SIGLA>.svg`` quando não há PNG. Este script desenha o SVG de quem não tem
nenhum dos dois: um escudo em duas cores do clube com a sigla no meio, no
estilo "escudo genérico" dos jogos de futebol.

Rodar da raiz do projeto::

    python scripts/gerar_escudos.py            # só os que faltam
    python scripts/gerar_escudos.py --forcar   # refaz todos os genéricos
"""

import argparse
import sys
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from game.clubes import TIMES_DATA, Clube

DIRETORIO = RAIZ / "assets" / "escudos"

# contorno clássico de escudo (viewBox 0 0 100 120)
ESCUDO = "M8 4 H92 V62 C92 90 74 108 50 117 C26 108 8 90 8 62 Z"
METADE = "M50 4 H92 V62 C92 90 74 108 50 117 Z"  # metade direita (2ª cor)
FAIXA_Y, FAIXA_H = 52, 30  # faixa escura onde a sigla fica legível


def _luminancia(cor: str) -> float:
    """Luminância relativa (0 = preto, 1 = branco) de uma cor ``#RRGGBB``."""
    cor = cor.lstrip("#")
    if len(cor) != 6:
        return 0.5
    r, g, b = (int(cor[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def svg_generico(clube: Clube) -> str:
    """Escudo genérico do clube em SVG (duas cores + faixa com a sigla)."""
    cor1, cor2 = clube.cor1, clube.cor2
    if cor1.lower() == cor2.lower():
        cor2 = "#FFFFFF" if _luminancia(cor1) < 0.5 else "#212121"
    sigla = escape(clube.sigla[:4])
    # a sigla precisa caber na parte do escudo que estreita: diminui com o tamanho
    tamanho = {2: 34, 3: 28, 4: 22}.get(len(clube.sigla), 20)
    fonte = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120" '
        f'width="100" height="120" role="img" data-generico="1" '
        f'aria-label="Escudo do {escape(clube.nome)}">'
        f"<title>{escape(clube.nome)}</title>"
        f'<clipPath id="escudo"><path d="{ESCUDO}"/></clipPath>'
        f'<g clip-path="url(#escudo)">'
        f'<path d="{ESCUDO}" fill="{cor1}"/>'
        f'<path d="{METADE}" fill="{cor2}"/>'
        f'<rect x="0" y="{FAIXA_Y}" width="100" height="{FAIXA_H}" fill="#1A1A1A" fill-opacity=".62"/>'
        f'<text x="50" y="{FAIXA_Y + FAIXA_H // 2 + tamanho // 3}" text-anchor="middle"'
        f' font-family="{fonte}" font-size="{tamanho}" font-weight="700" letter-spacing="0.5"'
        f' fill="#FFFFFF">{sigla}</text>'
        "</g>"
        f'<path d="{ESCUDO}" fill="none" stroke="#212121" stroke-opacity=".5" stroke-width="3"/>'
        "</svg>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--forcar",
        action="store_true",
        help="refaz só os SVGs genéricos (não toca nos escudos reais)",
    )
    args = parser.parse_args()

    DIRETORIO.mkdir(parents=True, exist_ok=True)
    criados, pulados = 0, 0
    for clube in TIMES_DATA:
        png = DIRETORIO / f"{clube.sigla}.png"
        svg = DIRETORIO / f"{clube.sigla}.svg"
        if png.exists():
            continue  # escudo real: não sobrescreve
        if svg.exists():
            # não sobrescreve escudo real em SVG: só refaz os genéricos
            generico = 'data-generico="1"' in svg.read_text(encoding="utf-8")
            if not (args.forcar and generico):
                pulados += 1
                continue
        svg.write_text(svg_generico(clube), encoding="utf-8")
        criados += 1

    print(f"Escudos genéricos criados: {criados} · já existentes: {pulados}")
    faltando = [c.nome for c in TIMES_DATA if not _tem_arquivo(c.sigla)]
    if faltando:  # pragma: no cover - só acontece se a escrita falhar
        print("Sem escudo:", ", ".join(faltando))


def _tem_arquivo(sigla: str) -> bool:
    return any((DIRETORIO / f"{sigla}{ext}").exists() for ext in (".png", ".svg"))


if __name__ == "__main__":
    main()
