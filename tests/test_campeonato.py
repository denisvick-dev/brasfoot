"""League: calendário, rodadas e classificação."""

import pytest

from game.campeonato import League


def test_liga_precisa_de_dois_times(times8):
    with pytest.raises(ValueError):
        League(times8[:1])


def test_calendario_tem_todos_contra_todos(times8):
    liga = League(times8)
    jogos = [par for rodada in liga.calendario for par in rodada]
    assert len(jogos) == 8 * 7
    assert len(liga.calendario) == liga.total_rodadas


def test_simular_rodada_distribui_pontos(times8):
    liga = League(times8)
    jogos = liga.simular_rodada("")
    assert len(jogos) == 4
    pontos = sum(t.pontos for t in times8)
    # cada jogo distribui 3 pontos (vitória) ou 2 (empate)
    assert 4 * 2 <= pontos <= 4 * 3
    assert liga.rodada_atual == 1


def test_classificacao_ordena_por_pontos_e_saldo(times8):
    liga = League(times8)
    for _ in range(3):
        liga.simular_rodada("")
    tabela = liga.classificacao
    assert len(tabela) == 8
    chaves = [(t.pontos, t.saldo_gols) for t in tabela]
    assert chaves == sorted(chaves, reverse=True)


def test_artilharia_ordenada(times8):
    liga = League(times8)
    for _ in range(5):
        liga.simular_rodada("")
    art = liga.artilharia(top=5)
    assert len(art) <= 5
    gols = [j.gols for j, _ in art]
    assert gols == sorted(gols, reverse=True)
