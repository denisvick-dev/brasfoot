"""
Escudos dos clubes.

As imagens ficam em ``assets/escudos`` com o nome da sigla do clube:

* ``<SIGLA>.png`` — escudo oficial (usado quando existe);
* ``<SIGLA>.svg`` — escudo em vetor (importado ou gerado por
  ``scripts/gerar_escudos.py`` para os clubes sem imagem).

O app precisa que a imagem viaje junto com o HTML (``st.markdown`` com
``unsafe_allow_html``), então o arquivo é embutido como *data URI* — nada de
servidor de estáticos. Como o mesmo escudo aparece em várias tabelas, o data
URI fica em cache.

Uso
---
>>> from game.escudos import imagem
>>> imagem("FLA", "🔴⚫")        # <img class="escudo" src="data:image/png;base64,...">
>>> tem_escudo("FLA"), tem_escudo("XYZ")
(True, False)
"""

from functools import cache
from pathlib import Path

DIRETORIO = Path(__file__).resolve().parent.parent / "assets" / "escudos"

_EXTENSOES = (".png", ".svg")
_MIME = {".png": "image/png", ".svg": "image/svg+xml"}


@cache
def caminho(sigla: str) -> Path | None:
    """Caminho do arquivo de escudo da sigla (``None`` se não houver)."""
    alvo = str(sigla).strip().upper()
    if not alvo:
        return None
    for ext in _EXTENSOES:
        arquivo = DIRETORIO / f"{alvo}{ext}"
        if arquivo.is_file():
            return arquivo
    return None


def tem_escudo(sigla: str) -> bool:
    """``True`` se o clube tem imagem de escudo."""
    return caminho(sigla) is not None


@cache
def data_uri(sigla: str) -> str | None:
    """Escudo embutido como data URI (``None`` se não houver imagem)."""
    arquivo = caminho(sigla)
    if arquivo is None:
        return None
    import base64

    mime = _MIME[arquivo.suffix]
    dados = base64.b64encode(arquivo.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{dados}"


def imagem(sigla: str, emoji: str = "", classe: str = "escudo") -> str:
    """
    HTML do escudo.

    Sem imagem cadastrada devolve o emoji (ou string vazia) — assim clubes
    criados pelo jogador continuam com alguma representação visual.
    """
    uri = data_uri(sigla)
    if uri is None:
        return emoji
    return f'<img class="{classe}" src="{uri}" alt="Escudo {sigla}" loading="lazy">'


def disponiveis() -> int:
    """Quantos clubes do banco têm escudo."""
    from game.clubes import TIMES_DATA

    return sum(1 for c in TIMES_DATA if tem_escudo(c.sigla))


def faltando() -> list[str]:
    """Siglas de clubes do banco que ficaram sem arquivo em ``assets/escudos``."""
    from game.clubes import TIMES_DATA

    return sorted({c.sigla for c in TIMES_DATA if not tem_escudo(c.sigla)})


def orfaos() -> list[str]:
    """Arquivos de ``assets/escudos`` cujo nome não é a sigla de nenhum clube."""
    from game.clubes import TIMES_DATA

    siglas = {c.sigla for c in TIMES_DATA}
    return sorted(
        {
            arquivo.stem
            for arquivo in DIRETORIO.iterdir()
            if arquivo.suffix in _EXTENSOES and arquivo.stem not in siglas
        }
    )
