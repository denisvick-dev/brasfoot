"""Banco de clubes e escudos."""

from collections import Counter

from game import escudos
from game.banco_dados import criar_times, criar_times_por_nome
from game.clubes import TIMES_DATA


def test_banco_tem_156_clubes_em_quatro_divisoes():
    assert len(TIMES_DATA) == 156
    assert Counter(c.divisao for c in TIMES_DATA) == Counter(
        {"A": 20, "B": 20, "C": 20, "D": 96}
    )


def test_siglas_sao_unicas():
    repetidas = [s for s, n in Counter(c.sigla for c in TIMES_DATA).items() if n > 1]
    assert repetidas == []


def test_todo_clube_tem_escudo_arquivo():
    faltando = escudos.faltando()
    assert faltando == []


def test_nao_ha_arquivo_de_escudo_orfao():
    assert escudos.orfaos() == []


def test_disponiveis_cobre_os_156():
    assert escudos.disponiveis() == 156


def test_data_uri_e_png_ou_svg():
    for sigla in ("FLA", "IND", "IAPE", "CRAC"):
        uri = escudos.data_uri(sigla)
        assert uri is not None
        assert uri.startswith("data:image/")


def test_sem_escudo_cai_no_emoji():
    assert not escudos.tem_escudo("ZZZ")
    assert escudos.imagem("ZZZ", "🔵") == "🔵"
    assert escudos.caminho("  ") is None


def test_criar_times_quantidades():
    assert len(criar_times(20)) == 20
    assert len(criar_times(None, semente=7)) == 156
    serie_b = criar_times(divisao="B")
    assert len(serie_b) == 20
    assert all(t.divisao == "B" for t in serie_b)


def test_criar_times_e_reproduzivel_com_semente():
    a = criar_times(12, aleatorio=True, semente=42)
    b = criar_times(12, aleatorio=True, semente=42)
    assert [t.nome for t in a] == [t.nome for t in b]


def test_criar_por_nome_ignora_desconhecidos():
    times = criar_times_por_nome(["Flamengo", "Clube Que Não Existe"])
    assert [t.nome for t in times] == ["Flamengo"]
