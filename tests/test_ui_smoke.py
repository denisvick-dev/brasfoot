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
    "financas",
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


def test_rodada_mostra_barra_e_todos_os_placares():
    """Simular a rodada guarda os placares de todas as competições da rodada."""
    from game.banco_dados import criar_times
    from game.campeonato import League

    times = criar_times(20, semente=3)
    at = AppTest.from_file(str(APP), default_timeout=1800)
    at.session_state["game_started"] = True
    at.session_state["times"] = times
    at.session_state["league"] = League(times)
    at.session_state["meu_time"] = times[0].nome
    at.session_state["piramide"] = None
    at.session_state["pagina"] = "jogar"
    at.run()
    assert not at.exception

    botao = next(b for b in at.button if "SIMULAR" in b.label)
    botao.click()
    at.run()
    assert not at.exception

    placares = at.session_state["placares_rodada"]
    assert placares, "a rodada simulada precisa guardar os placares"
    assert sum(len(jogos) for jogos in placares.values()) == 10  # 20 clubes
    assert any("Placares da rodada" in m.value for m in at.markdown)
