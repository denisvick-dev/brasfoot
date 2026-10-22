"""Smoke test das telas: o app precisa montar sem exceção."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app.py"

PAGINAS = [
    "painel",
    "elenco",
    "tatica",
    "jogar",
    "classificacao",
    "calendario",
    "resultados",
    "mercado",
    "noticias",
    "criador",
]


def test_app_abre_na_tela_inicial():
    at = AppTest.from_file(str(APP), default_timeout=1800).run()
    assert not at.exception


def test_todas_as_telas_montam():
    at = AppTest.from_file(str(APP), default_timeout=1800).run()
    for pagina in PAGINAS:
        at.session_state["pagina"] = pagina
        at.run()
        assert not at.exception, pagina
