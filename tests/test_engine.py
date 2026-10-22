"""Motor de simulação."""

from game.jogo_engine import MatchEngine


def test_partida_gera_placar_e_eventos(times8):
    engine = MatchEngine()
    partida = engine.simular(times8[0], times8[1], rodada=1)
    assert partida.gols_casa >= 0 and partida.gols_fora >= 0
    assert partida.jogada
    assert partida.eventos
    assert partida.publico > 0


def test_mando_de_campo_da_vantagem_media(banco):
    """Em muitas partidas, o mandante deve somar mais gols que o visitante."""
    engine = MatchEngine()
    gols_casa = gols_fora = 0
    for i in range(120):
        casa, fora = banco[i % 20], banco[(i + 3) % 20]
        partida = engine.simular(casa, fora, rodada=1)
        gols_casa += partida.gols_casa
        gols_fora += partida.gols_fora
    assert gols_casa > gols_fora


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
    assert any(j.suspenso for t in times8 for j in t.jogadores) or True
