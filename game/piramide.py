"""
Temporada completa: todas as divisões jogando ao mesmo tempo.

Cada divisão é uma ``League`` (calendário e classificação próprios) e a
``Piramide`` coordena tudo: avança uma rodada em todas as divisões,
empresta as datas do calendário e aplica acesso/descenso no fim da temporada.

Uso
---
>>> from game.piramide import Piramide
>>> piramide = Piramide(times)                 # times com .divisao = "A".."D"
>>> piramide.ordem                             # ['A', 'B', 'C', 'D']
>>> piramide.rodada("B"), piramide.total_rodadas("B")
(0, 38)
>>> piramide.simular_rodada("Flamengo")        # uma rodada em cada divisão
{'A': [Partida(...), ...], 'B': [...], ...}
>>> piramide.classificacao("D")[0].nome        # líder da Série D
>>> piramide.acesso_descenso()                 # prévia do sobe-e-desce
>>> piramide.nova_temporada()                  # aplica e recomeça
"""

from __future__ import annotations

import datetime as dt

from game.campeonato import League
from game.modelos import Partida, Time

# ordem da pirâmide (de cima para baixo)
ORDEM_DIVISOES = ("A", "B", "C", "D")

NOMES_DIVISAO = {"A": "Série A", "B": "Série B", "C": "Série C", "D": "Série D"}

