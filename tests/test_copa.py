"""Copa do Brasil."""

import pytest

from game.copa import CopaBrasil


def test_copa_precisa_de_quatro_clubes(times8):
    with pytest.raises(ValueError):
        CopaBrasil(times8[:3])


def test_copa_usa_128_clubes(banco):
    copa = CopaBrasil(banco, semente=1)
    assert len(copa.times) == 128
    assert len(copa.times) == len(set(t.nome for t in copa.times))


def test_copa_arredonda_para_potencia_de_dois(times8):
    copa = CopaBrasil(times8, semente=1)
    assert len(copa.times) == 8


def test_copa_tem_campeao_ao_final(banco):
    copa = CopaBrasil(banco, temporada=2026, semente=2)
    for rodada in range(0, 400):
        copa.simular_rodada_global(rodada)
        if copa.encerrada:
            break
    assert copa.encerrada
    assert copa.campeao is not None
    assert copa.campeao.nome in {t.nome for t in copa.times}
    assert copa.vice is not None and copa.vice is not copa.campeao
