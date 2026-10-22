"""Criador de clubes/jogadores e persistência em JSON."""

import pytest

from game import persistencia
from game.criador import criar_clube, criar_jogador
from game.persistencia import jogador_de_dict, jogador_para_dict


@pytest.fixture(autouse=True)
def dados_em_tmp(tmp_path, monkeypatch):
    """Isola os arquivos de `dados/` num diretório temporário."""
    monkeypatch.setattr(persistencia, "DADOS_DIR", tmp_path)


def test_criar_jogador_valida_posicao():
    with pytest.raises(ValueError):
        criar_jogador("Zé", "XYZ", 25, 70, 70, 70, 70, 70, 70)


def test_criar_clube_valida_entradas():
    with pytest.raises(ValueError):
        criar_clube("", "ABC")
    with pytest.raises(ValueError):
        criar_clube("Time", "ABC", forca_min=90, forca_max=50)


def test_criar_clube_monta_elenco_e_ficha():
    time = criar_clube("Clube Teste", "CTE", tamanho_elenco=18, forca_min=50, forca_max=60)
    assert time.sigla == "CTE"
    assert len(time.jogadores) == 18
    assert time.origem == "custom"
    assert time.formacao in {"4-4-2", "4-3-3", "3-5-2", "4-5-1", "5-3-2"}
    assert time.estadio


def test_salvar_e_carregar_clube(tmp_path):
    time = criar_clube("Clube Persistido", "CPR", tamanho_elenco=16)
    slug = persistencia.salvar("clube", time.nome, persistencia.time_para_dict(time))
    assert slug
    assert persistencia.total("clube") == 1
    registro = persistencia.carregar("clube", slug)
    assert registro is not None
    voltou = persistencia.time_de_dict(registro["dados"])
    assert voltou.nome == time.nome
    assert len(voltou.jogadores) == len(time.jogadores)


def test_jogador_round_trip(banco):
    jogador = banco[0].jogadores[0]
    voltou = jogador_de_dict(jogador_para_dict(jogador))
    assert voltou.nome == jogador.nome
    assert voltou.overall == jogador.overall


def test_excluir_registro():
    time = criar_clube("Clube Apagado", "CAP", tamanho_elenco=16)
    slug = persistencia.salvar("clube", time.nome, persistencia.time_para_dict(time))
    assert persistencia.excluir("clube", slug)
    assert persistencia.carregar("clube", slug) is None
