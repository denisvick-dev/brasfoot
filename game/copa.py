"""
Copa do Brasil: 128 clubes, mata-mata em ida e volta, dentro da temporada.

A copa corre junto com as divisões: cada fase tem dois jogos (ida e volta) e as
datas saem espalhadas pelo calendário da temporada, então a copa aparece nas
mesmas rodadas do Brasileirão (como as quartas de semana do calendário real).

Uso
---
>>> from game.copa import CopaBrasil
>>> copa = CopaBrasil(times, temporada=2026, rodadas_temporada=27)
>>> copa.fases[0].nome                   # 'Primeira fase' (64 confrontos)
>>> copa.datas                           # rodadas globais dos jogos
>>> copa.simular_rodada_global(1)        # joga o que cai na rodada 1
>>> copa.campeao.nome                    # depois da final
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from game.jogo_engine import MatchEngine
from game.modelos import Jogador, Noticia, Partida, Time

# nome da fase pelo número de clubes ainda vivos
NOMES_FASES = {
    128: "Primeira fase",
    64: "Segunda fase",
    32: "Terceira fase",
    16: "Oitavas de final",
    8: "Quartas de final",
    4: "Semifinal",
    2: "Final",
}

REGULAMENTO = [
    "128 clubes das quatro divisões, sorteados por força (todos contra todos).",
    "Mata-mata em ida e volta da primeira fase até a final.",
    "Sem jogo único: o título é decidido no agregado dos dois jogos.",
    "Empate no agregado vai para os pênaltis.",
    "Os jogos da copa entram no calendário junto com as rodadas das divisões.",
]


@dataclass
class FaseCopa:
    """Uma fase eliminatória da copa: confrontos e datas das duas pernas."""

    nome: str
    pares: list[tuple[str, str]] = field(default_factory=list)
    rodadas: list[int] = field(default_factory=list)
    jogos: list[Partida] = field(default_factory=list)
    rodada_atual: int = 0
    vencedores: list[Time] = field(default_factory=list)
    concluida: bool = False

    @property
    def total_rodadas(self) -> int:
        return len(self.rodadas)


def _datas_da_copa(total_rodadas: int, n_datas: int) -> list[int]:
    """Espalha as datas da copa pelas rodadas da temporada (1-based)."""
    base = max(total_rodadas, n_datas)
    if n_datas <= 1:
        return [1]
    datas: list[int] = []
    for i in range(n_datas):
        rodada = round(i * (base - 1) / (n_datas - 1)) + 1
        rodada = min(base, max(1, rodada))
        while datas and rodada <= datas[-1]:
            rodada = datas[-1] + 1
        datas.append(rodada)
    return datas


class CopaBrasil:
    """A copa nacional da temporada: 128 clubes em mata-mata de ida e volta."""

    def __init__(
        self,
        times: list[Time],
        temporada: int = 2026,
        rodadas_temporada: int = 27,
        max_clubes: int = 128,
        semente: int | None = None,
        deslocamento: int = 0,
    ):
        if len(times) < 4:
            raise ValueError("A Copa do Brasil precisa de ao menos 4 clubes.")
        self.temporada = temporada
        self.engine = MatchEngine()
        self.rng = random.Random(semente)
        self.noticias: list[Noticia] = []
        self.campeao: Time | None = None
        self.vice: Time | None = None
        self._resultados: dict[int, list[Partida]] = {}

        n = min(len(times), max_clubes)
        while n > 4 and n & (n - 1):
            n -= 1  # maior potência de 2 que caiba
        ordenados = sorted(times, key=lambda t: (-t.reputacao, t.nome))[:n]
        self.times = ordenados
        self._por_nome: dict[str, Time] = {t.nome: t for t in ordenados}

        # metade mais forte contra a mais fraca (1º x último, 2º x penúltimo…)
        metade = n // 2
        fortes = ordenados[:metade]
        fracos = list(reversed(ordenados[metade:]))
        n_fases = max(1, n.bit_length() - 1)
        self.datas = [
            deslocamento + d for d in _datas_da_copa(rodadas_temporada, 2 * n_fases)
        ]
        self.fases: list[FaseCopa] = [self._primeira_fase(fortes, fracos)]

    # ---- montagem ---------------------------------------------------
    def _primeira_fase(
        self, fortes: list[Time], fracos: list[Time]
    ) -> FaseCopa:
        pares = [
            (forte.nome, fraco.nome)
            for forte, fraco in zip(fortes, fracos, strict=True)
        ]
        return FaseCopa(
            nome=NOMES_FASES.get(len(self.times), "Primeira fase"),
            pares=pares,
            rodadas=self.datas[:2],
        )

    def _proxima_fase(self, fase: FaseCopa) -> None:
        """Cria a fase seguinte com os vencedores (ou fecha a copa)."""
        vencedores = fase.vencedores
        if len(vencedores) < 2:
            self._fechar(vencedores)
            return
        base = fase.rodadas[-1] if fase.rodadas else 0
        # as duas datas seguintes do calendário
        proximas = [d for d in self.datas if d > base][:2]
        if len(proximas) < 2:
            proximas = [base + 1, base + 2]
        pares = [
            (vencedores[i].nome, vencedores[i + 1].nome)
            for i in range(0, len(vencedores) - 1, 2)
        ]
        self.fases.append(
            FaseCopa(
                nome=NOMES_FASES.get(len(vencedores), f"Fase de {len(vencedores)}"),
                pares=pares,
                rodadas=proximas,
            )
        )

    def _fechar(self, vencedores: list[Time]) -> None:
        if vencedores:
            self.campeao = vencedores[0]
            self.noticias.append(
                Noticia(
                    titulo=f"🏆 {self.campeao.nome} é campeão da Copa do Brasil!",
                    texto=(
                        f"{self.campeao.nome} venceu a final da Copa do Brasil de "
                        f"{self.temporada}."
                    ),
                    rodada=self.rodada_atual,
                    tipo="geral",
                )
            )

    # ---- situação ----------------------------------------------------
    @property
    def fase_atual(self) -> FaseCopa | None:
        if self.encerrada:
            return None
        return self.fases[-1]

    @property
    def rodada_atual(self) -> int:
        """Rodada global da copa (a da fase em disputa)."""
        fase = self.fases[-1] if self.fases else None
        if fase is None:
            return 0
        if fase.rodada_atual < len(fase.rodadas):
            return fase.rodadas[fase.rodada_atual]
        return fase.rodadas[-1] if fase.rodadas else 0

    @property
    def total_rodadas(self) -> int:
        """Rodada global do último jogo previsto."""
        return max(self.datas) if self.datas else 0

    @property
    def encerrada(self) -> bool:
        return self.campeao is not None

    @property
    def resultados(self) -> dict[int, list[Partida]]:
        return self._resultados

    # ---- simulação ---------------------------------------------------
    def simular_rodada_global(
        self, rodada: int, time_jogador: str = ""
    ) -> list[Partida]:
        """Joga a perna da fase atual que cai nesta rodada da temporada."""
        if self.encerrada:
            return []
        fase = self.fases[-1]
        if fase.rodada_atual >= len(fase.rodadas):
            return []
        if fase.rodadas[fase.rodada_atual] > rodada:
            return []

        perna = fase.rodada_atual
        jogos = self._jogar_perna(fase, perna, rodada, time_jogador)
        fase.rodada_atual += 1
        if fase.rodada_atual >= len(fase.rodadas):
            fase.concluida = True
            self._resolver(fase)
            self._proxima_fase(fase)
        return jogos

    def _jogar_perna(
        self, fase: FaseCopa, perna: int, rodada: int, time_jogador: str
    ) -> list[Partida]:
        jogos: list[Partida] = []
        for indice, (forte, fraco) in enumerate(fase.pares):
            casa, fora = (fraco, forte) if perna == 0 else (forte, fraco)
            partida = self.engine.simular(
                self._por_nome[casa],
                self._por_nome[fora],
                rodada,
                is_player_home=(casa == time_jogador),
                is_player_away=(fora == time_jogador),
            )
            partida.fase = fase.nome
            partida.grupo = "Volta" if perna else "Ida"
            partida.eventos.insert(
                0, f"🏆 Copa do Brasil · {fase.nome} · jogo de {partida.grupo.lower()}"
            )
            fase.jogos.append(partida)
            jogos.append(partida)
            _ = indice
        self._resultados.setdefault(rodada, []).extend(jogos)
        return jogos

    def _resolver(self, fase: FaseCopa) -> None:
        """Decide quem passa: agregado dos dois jogos e, se preciso, pênaltis."""
        vencedores: list[Time] = []
        for forte, fraco in fase.pares:
            a, b = self._por_nome[forte], self._por_nome[fraco]
            gols_a = gols_b = 0
            for partida in fase.jogos:
                if a.nome in (partida.time_casa, partida.time_fora) and b.nome in (
                    partida.time_casa,
                    partida.time_fora,
                ):
                    if partida.time_casa == a.nome:
                        gols_a += partida.gols_casa
                        gols_b += partida.gols_fora
                    else:
                        gols_a += partida.gols_fora
                        gols_b += partida.gols_casa
            if gols_a == gols_b:
                vencedor = self._penaltis(a, b)
                self._anotar_penaltis(fase, a, b, vencedor)
            else:
                vencedor = a if gols_a > gols_b else b
            vencedores.append(vencedor)
            if len(fase.pares) == 1:
                self.vice = b if vencedor is a else a
        fase.vencedores = vencedores

    def _penaltis(self, a: Time, b: Time) -> Time:
        p = 0.5 + (a.overall_time - b.overall_time) / 300
        p = max(0.2, min(0.8, p))
        return a if self.rng.random() < p else b

    def _anotar_penaltis(self, fase: FaseCopa, a: Time, b: Time, vencedor: Time) -> None:
        placar_v, placar_p = (4, 3) if self.rng.random() < 0.7 else (5, 4)
        for partida in reversed(fase.jogos):
            if {a.nome, b.nome} == {partida.time_casa, partida.time_fora}:
                partida.eventos.append(
                    f"🥅 Pênaltis: {vencedor.nome} vence por {placar_v} x {placar_p}"
                )
                break

    # ---- consultas ---------------------------------------------------
    def confrontos_da_rodada(
        self, rodada: int
    ) -> list[tuple[str, str, Partida | None]]:
        """Confrontos marcados para uma rodada global (``(casa, fora, partida)``)."""
        for fase in self.fases:
            if fase.rodada_atual >= len(fase.rodadas):
                continue
            if fase.rodadas[fase.rodada_atual] != rodada:
                continue
            perna = fase.rodada_atual
            confrontos: list[tuple[str, str, Partida | None]] = []
            for forte, fraco in fase.pares:
                casa, fora = (fraco, forte) if perna == 0 else (forte, fraco)
                confrontos.append((casa, fora, self.partida(rodada, casa, fora)))
            return confrontos
        return []

    def partida(self, rodada: int, casa: str, fora: str) -> Partida | None:
        for partida in self._resultados.get(rodada, []):
            if partida.time_casa == casa and partida.time_fora == fora:
                return partida
        return None

    def jogo_do_jogador(self, nome: str, rodada: int) -> Partida | None:
        for partida in self._resultados.get(rodada, []):
            if nome in (partida.time_casa, partida.time_fora):
                return partida
        return None

    def jogos_do_time(
        self, nome: str
    ) -> list[tuple[int, str, str, Partida | None]]:
        """Jogos do clube na copa: ``(rodada, casa, fora, partida)``."""
        jogos: list[tuple[int, str, str, Partida | None]] = []
        for fase in self.fases:
            for i, rodada in enumerate(fase.rodadas):
                for forte, fraco in fase.pares:
                    casa, fora = (fraco, forte) if i == 0 else (forte, fraco)
                    if nome in (casa, fora):
                        jogos.append(
                            (rodada, casa, fora, self.partida(rodada, casa, fora))
                        )
        return jogos

    def proximo_jogo(self, nome: str) -> tuple[int, str, str] | None:
        """O próximo jogo do clube na copa (ou ``None`` se já foi eliminado)."""
        if self.encerrada:
            return None
        fase = self.fases[-1]
        if fase.rodada_atual >= len(fase.rodadas):
            return None
        perna = fase.rodada_atual
        for forte, fraco in fase.pares:
            if nome not in (forte, fraco):
                continue
            casa, fora = (fraco, forte) if perna == 0 else (forte, fraco)
            return (fase.rodadas[perna], casa, fora)
        return None

    def vivo(self, nome: str) -> bool:
        """O clube ainda está na copa?"""
        return nome in (t.nome for f in self.fases for t in f.vencedores) or (
            not self.encerrada and self.proximo_jogo(nome) is not None
        )

    def artilharia(self, top: int = 15) -> list[tuple[Jogador, str]]:
        artilheiros = [
            (jogador, time.sigla)
            for time in self.times
            for jogador in time.jogadores
            if jogador.gols > 0
        ]
        artilheiros.sort(key=lambda x: (-x[0].gols, -x[0].assistencias))
        return artilheiros[:top]

    # ---- resumo -----------------------------------------------------
    def resumo(self) -> str:
        if self.encerrada and self.campeao is not None:
            return f"Copa do Brasil: encerrada · campeão {self.campeao.nome}"
        fase = self.fases[-1] if self.fases else None
        if fase is None:
            return "Copa do Brasil: sem fases"
        return (
            f"Copa do Brasil: {fase.nome} · {len(fase.pares)} confrontos · "
            f"jogo {min(fase.rodada_atual + 1, len(fase.rodadas))}/{len(fase.rodadas)}"
        )
