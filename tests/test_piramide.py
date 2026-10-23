"""Pirâmide: quatro divisões, acesso/descenso, copa e regionais."""

import pytest

from game.piramide import Piramide


@pytest.fixture
def piramide(times8):
    return Piramide(times8, temporada=2026)


def test_tem_as_quatro_divisoes_quando_ha_clubes(banco):
    p = Piramide(banco, temporada=2026)
    assert set(p.divisoes) == {"A", "B", "C", "D"}
    assert p.copa is not None
    assert len(p.regionais) >= 1


def test_temporada_termina_e_tem_campeao(piramide):
    for _ in range(piramide.total_rodadas_global):
        piramide.simular_rodada("")
    assert piramide.encerrada
    assert piramide.league("A").campeao is not None
    assert piramide.resumo()


def test_nova_temporada_reinicia(piramide):
    for _ in range(piramide.total_rodadas_global):
        piramide.simular_rodada("")
    temporada = piramide.temporada
    piramide.nova_temporada()
    assert piramide.temporada == temporada + 1
    assert not piramide.encerrada
    assert piramide.rodada("A") == 0


def test_acesso_e_descenso_entre_series(banco):
    p = Piramide(banco, temporada=2026)
    antes = {t.nome: t.divisao for t in p.times}
    for _ in range(p.total_rodadas_global):
        p.simular_rodada("")
    p.nova_temporada()
    depois = {t.nome: t.divisao for t in p.times}
    subiram = [n for n in antes if depois[n] < antes[n]]
    cairam = [n for n in antes if depois[n] > antes[n]]
    assert subiram and cairam


def test_piramide_precisa_de_clubes():
    with pytest.raises(ValueError):
        Piramide([])


def test_supercopa_sai_da_agenda_depois_de_disputada(banco):
    """Depois da Supercopa o clube não tem 'próximo jogo' — a temporada fechou."""
    p = Piramide(banco, temporada=2026)
    p.simular_restante()

    if p.supercopa is None or p.supercopa_times is None:
        return  # cenário sem Supercopa: nada a checar

    casa, fora = p.supercopa_times
    for clube in (casa, fora):
        assert p.proximo_jogo(clube.nome) is None
