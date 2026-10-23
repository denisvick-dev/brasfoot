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


def test_classificacao_ordena_pelos_criterios_do_brasileirao(times8):
    """Pontos → vitórias → saldo → gols pró, como no regulamento."""
    liga = League(times8)
    for _ in range(3):
        liga.simular_rodada("")
    tabela = liga.classificacao
    assert len(tabela) == 8
    chaves = [(t.pontos, t.vitorias, t.saldo_gols, t.gols_pro) for t in tabela]
    assert chaves == sorted(chaves, reverse=True)


def test_empate_em_pontos_desempata_por_vitorias_depois_por_saldo(times8):
    """Com os mesmos pontos, mais vitórias vem antes — mesmo com saldo pior."""
    alvo = times8[:4]
    # (pontos, vitórias, gols pró, gols contra) → saldo = pró − contra
    pontos = (9, 9, 9, 9)
    vitorias = (3, 3, 2, 2)
    gols_pro = (4, 2, 8, 6)
    gols_contra = (3, 3, 5, 3)
    for time, p, v, gp, gc in zip(alvo, pontos, vitorias, gols_pro, gols_contra, strict=True):
        time.pontos, time.vitorias = p, v
        time.gols_pro = gp
        time.gols_contra = gc

    # saldos: 1, -1, 3, 3
    assert [t.saldo_gols for t in alvo] == [1, -1, 3, 3]

    liga = League(times8)
    nomes = [t.nome for t in liga.classificacao]
    # 3 vitórias passa na frente de 2 vitórias, ainda que o saldo seja menor.
    assert nomes.index(alvo[1].nome) < nomes.index(alvo[2].nome)
    # Entre os "3 vitórias", melhor saldo primeiro.
    assert nomes.index(alvo[0].nome) < nomes.index(alvo[1].nome)
    # Empate em pontos, vitórias e saldo: mais gols pró primeiro.
    assert nomes.index(alvo[2].nome) < nomes.index(alvo[3].nome)


def test_artilharia_ordenada(times8):
    liga = League(times8)
    for _ in range(5):
        liga.simular_rodada("")
    art = liga.artilharia(top=5)
    assert len(art) <= 5
    gols = [j.gols for j, _ in art]
    assert gols == sorted(gols, reverse=True)
