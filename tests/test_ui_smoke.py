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
    at.session_state["velocidade_rodada"] = "⏩ Rápida"  # relógio curto no teste
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

    # o relógio da rodada rodou: o painel "ao vivo" foi desenhado
    assert any("av-relogio" in m.value for m in at.markdown)
    textos = [m.value for m in at.markdown] + [c.value for c in at.caption]
    assert any("Sorteio #" in texto for texto in textos)

    sorteio = at.session_state["sorteio_rodada"]
    assert isinstance(sorteio, int) and sorteio >= 0


def test_cada_rodada_sorteia_resultados_novos():
    """Aleatoriedade de jogos: simular de novo sorteia outro placar."""
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
    at.session_state["velocidade_rodada"] = "⏩ Rápida"
    at.run()

    resultados = []
    sorteios = []
    for _ in range(2):
        next(b for b in at.button if "SIMULAR" in b.label).click()
        at.run()
        assert not at.exception
        sorteios.append(at.session_state["sorteio_rodada"])
        resultados.append(
            tuple(
                (p.time_casa, p.gols_casa, p.gols_fora)
                for jogos in at.session_state["placares_rodada"].values()
                for p in jogos
            )
        )

    assert sorteios[0] != sorteios[1], "cada rodada precisa de um sorteio novo"
    assert resultados[0] != resultados[1], "as rodadas não podem repetir placares"


def _app_na_rodada(velocidade: str = "⏩ Rápida", som: bool = True) -> AppTest:
    """App na tela de jogo, com 20 clubes, pronto para simular uma rodada."""
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
    at.session_state["velocidade_rodada"] = velocidade
    at.session_state["som_de_gol"] = som
    at.run()
    return at


def test_tela_de_jogo_tem_controle_de_som():
    at = _app_na_rodada()
    assert not at.exception
    rotulos = [c.label for c in at.checkbox]
    assert any("Som de gol" in rotulo for rotulo in rotulos)


def test_gol_toca_som_e_pisca_no_quadro_do_lance(monkeypatch):
    """Durante a rodada, o quadro do gol recebe o áudio e a classe do pisca."""
    import ui.jogar as jogar

    quadros: list[tuple[int, str]] = []
    original = jogar.html_ao_vivo

    def espiao(placares, minuto, **kwargs):
        quadros.append((minuto, kwargs.get("som", "")))
        return original(placares, minuto, **kwargs)

    monkeypatch.setattr(jogar, "html_ao_vivo", espiao)

    at = _app_na_rodada(som=True)
    next(b for b in at.button if "SIMULAR" in b.label).click()
    at.run()
    assert not at.exception

    com_som = [minuto for minuto, som in quadros if som]
    assert com_som, "algum quadro da rodada precisa tocar o som de gol"
    assert all(som.startswith("data:audio/wav;base64,") for _, som in quadros if som)
    # o som não toca em todo quadro: só quando sai gol
    assert len(com_som) < len(quadros)

    # o pisca vermelho aparece no HTML do quadro do gol (e some depois)
    from ui.ao_vivo import JANELA_FLASH

    placares = at.session_state["placares_rodada"]
    minutos_de_gol = [
        gol.minuto
        for jogos in placares.values()
        for partida in jogos
        for gol in partida.gols
    ]
    assert minutos_de_gol, "a rodada precisa ter algum gol"
    assert "gol-agora" in original(placares, minutos_de_gol[0], rodada=1)
    depois = max(minutos_de_gol) + JANELA_FLASH + 1
    assert "gol-agora" not in original(placares, depois, rodada=1)


def test_sem_som_ligado_nao_embute_audio(monkeypatch):
    import ui.jogar as jogar

    quadros: list[str] = []
    original = jogar.html_ao_vivo

    def espiao(placares, minuto, **kwargs):
        quadros.append(kwargs.get("som", ""))
        return original(placares, minuto, **kwargs)

    monkeypatch.setattr(jogar, "html_ao_vivo", espiao)

    at = _app_na_rodada(som=False)
    next(b for b in at.button if "SIMULAR" in b.label).click()
    at.run()
    assert not at.exception
    assert quadros and not any(quadros)
