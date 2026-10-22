"""
Temporada completa: as quatro divisões jogando ao mesmo tempo.

Cada divisão é uma ``TemporadaDivisao`` (com o regulamento da série) e a
``Piramide`` coordena tudo: avança uma rodada em todas as divisões, empresta as
datas do calendário e aplica acesso/descenso no fim da temporada.

Uso
---
>>> from game.piramide import Piramide
>>> piramide = Piramide(times)                 # times com .divisao = "A".."D"
>>> piramide.ordem                             # ['A', 'B', 'C', 'D']
>>> piramide.rodada("B"), piramide.total_rodadas("B")
(0, 27)
>>> piramide.simular_rodada("Flamengo")        # uma rodada em cada divisão
{'A': [Partida(...), ...], 'B': [...], ...}
>>> piramide.classificacao("D")[0].nome        # líder da 1ª fase da Série D
>>> piramide.acesso_descenso()                 # prévia do sobe-e-desce
>>> piramide.nova_temporada()                  # aplica e recomeça
"""

from __future__ import annotations

import datetime as dt

from game.divisao import REGULAMENTOS, TemporadaDivisao
from game.modelos import Partida, Time

# ordem da pirâmide (de cima para baixo)
ORDEM_DIVISOES = ("A", "B", "C", "D")

NOMES_DIVISAO = {"A": "Série A", "B": "Série B", "C": "Série C", "D": "Série D"}

# calendário: uma rodada por semana, começando em abril
MES_INICIO = 4
DIA_INICIO = 5
DIAS_POR_RODADA = 7


def data_da_rodada(rodada: int, temporada: int = 2026) -> dt.date:
    """Data fictícia de uma rodada: uma por semana, a partir de abril."""
    inicio = dt.date(temporada, MES_INICIO, DIA_INICIO)
    return inicio + dt.timedelta(days=DIAS_POR_RODADA * (rodada - 1))


