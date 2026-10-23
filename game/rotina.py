"""
Rotina entre rodadas: o que acontece com os clubes enquanto a bola não rola.

Energia, lesões, suspensões e folha de pagamento são processadas aqui, num
lugar só, para que a temporada completa (``Piramide``) e o campeonato avulso
(``League``) tenham o mesmo comportamento.
"""

from __future__ import annotations

import random

from game import financas
from game.modelos import Time

PROB_CURA = 0.22  # chance de um lesionado se recuperar por rodada

# Renda fixa por divisão (a cota de TV é o que mantém os clubes pequenos vivos:
# sem ela, quem joga poucas partidas em casa fecha a temporada no vermelho).
COTA_TV_RODADA: dict[str, int] = {
    "A": 450_000,
    "B": 260_000,
    "C": 190_000,
    "D": 120_000,
}
PATROCINIO_MES: dict[str, int] = {
    "A": 3_000_000,
    "B": 900_000,
    "C": 350_000,
    "D": 120_000,
}


def recuperar(time: Time, rng: random.Random | None = None) -> None:
    """Recupera energia, cura lesões e cumpre suspensões de um clube."""
    sorteio = rng if rng is not None else random
    engine_recuperacao = (12, 26)  # espelha MatchEngine.RECUPERACAO_MIN/MAX

    for jogador in time.jogadores:
        jogador.recuperar_energia(sorteio.randint(*engine_recuperacao))

        if jogador.lesionado and sorteio.random() < PROB_CURA:
            jogador.lesionado = False
            jogador.energia = max(jogador.energia, 60)

        if jogador.suspenso:
            jogador.jogos_suspenso = max(0, jogador.jogos_suspenso - 1)
            if jogador.jogos_suspenso == 0:
                jogador.suspenso = False
                # zerar o cartão evita nova suspensão no jogo seguinte
                jogador.cartoes_amarelos = 0

    time.auto_escalar()


def pagar_renda_fixa(time: Time, rodada: int, rodadas_por_mes: int = 6) -> None:
    """Cota de TV da rodada + patrocínio mensal (receita de todo clube)."""
    divisao = (getattr(time, "divisao", "") or "A").upper()
    financas.registrar(
        time,
        rodada,
        "tv",
        f"Cota de TV da rodada {rodada}",
        COTA_TV_RODADA.get(divisao, 100_000),
    )
    if rodadas_por_mes and rodada % rodadas_por_mes == 0:
        financas.registrar(
            time,
            rodada,
            "patrocinio",
            "Patrocínio do mês",
            PATROCINIO_MES.get(divisao, 100_000),
        )


def pagar_salarios(time: Time, rodada: int) -> int:
    """Desconta a folha salarial do clube e registra no extrato."""
    folha = time.folha_salarial
    if folha <= 0:
        return 0
    financas.registrar(
        time, rodada, "salarios", f"Folha salarial da rodada {rodada}", -folha
    )
    return folha


def entre_rodadas(
    times: list[Time], rodada: int, rodadas_por_mes: int = 6
) -> None:
    """Roda a rotina de todos os clubes ao fim de uma rodada."""
    for time in times:
        recuperar(time)
        pagar_renda_fixa(time, rodada, rodadas_por_mes)
        if rodadas_por_mes and rodada % rodadas_por_mes == 0:
            pagar_salarios(time, rodada)
