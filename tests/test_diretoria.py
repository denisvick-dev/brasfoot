"""Objetivo da diretoria."""

from game.diretoria import METAS, cor_da_situacao, objetivo_do_time
from game.modelos import Time


def _time(divisao: str) -> Time:
    time = Time(
        id=1,
        nome="Teste",
        sigla="TST",
        cidade="Lugar",
        estado="SP",
        cor_primaria="#16A34A",
        cor_secundaria="#FFFFFF",
        escudo_emoji="⚽",
    )
    time.divisao = divisao
    return time


def test_todas_as_divisoes_tem_meta():
    assert set(METAS) == {"A", "B", "C", "D"}


def test_objetivo_usa_a_divisao_do_time():
    for divisao in "ABCD":
        objetivo = objetivo_do_time(_time(divisao))
        assert objetivo.divisao == divisao
        assert objetivo.descricao == METAS[divisao][0]


def test_situacao_da_meta():
    objetivo = objetivo_do_time(_time("B"))
    assert objetivo.cumprido(3)
    assert not objetivo.cumprido(5)
    assert objetivo.situacao(0) == "Temporada ainda não começou"
    assert objetivo.situacao(1) == "Meta encaminhada"
    assert objetivo.situacao(6) == "Em risco"
    assert objetivo.situacao(18) == "Abaixo do esperado"


def test_cores_por_situacao():
    assert cor_da_situacao("Meta encaminhada") == "#16A34A"
    assert cor_da_situacao("Em risco") == "#D97706"
    assert cor_da_situacao("Abaixo do esperado") == "#DC2626"
