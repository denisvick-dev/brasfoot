"""Rodada ao vivo: relógio, placares revelados por minuto e sorteio da rodada."""

from game.jogo_engine import MatchEngine
from game.modelos import Gol, Partida
from ui.ao_vivo import (
    VELOCIDADES,
    gols_do_minuto,
    html_ao_vivo,
    linha_placar,
    minuto_final,
    passos,
    quadro,
    relogio,
    total_de_jogos,
    ultimo_gol,
)


def _partida_com_gols(casa: str, fora: str, gols: list[tuple[int, str]]) -> Partida:
    partida = Partida(rodada=1, time_casa=casa, time_fora=fora, jogada=True)
    for minuto, time in gols:
        partida.gols.append(Gol(minuto=minuto, time=time, jogador=f"Jogador {minuto}"))
    partida.gols_casa = sum(1 for _, t in gols if t == casa)
    partida.gols_fora = sum(1 for _, t in gols if t == fora)
    return partida


def test_relogio_mostra_acrescimos():
    assert relogio(0) == "0'"
    assert relogio(45) == "45'"
    assert relogio(90) == "90'"
    assert relogio(93) == "90+3'"


def test_passos_comecam_no_zero_e_terminam_no_ultimo_minuto():
    marcos = passos(90)
    assert marcos[0] == 0
    assert marcos[-1] == 90
    assert marcos == sorted(marcos)
    # acréscimo entra no último passo
    assert passos(93)[-1] == 93


def test_placar_aparece_aos_poucos_conforme_o_minuto():
    partida = _partida_com_gols("FLA", "PAL", [(12, "FLA"), (55, "PAL"), (88, "FLA")])
    placares = {"Série A": [partida]}

    assert minuto_final(placares) == 90  # fim regulamentar, mesmo sem gol no 90
    assert partida.placar_ate(0) == (0, 0)
    assert partida.placar_ate(12) == (1, 0)
    assert partida.placar_ate(54) == (1, 0)
    assert partida.placar_ate(55) == (1, 1)
    assert partida.placar_ate(90) == (2, 1)

    quadro_12 = quadro(placares, 12)
    assert quadro_12["Série A"][0][1:] == (1, 0)


def test_minuto_final_respeita_acrescimo():
    partida = _partida_com_gols("FLA", "PAL", [(92, "FLA")])
    assert minuto_final({"Série A": [partida]}) == 92


def test_gols_do_minuto_e_ultimo_gol():
    partida = _partida_com_gols("FLA", "PAL", [(10, "FLA"), (30, "PAL"), (30, "FLA")])
    placares = {"Série A": [partida]}

    assert len(gols_do_minuto(placares, 30)) == 2
    assert gols_do_minuto(placares, 11) == []
    assert ultimo_gol(partida, 29) is not None
    assert ultimo_gol(partida, 5) is None


def test_quadro_ignora_jogo_que_nao_aconteceu():
    nao_jogada = Partida(rodada=1, time_casa="FLA", time_fora="PAL")
    assert quadro({"Série A": [nao_jogada]}, 0) == {}
    assert total_de_jogos({"Série A": [nao_jogada]}) == 1


def test_html_ao_vivo_tem_relogio_destaque_e_demais_jogos():
    minha = _partida_com_gols("FLA", "PAL", [(20, "FLA")])
    outra = _partida_com_gols("VAS", "FLU", [(70, "FLU")])
    placares = {"Série A": [minha, outra]}

    html = html_ao_vivo(
        placares, 30, meu_time="FLA", rodada=7, sorteio=0xABCDEF, final=90
    )
    assert "av-relogio" in html and "30'" in html
    assert "Sorteio #abcdef" in html
    assert "Rodada 7 · 2 jogos" in html
    assert "av-destaque" in html  # o jogo do clube do jogador
    assert "Jogador 20" in html  # último gol até o minuto
    # o jogo do jogador não se repete na lista dos "outros"
    assert "VAS" in html and html.count("FLA") == 1


def test_linha_placar_destaca_e_mostra_placar_parcial():
    partida = _partida_com_gols("FLA", "PAL", [(5, "PAL")])
    html = linha_placar(partida, 0, 1, destaque=True)
    assert "placar-linha destaque" in html
    assert ">0<i>x</i>1<" in html


def test_engine_guarda_os_gols_com_minuto():
    """O replay depende disto: cada gol com autor, clube e minuto."""
    from game.banco_dados import criar_times

    times = criar_times(8, semente=3)
    engine = MatchEngine()
    partida = engine.simular(times[0], times[1], rodada=1)

    assert len(partida.gols) == partida.gols_casa + partida.gols_fora
    assert all(1 <= gol.minuto <= 95 for gol in partida.gols)
    assert all(
        gol.time in (partida.time_casa, partida.time_fora) for gol in partida.gols
    )
    # a soma dos gols por clube bate com o placar
    assert partida.placar_ate(95) == (partida.gols_casa, partida.gols_fora)


def test_velocidades_disponiveis():
    assert VELOCIDADES
    assert all(segundos > 0 for segundos in VELOCIDADES.values())
