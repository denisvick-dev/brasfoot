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
>>> piramide.simular_rodada("Flamengo")        # uma rodada em cada divisão (+ copa)
{'A': [Partida(...), ...], 'B': [...], ...}
>>> piramide.classificacao("D")[0].nome        # líder da 1ª fase da Série D
>>> piramide.acesso_descenso()                 # prévia do sobe-e-desce
>>> piramide.nova_temporada()                  # aplica e recomeça
"""

from __future__ import annotations

import datetime as dt
import random

from game.copa import CopaBrasil
from game.jogo_engine import MatchEngine
from game.divisao import REGULAMENTOS, TemporadaDivisao
from game.regional import REGIONAIS, TorneioRegional
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
        self.copa: CopaBrasil | None = None
        self.regionais: list[TorneioRegional] = []
        self.engine = MatchEngine()
        self.rng = random.Random()
        self.supercopa: Partida | None = None
        self.supercopa_times: tuple[Time, Time] | None = None
        self._rodada = 0
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
        self._rodada = 0
        self.regionais = self._montar_regionais()
        self.supercopa = None
        self.supercopa_times = None
        self.copa = self._montar_copa()

    def _montar_copa(self) -> CopaBrasil | None:
        """A Copa do Brasil da temporada, com as datas espalhadas nas rodadas."""
        if len(self.times) < 4:
            return None
        total = max(
            (temporada.total_rodadas for temporada in self.divisoes.values()),
            default=0,
        )
        try:
            return CopaBrasil(
                self.times,
                temporada=self.temporada,
                rodadas_temporada=total,
                deslocamento=self.rodadas_regionais,
            )
        except ValueError:
            return None

    def _montar_regionais(self) -> list[TorneioRegional]:
        """Os torneios regionais que abrem a temporada."""
        torneios: list[TorneioRegional] = []
        for chave in REGIONAIS:
            try:
                torneios.append(
                    TorneioRegional(
                        self.times,
                        chave,
                        temporada=self.temporada,
                        deslocamento=0,
                    )
                )
            except ValueError:
                continue
        return torneios

    @property
    def rodadas_regionais(self) -> int:
        """Quantas rodadas os torneios regionais ocupam no início do ano."""
        return max((t.total_rodadas for t in self.regionais), default=0)

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
    def copa_encerrada(self) -> bool:
        """``True`` quando a Copa do Brasil terminou (ou não existe)."""
        return self.copa is None or self.copa.encerrada

    @property
    def fases_finais_encerradas(self) -> bool:
        """Divisões e copa já terminaram (falta só a Supercopa)."""
        return all(self.encerrada_em(d) for d in self.ordem) and self.copa_encerrada

    @property
    def encerrada(self) -> bool:
        """``True`` quando divisões, copa e Supercopa terminaram."""
        if not self.fases_finais_encerradas:
            return False
        if not self._tem_supercopa():
            return True
        self._garantir_supercopa()
        if self.supercopa_times is None:
            return self.supercopa is not None or True
        return self.supercopa is not None

    @property
    def rodada_global(self) -> int:
        """Rodada da temporada já disputada (divisões e copa andam juntas)."""
        return self._rodada

    @property
    def total_rodadas_global(self) -> int:
        """Calendário da temporada: regionais + divisões/copa + Supercopa."""
        divisoes = max((self.total_rodadas(d) for d in self.ordem), default=0)
        total = self.rodadas_regionais + divisoes
        if self.copa is not None:
            total = max(total, self.copa.total_rodadas)
        if self._tem_supercopa():
            total += 1
        return total

    def simular_rodada(self, time_jogador: str = "") -> dict[str, list[Partida]]:
        """Joga a rodada da temporada: regionais, divisões/copa ou Supercopa."""
        jogos: dict[str, list[Partida]] = {}
        self._rodada += 1

        # início do ano: só os torneios regionais
        if self._rodada <= self.rodadas_regionais:
            for torneio in self.regionais:
                partidas = torneio.simular_rodada_global(
                    self._rodada, time_jogador
                )
                if partidas:
                    jogos[torneio.chave] = partidas
            return jogos

        # meio do ano: divisões + Copa do Brasil
        if not self.fases_finais_encerradas:
            for divisao in self.ordem:
                temporada = self.divisoes[divisao]
                if temporada.encerrada:
                    continue
                jogos[divisao] = temporada.simular_rodada(time_jogador)
            if self.copa is not None:
                partidas = self.copa.simular_rodada_global(
                    self._rodada, time_jogador
                )
                if partidas:
                    jogos["COPA"] = partidas
            return jogos

        # fim do ano: Supercopa do Brasil
        partida = self._jogar_supercopa(time_jogador)
        if partida is not None:
            jogos["SUPERCOPA"] = [partida]
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

    # ---- torneios regionais -----------------------------------------
    def torneio(self, chave: str) -> TorneioRegional | None:
        """Um torneio regional pelo código (``RIO-SP``, ``SUL-MINAS``…)."""
        alvo = str(chave).upper()
        for torneio in self.regionais:
            if torneio.chave == alvo:
                return torneio
        return None

    @property
    def nomes_regionais(self) -> list[str]:
        return [torneio.nome for torneio in self.regionais]

    def regional_jogos_do_time(
        self, nome_time: str
    ) -> list[tuple[str, int, str, str, Partida | None]]:
        """Jogos do clube nos torneios regionais."""
        jogos: list[tuple[str, int, str, str, Partida | None]] = []
        for torneio in self.regionais:
            for rodada, casa, fora, partida in torneio.jogos_do_time(nome_time):
                jogos.append((torneio.nome, rodada, casa, fora, partida))
        return jogos

    # ---- supercopa ---------------------------------------------------
    def _montar_confronto_supercopa(self) -> tuple[Time, Time] | None:
        """Campeão brasileiro x campeão da Copa do Brasil (ou o vice da copa)."""
        if "A" not in self.divisoes or self.copa is None:
            return None
        campeao_br = self.divisoes["A"].campeao
        campeao_copa = self.copa.campeao
        if campeao_br is None or campeao_copa is None:
            return None
        desafiante = campeao_copa
        if desafiante.nome == campeao_br.nome:
            if self.copa.vice is None:
                return None
            desafiante = self.copa.vice
        if desafiante.nome == campeao_br.nome:
            return None
        return (campeao_br, desafiante)

    def _garantir_supercopa(self) -> bool:
        if not (self.fases_finais_encerradas and self.copa is not None):
            return False
        if "A" not in self.divisoes:
            return False
        if self.supercopa_times is None:
            self.supercopa_times = self._montar_confronto_supercopa()
        return self.supercopa_times is not None

    def _tem_supercopa(self) -> bool:
        return "A" in self.divisoes and self.copa is not None

    def _jogar_supercopa(self, time_jogador: str = "") -> Partida | None:
        """Disputa a Supercopa do Brasil (jogo único)."""
        if self.supercopa is not None or not self._garantir_supercopa():
            return None
        assert self.supercopa_times is not None
        casa, fora = self.supercopa_times
        partida = self.engine.simular(
            casa,
            fora,
            self._rodada,
            is_player_home=(casa.nome == time_jogador),
            is_player_away=(fora.nome == time_jogador),
        )
        partida.fase = "Supercopa do Brasil"
        partida.grupo = "Jogo único"
        partida.eventos.insert(0, "🏆 Supercopa do Brasil · jogo único")
        if partida.gols_casa == partida.gols_fora:
            p = 0.5 + (casa.overall_time - fora.overall_time) / 300
            p = max(0.2, min(0.8, p))
            vencedor = casa if self.rng.random() < p else fora
            partida.eventos.append(f"🥅 Pênaltis: {vencedor.nome} vence a Supercopa")
        self.supercopa = partida
        return partida

    @property
    def supercopa_disponivel(self) -> bool:
        return self.supercopa is None and self._tem_supercopa()

    # ---- consultas --------------------------------------------------
    def proximo_jogo(self, nome_time: str) -> tuple[str, int, str, str] | None:
        """Próximo jogo do clube: ``(competição, rodada, casa, fora)``."""
        rodada = self._rodada + 1
        if rodada <= self.rodadas_regionais:
            for torneio in self.regionais:
                prox = torneio.proximo_jogo(nome_time)
                if prox is not None and prox[0] == rodada:
                    return (torneio.nome, prox[0], prox[1], prox[2])
            return None
        if self.copa is not None and not self.copa.encerrada:
            prox = self.copa.proximo_jogo(nome_time)
            if prox is not None and prox[0] == rodada:
                return ("Copa do Brasil", prox[0], prox[1], prox[2])
        if self._garantir_supercopa() and self.supercopa_times is not None:
            casa, fora = self.supercopa_times
            if nome_time in (casa.nome, fora.nome):
                return ("Supercopa do Brasil", rodada, casa.nome, fora.nome)
        divisao = self.divisao_de(nome_time)
        if divisao is not None:
            temporada = self.league(divisao)
            indice = temporada.rodada_atual
            if not temporada.encerrada and indice < len(temporada.calendario):
                for casa, fora in temporada.calendario[indice]:
                    if nome_time in (casa, fora):
                        return (self.nome_divisao(divisao), rodada, casa, fora)
        return None

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

    # ---- copa do brasil ---------------------------------------------
    def copa_do_brasil(self) -> CopaBrasil | None:
        """A Copa do Brasil da temporada (``None`` se não foi montada)."""
        return self.copa

    def copa_confrontos(self, rodada: int) -> list[tuple[str, str, Partida | None]]:
        """Confrontos da copa marcados para uma rodada global."""
        return self.copa.confrontos_da_rodada(rodada) if self.copa is not None else []

    def copa_jogos_do_time(
        self, nome_time: str
    ) -> list[tuple[int, str, str, Partida | None]]:
        """Jogos de um clube na copa: ``(rodada, casa, fora, partida)``."""
        return self.copa.jogos_do_time(nome_time) if self.copa is not None else []

    @property
    def copa_campeao(self) -> Time | None:
        return self.copa.campeao if self.copa is not None else None

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
        linhas = [f"{t.resumo()}" for t in self.regionais]
        linhas += [
            f"{self.nome_divisao(d)}: {self.league(d).resumo()}" for d in self.ordem
        ]
        if self.copa is not None:
            linhas.append(self.copa.resumo())
        if self.supercopa is not None:
            linhas.append(
                f"Supercopa: {self.supercopa.time_casa} "
                f"{self.supercopa.gols_casa} x {self.supercopa.gols_fora} "
                f"{self.supercopa.time_fora}"
            )
        return "\n".join(linhas)