# quantos clubes caem de cada divisão (e sobem da de baixo)
ACESSO_PADRAO: dict[str, int] = {"A": 4, "B": 4, "C": 4}

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
        self.divisoes: dict[str, League] = {}
        self._montar()

    # ---- montagem ---------------------------------------------------
    def _montar(self) -> None:
        """Cria uma ``League`` por divisão que tenha ao menos 2 clubes."""
        self.divisoes = {}
        for divisao in ORDEM_DIVISOES:
            clubes = [t for t in self.times if t.divisao == divisao]
            if len(clubes) < 2:
                continue
            liga = League(clubes)
            liga.temporada = self.temporada
            self.divisoes[divisao] = liga
        if not self.divisoes:
            raise ValueError(
                "Nenhuma divisão com pelo menos 2 clubes para montar a temporada."
            )

    # ---- divisões ---------------------------------------------------
    @property
    def ordem(self) -> list[str]:
        """Divisões existentes, de cima para baixo (ex.: ``['A', 'B', 'C', 'D']``)."""
        return [d for d in ORDEM_DIVISOES if d in self.divisoes]

    def league(self, divisao: str) -> League:
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

    def league_de(self, nome_time: str) -> League | None:
        divisao = self.divisao_de(nome_time)
        return self.divisoes[divisao] if divisao else None

    def nome_divisao(self, divisao: str) -> str:
        return NOMES_DIVISAO.get(str(divisao).upper(), f"Série {divisao}")

    # ---- rodadas ----------------------------------------------------
    def rodada(self, divisao: str) -> int:
        return self.league(divisao).rodada_atual

    def total_rodadas(self, divisao: str) -> int:
        return self.league(divisao).total_rodadas

    def encerrada_em(self, divisao: str) -> bool:
        liga = self.league(divisao)
        return liga.campeonato_encerrado or liga.rodada_atual >= liga.total_rodadas

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
        """Calendário mais longo da temporada (a Série D puxa esse número)."""
        return max(self.total_rodadas(d) for d in self.ordem)

    def simular_rodada(self, time_jogador: str = "") -> dict[str, list[Partida]]:
        """Joga a rodada atual de cada divisão que ainda tem jogos."""
        jogos: dict[str, list[Partida]] = {}
        for divisao in self.ordem:
            liga = self.divisoes[divisao]
            if liga.rodada_atual >= liga.total_rodadas:
                continue
            jogos[divisao] = liga.simular_rodada(time_jogador)
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
        return self.league(divisao).classificacao

    def calendario(self, divisao: str) -> list[list[tuple[str, str]]]:
        return self.league(divisao).calendario

    def resultados(self, divisao: str) -> dict[int, list[Partida]]:
        return self.league(divisao).resultados

    def partida(self, divisao: str, rodada: int, casa: str, fora: str) -> Partida | None:
        """Partida de uma rodada (``None`` se ainda não foi jogada)."""
        for partida in self.resultados(divisao).get(rodada, []):
            if partida.time_casa == casa and partida.time_fora == fora:
                return partida
        return None

    def confrontos_da_rodada(
        self, divisao: str, rodada: int
    ) -> list[tuple[str, str, Partida | None]]:
        """Jogos de uma rodada (1-based) com o resultado, se já disputado."""
        calendario = self.calendario(divisao)
        if rodada < 1 or rodada > len(calendario):
            return []
        return [
            (casa, fora, self.partida(divisao, rodada, casa, fora))
            for casa, fora in calendario[rodada - 1]
        ]

    def jogos_do_time(
        self, nome_time: str, divisao: str | None = None
    ) -> list[tuple[int, str, str, Partida | None]]:
        """Calendário completo de um clube: ``(rodada, casa, fora, partida)``."""
        div = divisao or self.divisao_de(nome_time)
        if div is None:
            return []
        jogos = []
        for i, rodada in enumerate(self.calendario(div), start=1):
            for casa, fora in rodada:
                if nome_time in (casa, fora):
                    jogos.append(
                        (i, casa, fora, self.partida(div, i, casa, fora))
                    )
        return jogos

    def data_da_rodada(self, rodada: int, temporada: int | None = None) -> dt.date:
        """Data (semanal) de uma rodada — o calendário do jogo é fictício."""
        return data_da_rodada(rodada, temporada or self.temporada)

    # ---- fim de temporada -------------------------------------------
    def acesso_descenso(
        self, vagas: dict[str, int] | None = None
    ) -> dict[str, dict[str, list[Time]]]:
        """
        Prévia do sobe-e-desce, sem mexer em nada.

        Devolve ``{"A": {"rebaixados": [...], "promovidos": [...]}, ...}``.
        """
        cotas = dict(ACESSO_PADRAO if vagas is None else vagas)
        resumo: dict[str, dict[str, list[Time]]] = {
            d: {"promovidos": [], "rebaixados": []} for d in self.ordem
        }
        for i, cima in enumerate(ORDEM_DIVISOES):
            baixo = ORDEM_DIVISOES[i + 1] if i + 1 < len(ORDEM_DIVISOES) else None
            if baixo is None or cima not in self.divisoes or baixo not in self.divisoes:
                continue
            tabela_cima = self.classificacao(cima)
            tabela_baixo = self.classificacao(baixo)
            n = min(cotas.get(cima, 0), len(tabela_cima) // 2, len(tabela_baixo) // 2)
            if n <= 0:
                continue
            resumo[cima]["rebaixados"] = tabela_cima[-n:]
            resumo[baixo]["promovidos"] = tabela_baixo[:n]
        return resumo

    def aplicar_acesso_descenso(
        self, vagas: dict[str, int] | None = None
    ) -> dict[str, dict[str, list[Time]]]:
        """Aplica a prévia: muda ``Time.divisao`` de quem subiu e de quem caiu."""
        resumo = self.acesso_descenso(vagas)
        for i, cima in enumerate(ORDEM_DIVISOES):
            baixo = ORDEM_DIVISOES[i + 1] if i + 1 < len(ORDEM_DIVISOES) else None
            if baixo is None or cima not in self.divisoes or baixo not in self.divisoes:
                continue
            for time in resumo[cima]["rebaixados"]:
                time.divisao = baixo
            for time in resumo[baixo]["promovidos"]:
                time.divisao = cima
        return resumo

    def nova_temporada(
        self, vagas: dict[str, int] | None = None
    ) -> dict[str, dict[str, list[Time]]]:
        """
        Fecha a temporada e começa outra: acesso/descenso, estatísticas
        zeradas e calendários novos. Devolve o resumo do sobe-e-desce.
        """
        movimentos = self.aplicar_acesso_descenso(vagas)
        self.temporada += 1
        for time in self.times:
            time.resetar_campeonato()
            time.auto_escalar()
        self._montar()
        return movimentos

    # ---- resumo -----------------------------------------------------
    def resumo(self) -> str:
        """Texto com a situação de cada divisão (debug/rodapé)."""
        linhas = []
        for divisao in self.ordem:
            liga = self.divisoes[divisao]
            lider = liga.classificacao[0].nome if liga.times else "—"
            linhas.append(
                f"{self.nome_divisao(divisao)}: rodada "
                f"{liga.rodada_atual}/{liga.total_rodadas} · líder {lider}"
            )
        return "\n".join(linhas)
