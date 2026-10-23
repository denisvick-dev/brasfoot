"""Finanças: extrato, resumo e premiação."""

from game import financas, rotina
from game.modelos import Jogador, Time


def _time(divisao: str = "A", torcida: int = 40, salario: int = 10_000) -> Time:
    jogadores = [
        Jogador(i, f"J{i}", "ATA", 25, 60, 60, 60, 60, 60, 60, salario=salario)
        for i in range(11)
    ]
    time = Time(
        id=1,
        nome="Teste",
        sigla="TST",
        cidade="Lugar",
        estado="SP",
        cor_primaria="#16A34A",
        cor_secundaria="#FFFFFF",
        escudo_emoji="⚽",
        jogadores=jogadores,
        torcida=torcida,
    )
    time.divisao = divisao
    return time


def test_registrar_atualiza_caixa_e_extrato():
    time = _time()
    caixa = time.financas
    financas.registrar(time, 1, "bilheteria", "Jogo em casa", 500_000)
    financas.registrar(time, 1, "salarios", "Folha", -200_000)
    assert time.financas == caixa + 500_000 - 200_000
    assert len(time.extrato) == 2
    assert financas.receitas(time) == 500_000
    assert financas.despesas(time) == 200_000


def test_tipo_desconhecido_vira_outros():
    time = _time()
    financas.registrar(time, 1, "inventado", "?", 100)
    assert time.extrato[-1]["tipo"] == "outros"


def test_resumo_soma_por_tipo():
    time = _time()
    financas.registrar(time, 1, "tv", "a", 100)
    financas.registrar(time, 2, "tv", "b", 50)
    financas.registrar(time, 2, "salarios", "c", -30)
    resumo = financas.resumo(time)
    assert resumo["tv"] == 150
    assert resumo["salarios"] == -30


def test_extrato_nao_cresce_sem_limite():
    time = _time()
    for i in range(financas.LIMITE_EXTRATO + 30):
        financas.registrar(time, i, "outros", "x", 1)
    assert len(time.extrato) == financas.LIMITE_EXTRATO


def test_premio_por_posicao_decresce():
    premios = [financas.premio_temporada("A", p, 20) for p in range(1, 21)]
    assert premios[0] > premios[1] > premios[3]
    assert premios[-1] == min(premios)
    assert financas.premio_temporada("D", 0, 96) == 0
    assert financas.premio_temporada("D", 97, 96) == 0


def test_premio_copa():
    assert financas.premio_copa("Campeão") > financas.premio_copa("Vice")
    assert financas.premio_copa("") == 0


def test_renda_fixa_entra_toda_rodada():
    time = _time(divisao="D")
    rotina.pagar_renda_fixa(time, rodada=1, rodadas_por_mes=6)
    tipos = [e["tipo"] for e in time.extrato]
    assert tipos == ["tv"]
    rotina.pagar_renda_fixa(time, rodada=6, rodadas_por_mes=6)
    assert time.extrato[-1]["tipo"] == "patrocinio"


def test_salarios_so_a_cada_seis_rodadas():
    time = _time(salario=10_000)
    rotina.entre_rodadas([time], rodada=1, rodadas_por_mes=6)
    assert not any(e["tipo"] == "salarios" for e in time.extrato)
    rotina.entre_rodadas([time], rodada=6, rodadas_por_mes=6)
    assert time.extrato[-1]["tipo"] == "salarios"
    assert time.extrato[-1]["valor"] == -time.folha_salarial


def test_recuperar_energia_cura_e_cumpre_suspensao(monkeypatch):
    monkeypatch.setattr(rotina, "PROB_CURA", 1.0)  # garante a cura
    time = _time()
    jogador = time.jogadores[0]
    jogador.energia = 10
    jogador.lesionado = True
    jogador.suspenso = True
    jogador.jogos_suspenso = 1
    jogador.cartoes_amarelos = 3

    rotina.recuperar(time)
    assert jogador.energia > 10
    assert not jogador.lesionado
    assert not jogador.suspenso
    assert jogador.jogos_suspenso == 0
    assert jogador.cartoes_amarelos == 0


def test_suspensao_dura_um_jogo():
    """Cartão deixa o jogador fora do jogo seguinte (e só de um)."""
    time = _time()
    jogador = time.jogadores[0]
    jogador.suspenso = True
    jogador.jogos_suspenso = 2  # o que o motor grava ao dar o cartão
    rotina.recuperar(time)

    assert jogador.suspenso, "ainda tem que cumprir a rodada seguinte"
    assert jogador.jogos_suspenso == 1
    rotina.recuperar(time)
    assert not jogador.suspenso
