"""Progresso da simulação (barra de carregamento)."""

from game.campeonato import League
from game.piramide import Piramide


def test_piramide_avisa_o_progresso_por_competicao(banco):
    piramide = Piramide(banco, temporada=2026)
    chamadas: list[tuple[float, str]] = []

    piramide.simular_rodada("", progresso=lambda f, r: chamadas.append((f, r)))

    assert chamadas, "a interface precisa ser avisada ao menos uma vez"
    fracoes = [f for f, _ in chamadas]
    assert fracoes == sorted(fracoes), "o progresso não pode voltar"
    assert all(0.0 <= f <= 1.0 for f in fracoes)
    assert all(rotulo for _, rotulo in chamadas)


def test_piramide_sem_callback_continua_funcionando(banco):
    piramide = Piramide(banco, temporada=2026)
    jogos = piramide.simular_rodada("")
    assert jogos
    assert piramide.rodada_global == 1


def test_league_avisa_jogo_a_jogo(times8):
    liga = League(times8)
    chamadas: list[tuple[float, str]] = []

    liga.simular_rodada("", progresso=lambda f, r: chamadas.append((f, r)))

    assert len(chamadas) == 4  # 4 jogos na rodada
    assert chamadas[-1][0] == 1.0
    assert " x " in chamadas[0][1]