class Piramide:
    """As divisões de uma temporada, com acesso e descenso entre elas."""

    def __init__(self, times: list[Time], temporada: int = 2026):
        self.times = list(times)
        self.temporada = temporada
        self.divisoes: dict[str, TemporadaDivisao] = {}
        self._montar()

    # ---- montagem ---------------------------------------------------
    def _montar(self) -> None:
        """Cria uma temporada por divisão que tenha ao menos 2 clubes."""
        self.divisoes = {}
        for divisao in ORDEM_DIVISOES:
            clubes = [t for t in self.times if t.divisao == divisao]
            if len(clubes) < 2:
                continue
            self.divisoes[divisao] = TemporadaDivisao(
                clubes, divisao, temporada=self.temporada
            )
        if not self.divisoes:
            raise ValueError(
                "Nenhuma divisão com pelo menos 2 clubes para montar a temporada."
            )

    # ---- divisões ---------------------------------------------------
    @property
    def ordem(self) -> list[str]:
        """Divisões existentes, de cima para baixo (ex.: ``['A', 'B', 'C', 'D']``)."""
        return [d for d in ORDEM_DIVISOES if d in self.divisoes]

    def league(self, divisao: str) -> TemporadaDivisao:
        """A temporada de uma divisão (``ValueError`` se não existir)."""
        div = str(divisao).upper()
        if div not in self.divisoes:
            raise ValueError(
                f"Divisão inexistente nesta temporada: {divisao!r}. "
                f"Disponíveis: {self.ordem}."
            )
        return self.divisoes[div]

    def divisao_de(self, nome_time: str) -> str | None:
        """Divisão em que o clube joga (``None`` se não estiver na temporada)."""
        for divisao in self.ordem:
            if any(t.nome == nome_time for t in self.divisoes[divisao].times):
                return divisao
        return None

    def league_de(self, nome_time: str) -> TemporadaDivisao | None:
        divisao = self.divisao_de(nome_time)
        return self.divisoes[divisao] if divisao else None

    def nome_divisao(self, divisao: str) -> str:
        return NOMES_DIVISAO.get(str(divisao).upper(), f"Série {divisao}")

    def regulamento(self, divisao: str) -> list[str]:
        """Regras da divisão, em tópicos (para a interface)."""
        return REGULAMENTOS.get(str(divisao).upper(), [])

    # ---- rodadas ----------------------------------------------------
    def rodada(self, divisao: str) -> int:
        return self.league(divisao).rodada_atual

    def total_rodadas(self, divisao: str) -> int:
        return self.league(divisao).total_rodadas

    def encerrada_em(self, divisao: str) -> bool:
        return self.league(divisao).encerrada

    @property
    def encerrada(self) -> bool:
        """``True`` quando todas as divisões terminaram."""
        return all(self.encerrada_em(d) for d in self.ordem)

    @property
    def rodada_global(self) -> int:
        """Maior rodada já disputada em qualquer divisão."""
        return max(self.rodada(d) for d in self.ordem)

    @property
    def total_rodadas_global(self) -> int:
        """Calendário mais longo da temporada."""
        return max(self.total_rodadas(d) for d in self.ordem)

    def simular_rodada(self, time_jogador: str = "") -> dict[str, list[Partida]]:
        """Joga a rodada atual de cada divisão que ainda tem jogos."""
        jogos: dict[str, list[Partida]] = {}
        for divisao in self.ordem:
            temporada = self.divisoes[divisao]
            if temporada.encerrada:
                continue
            jogos[divisao] = temporada.simular_rodada(time_jogador)
        return jogos

    def simular_restante(self, limite: int = 400) -> int:
        """Simula tudo o que falta (útil para fechar as outras divisões)."""
        total = 0
        voltas = 0
        while not self.encerrada and voltas < limite:
            for partidas in self.simular_rodada().values():
                total += len(partidas)
            voltas += 1
        return total

    # ---- consultas --------------------------------------------------
    def classificacao(self, divisao: str) -> list[Time]:
        """Classificação da primeira fase da divisão."""
        return self.league(divisao).classificacao

    def tabela(
        self, divisao: str, fase_idx: int = 0, grupo: str | None = None
    ) -> list[dict]:
        """Classificação de uma fase (ou grupo) da divisão."""
        temporada = self.league(divisao)
        fase = temporada.fases[min(fase_idx, len(temporada.fases) - 1)]
        return temporada.tabela(fase, grupo)

    def calendario(self, divisao: str) -> list[list[tuple[str, str]]]:
        return self.league(divisao).calendario

    def resultados(self, divisao: str) -> dict[int, list[Partida]]:
        return self.league(divisao).resultados

    def partida(self, divisao: str, rodada: int, casa: str, fora: str) -> Partida | None:
        """Partida de uma rodada (``None`` se ainda não foi jogada)."""
        return self.league(divisao).partida(rodada, casa, fora)

    def confrontos_da_rodada(
        self, divisao: str, rodada: int
    ) -> list[tuple[str, str, Partida | None]]:
        """Jogos de uma rodada (1-based) com o resultado, se já disputado."""
        return self.league(divisao).confrontos_da_rodada(rodada)

    def jogos_do_time(
        self, nome_time: str, divisao: str | None = None
    ) -> list[tuple[int, str, str, Partida | None]]:
        """Calendário completo de um clube: ``(rodada, casa, fora, partida)``."""
        div = divisao or self.divisao_de(nome_time)
        if div is None:
            return []
        return self.league(div).jogos_do_time(nome_time)

    def data_da_rodada(self, rodada: int, temporada: int | None = None) -> dt.date:
        """Data (semanal) de uma rodada — o calendário do jogo é fictício."""
        return data_da_rodada(rodada, temporada or self.temporada)

    # ---- fim de temporada -------------------------------------------
    def acesso_descenso(self) -> dict[str, dict[str, list[Time]]]:
        """
        Prévia do sobe-e-desce, sem mexer em nada.

        Cada divisão informa quem sobe e quem cai segundo o seu regulamento
        (Série B: 1º e 2º de cada grupo; Série C: os 4 primeiros; Série D: os
        4 semifinalistas; rebaixamento: os 4 últimos da 1ª fase).
        """
        resumo: dict[str, dict[str, list[Time]]] = {
            d: {"promovidos": [], "rebaixados": []} for d in self.ordem
        }
        for i, cima in enumerate(ORDEM_DIVISOES):
            baixo = ORDEM_DIVISOES[i + 1] if i + 1 < len(ORDEM_DIVISOES) else None
            if cima not in self.divisoes:
                continue
            if baixo is not None and baixo in self.divisoes:
                resumo[baixo]["promovidos"] = self.league(baixo).promovidos
            resumo[cima]["rebaixados"] = self.league(cima).rebaixados
        return resumo

    def aplicar_acesso_descenso(self) -> dict[str, dict[str, list[Time]]]:
        """Aplica a prévia: muda ``Time.divisao`` de quem subiu e de quem caiu."""
        resumo = self.acesso_descenso()
        for i, cima in enumerate(ORDEM_DIVISOES):
            baixo = ORDEM_DIVISOES[i + 1] if i + 1 < len(ORDEM_DIVISOES) else None
            if baixo is None or cima not in self.divisoes or baixo not in self.divisoes:
                continue
            for time in resumo[cima]["rebaixados"]:
                time.divisao = baixo
            for time in resumo[baixo]["promovidos"]:
                time.divisao = cima
        return resumo

    def nova_temporada(self) -> dict[str, dict[str, list[Time]]]:
        """
        Fecha a temporada e começa outra: acesso/descenso, estatísticas
        zeradas e regulamentos reiniciados. Devolve o resumo do sobe-e-desce.
        """
        movimentos = self.aplicar_acesso_descenso()
        self.temporada += 1
        for time in self.times:
            time.resetar_campeonato()
            time.auto_escalar()
        self._montar()
        return movimentos

    # ---- resumo -----------------------------------------------------
    def resumo(self) -> str:
        """Texto com a situação de cada divisão (debug/rodapé)."""
        return "\n".join(
            f"{self.nome_divisao(d)}: {self.league(d).resumo()}" for d in self.ordem
        )
