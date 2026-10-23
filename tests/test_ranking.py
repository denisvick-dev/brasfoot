"""Ranking de pontos acumulados entre temporadas."""

from game.banco_dados import criar_times
from game.ranking import LinhaRanking, Ranking, ranking_da_temporada


def _linha(ranking: Ranking, clube: str) -> LinhaRanking:
    """Linha do clube no ranking (falha o teste se ele não estiver lá)."""
    linha = ranking.linha(clube)
    assert linha is not None, clube
    return linha


def _jogar_temporada(times):
    """Dá a cada clube uma campanha (pontos = 3 por vitória) sem simular."""
    for indice, time in enumerate(times):
        time.jogos_campeonato = 10
        time.vitorias = 6 - indice % 4
        time.empates = 2
        time.derrotas = 10 - time.vitorias - time.empates
        time.pontos = 3 * time.vitorias + time.empates
        time.gols_pro = 20 - indice
        time.gols_contra = 10 + indice


def test_ranking_comeca_vazio():
    ranking = Ranking()
    assert ranking.vazio
    assert ranking.ordenar() == []
    assert ranking.posicao("Flamengo") is None
    assert "vazio" in ranking.resumo()


def test_registrar_temporada_soma_a_campanha_dos_clubes():
    times = criar_times(8, semente=3)
    _jogar_temporada(times)
    esperado = sum(t.pontos for t in times)

    ranking = Ranking()
    assert ranking.registrar_temporada(2026, times, campeao=times[0])

    assert len(ranking.linhas) == 8
    assert sum(linha.pontos for linha in ranking.linhas.values()) == esperado
    linha = _linha(ranking, times[0].nome)
    assert linha.temporadas == 1
    assert linha.jogos == 10
    assert linha.titulos == 1
    assert ranking.total_temporadas == 1
    ultima = ranking.ultima_temporada()
    assert ultima is not None
    assert ultima.campeao == times[0].nome


def test_temporada_repetida_nao_dobra_a_pontuacao():
    times = criar_times(8, semente=3)
    _jogar_temporada(times)
    ranking = Ranking()

    assert ranking.registrar_temporada(2026, times) is True
    pontos = _linha(ranking, times[0].nome).pontos
    assert ranking.registrar_temporada(2026, times) is False
    assert _linha(ranking, times[0].nome).pontos == pontos
    assert ranking.total_temporadas == 1


def test_duas_temporadas_acumulam():
    times = criar_times(8, semente=3)
    ranking = Ranking()
    _jogar_temporada(times)
    ranking.registrar_temporada(2026, times)
    pontos_1 = _linha(ranking, times[0].nome).pontos
    _jogar_temporada(times)
    ranking.registrar_temporada(2027, times)

    linha = _linha(ranking, times[0].nome)
    assert linha.temporadas == 2
    assert linha.pontos == 2 * pontos_1
    assert ranking.total_temporadas == 2


def test_ordenacao_usa_os_criterios_do_brasileirao():
    times = criar_times(4, semente=3)
    ranking = Ranking()
    # todos com 10 pts; desempate por vitórias e depois saldo
    cenarios = [
        (5, 30, 20),  # 5 vitórias, saldo +10
        (5, 40, 20),  # 5 vitórias, saldo +20
        (4, 12, 8),  # 4 vitórias, saldo +4
        (3, 14, 0),  # 3 vitórias, saldo +14
    ]
    for time, (vitorias, gols_pro, gols_contra) in zip(times, cenarios, strict=True):
        time.jogos_campeonato = 10
        time.vitorias = vitorias
        time.pontos = 10
        time.gols_pro = gols_pro
        time.gols_contra = gols_contra
    ranking.registrar_temporada(2026, times)

    ordem = [linha.clube for linha in ranking.ordenar()]
    assert ordem == [times[1].nome, times[0].nome, times[2].nome, times[3].nome]
    assert ranking.posicao(times[1].nome) == 1
    assert ranking.top(1)[0].clube == times[1].nome


def test_titulos_copas_regionais_acessos_e_rebaixamentos():
    times = criar_times(8, semente=3)
    _jogar_temporada(times)
    ranking = Ranking()
    ranking.registrar_temporada(
        2026,
        times,
        campeao=times[0],
        campeao_copa=times[1],
        campeoes_regionais=[times[2], times[3]],
        acessos=[times[4].nome],
        rebaixados=[times[5].nome],
    )
    assert _linha(ranking, times[0].nome).titulos == 1
    assert _linha(ranking, times[1].nome).copas == 1
    assert _linha(ranking, times[2].nome).regionais == 1
    assert _linha(ranking, times[4].nome).acessos == 1
    assert _linha(ranking, times[5].nome).rebaixamentos == 1


def test_aproveitamento_e_media_por_temporada():
    times = criar_times(2, semente=3)
    ranking = Ranking()
    for time in times:
        time.jogos_campeonato = 10
        time.vitorias = 5
        time.pontos = 15
    ranking.registrar_temporada(2026, times)

    linha = _linha(ranking, times[0].nome)
    assert linha.aproveitamento == 50.0  # 15 de 30 pontos disputados
    assert linha.media_pontos == 15.0
    assert linha.saldo_gols == 0


def test_clube_sem_jogo_nao_entra_no_ranking():
    times = criar_times(4, semente=3)
    for time in times:
        time.jogos_campeonato = 0
    ranking = Ranking()
    assert ranking.registrar_temporada(2026, times) is False
    assert ranking.vazio


def test_registrar_posicoes_guarda_a_melhor_colocacao():
    times = criar_times(4, semente=3)
    _jogar_temporada(times)
    ranking = Ranking()
    ranking.registrar_temporada(2026, times)
    ranking.registrar_posicoes(2026, {times[0].nome: 5, times[1].nome: 2})
    assert _linha(ranking, times[1].nome).melhor_posicao == 2
    assert _linha(ranking, times[0].nome).melhor_posicao == 5


def test_ranking_da_temporada_ordena_por_pontos():
    times = criar_times(6, semente=3)
    _jogar_temporada(times)
    ordenados = ranking_da_temporada(times)
    assert len(ordenados) == 6
    pontos = [t.pontos for t in ordenados]
    assert pontos == sorted(pontos, reverse=True)


def test_ranking_da_temporada_ignora_quem_nao_jogou():
    times = criar_times(4, semente=3)
    assert ranking_da_temporada(times) == []
