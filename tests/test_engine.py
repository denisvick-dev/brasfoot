"""Motor de simulação."""

from game.jogo_engine import MatchEngine


def test_partida_gera_placar_e_eventos(times8):
    engine = MatchEngine()
    partida = engine.simular(times8[0], times8[1], rodada=1)
    assert partida.gols_casa >= 0 and partida.gols_fora >= 0
    assert partida.jogada
    assert partida.eventos
    assert partida.publico > 0


def test_mando_de_campo_entra_nas_forcas(times8):
    """O bônus de casa é uma regra do motor, não sorte: dá para checar direto."""
    engine = MatchEngine()
    time = times8[0]

    assert engine._calcular_forca(time, casa=True) > engine._calcular_forca(
        time, casa=False
    )
    assert engine._forca_ataque(time, casa=True) > engine._forca_ataque(
        time, casa=False
    )
    assert engine._forca_defesa(time, casa=True) > engine._forca_defesa(
        time, casa=False
    )


def test_mando_de_campo_aparece_no_placar(banco):
    """Em muitos jogos, o mandante soma mais gols e mais vitórias que o visitante.

    Cada confronto é jogado nos dois sentidos (A×B e B×A), então a diferença de
    força entre os clubes se anula e sobra só o mando de campo. O número de
    jogos é alto de propósito: com 400 partidas a margem fica folgada em
    qualquer semente (ver `tests/conftest.py`).
    """
    engine = MatchEngine()
    gols_casa = gols_fora = vitorias_casa = vitorias_fora = 0

    for i in range(200):
        a, b = banco[i % 20], banco[(i * 7 + 5) % 20]
        for casa, fora in ((a, b), (b, a)):
            partida = engine.simular(casa, fora, rodada=1)
            gols_casa += partida.gols_casa
            gols_fora += partida.gols_fora
            if partida.gols_casa > partida.gols_fora:
                vitorias_casa += 1
            elif partida.gols_fora > partida.gols_casa:
                vitorias_fora += 1

    assert gols_casa > gols_fora, f"gols {gols_casa} x {gols_fora}"
    assert vitorias_casa > vitorias_fora, f"vitórias {vitorias_casa} x {vitorias_fora}"


def test_publico_respeita_capacidade(times8):
    engine = MatchEngine()
    for time in times8:
        publico = engine._calcular_publico(time)
        assert 0 < publico <= time.capacidade


def test_cartoes_suspendem_jogador(times8):
    engine = MatchEngine()
    for _ in range(40):
        engine.simular(times8[2], times8[3], rodada=1)
    amarelos = sum(j.cartoes_amarelos for t in times8 for j in t.jogadores)
    assert amarelos > 0
    # Três amarelos (ou um vermelho) tiram o jogador da rodada seguinte.
    for time in times8:
        for jogador in time.jogadores:
            esperado = jogador.cartoes_amarelos >= 3 or jogador.cartoes_vermelhos > 0
            assert jogador.suspenso == esperado, jogador.nome
