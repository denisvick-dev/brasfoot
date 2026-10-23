"""Modelos: Jogador e Time."""

from game.modelos import Jogador, Partida, Time


def _time(jogadores: list[Jogador] | None = None) -> Time:
    """Time de teste, com elenco opcional."""
    return Time(
        id=1,
        nome="Teste",
        sigla="TST",
        cidade="Lugar",
        estado="SP",
        cor_primaria="#16A34A",
        cor_secundaria="#FFFFFF",
        escudo_emoji="⚽",
        jogadores=jogadores or [],
    )


def test_overall_fica_na_faixa(banco):
    for time in banco:
        for jogador in time.jogadores:
            assert 1 <= jogador.overall <= 100


def test_auto_escalar_monta_onze_titulares(banco):
    for time in banco[:10]:
        time.auto_escalar()
        assert len(time.titulares) == 11
        assert time.overall_time > 0


def test_escalacao_respeita_formacao():
    time = _time()
    time.formacao = "4-3-3"
    time.jogadores = [
        Jogador(i, f"J{i}", pos, 25, 70, 70, 70, 70, 70, 70)
        for i, pos in enumerate(
            ["GOL"]
            + ["ZAG"] * 4
            + ["LAT"] * 2
            + ["VOL"] * 2
            + ["MEI"] * 3
            + ["ATA"] * 4
        )
    ]
    time.auto_escalar()
    assert sum(1 for j in time.titulares if j.posicao == "ATA") == 3


def test_jogador_cansado_perde_espaco():
    novo = Jogador(1, "Novo", "ATA", 22, 70, 70, 70, 70, 70, 70)
    cansado = Jogador(2, "Cansado", "ATA", 22, 70, 70, 70, 70, 70, 70)
    cansado.energia = 20
    time = _time(jogadores=[novo, cansado])
    assert time.peso_escalacao(novo) > time.peso_escalacao(cansado)


def test_lesionado_e_suspenso_ficam_fora():
    time = _time(
        jogadores=[
            Jogador(i, f"J{i}", "GOL", 25, 70, 70, 70, 70, 70, 70) for i in range(3)
        ]
    )
    time.jogadores[0].lesionado = True
    time.jogadores[1].suspenso = True
    time.auto_escalar()
    assert [j.nome for j in time.titulares] == ["J2"]


def test_resetar_campeonato_zera_estatisticas(banco):
    time = banco[0]
    time.pontos, time.gols_pro, time.jogos_campeonato = 10, 7, 5
    time.jogadores[0].gols = 4
    time.resetar_campeonato()
    assert (time.pontos, time.gols_pro, time.jogos_campeonato) == (0, 0, 0)
    assert time.jogadores[0].gols == 0


def test_saldo_e_folha(banco):
    time = banco[0]
    time.gols_pro, time.gols_contra = 10, 4
    assert time.saldo_gols == 6
    assert time.folha_salarial == sum(j.salario for j in time.jogadores)
    assert time.valor_elenco == sum(j.valor_mercado for j in time.jogadores)


def test_partida_resultado_str():
    partida = Partida(rodada=1, time_casa="A", time_fora="B", gols_casa=2, gols_fora=1)
    assert partida.resultado_str == "A 2 x 1 B"
