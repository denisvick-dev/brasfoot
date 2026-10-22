"""
Torneios regionais do início da temporada: Rio-SP, Sul-Minas e Nordeste.

Cada torneio reúne os **12 clubes** mais fortes da sua região e é disputado
antes do Brasileirão começar:

* **fase de grupos** — 3 grupos de 4, em turno único (3 rodadas);
* **quartas e semifinais** — jogo único, com o melhor campanha em casa;
* **final** — ida e volta.

Os 8 classificados são os líderes e vice-líderes de cada grupo mais os dois
melhores terceiros. As datas ocupam as primeiras rodadas da temporada
(deslocamento aplicado pela :class:`~game.piramide.Piramide`).

Uso
---
>>> from game.regional import TorneioRegional
>>> rio_sp = TorneioRegional(times, "RIO-SP", temporada=2026, deslocamento=0)
>>> rio_sp.nome, len(rio_sp.times)              # 'Torneio Rio-SP', 12
>>> rio_sp.datas                                # [1, 2, 3, 4, 5, 6, 7]
>>> rio_sp.simular_rodada_global(1)             # 1ª rodada dos grupos
>>> rio_sp.campeao.nome                         # depois da final
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from game.divisao import _round_robin
from game.jogo_engine import MatchEngine
from game.modelos import Jogador, Noticia, Partida, Time


@dataclass(frozen=True)
class Regiao:
    """Um torneio regional: nome e estados que participam."""

    nome: str
    estados: tuple[str, ...]
    resumo: str


REGIONAIS: dict[str, Regiao] = {
    "RIO-SP": Regiao(
        "Torneio Rio-SP",
        ("RJ", "SP"),
        "Clubes do Rio de Janeiro e de São Paulo.",
    ),
    "SUL-MINAS": Regiao(
        "Torneio Sul-Minas",
        ("RS", "SC", "PR", "MG"),
        "Clubes do Sul e de Minas Gerais.",
    ),
    "NORDESTE": Regiao(
        "Copa do Nordeste",
        ("BA", "PE", "CE", "RN", "PB", "AL", "SE", "PI", "MA"),
        "Clubes do Nordeste.",
    ),
}

NOMES_MATA = {
    8: "Quartas de final",
    4: "Semifinal",
    2: "Final",
}

REGULAMENTO = [
    "12 clubes da região, divididos em 3 grupos de 4.",
    "Fase de grupos em turno único (3 rodadas).",
    "Classificam-se os 2 primeiros de cada grupo e os 2 melhores terceiros.",
    "Quartas e semifinais em jogo único, com mando do melhor campanha.",
    "Final em ida e volta; empate no agregado vai para os pênaltis.",
    "Disputado no início da temporada, antes do Brasileirão.",
]


@dataclass
class FaseRegional:
    """Uma fase do torneio: grupos ou mata-mata."""

    nome: str
    tipo: str  # "grupos" | "mata"
    grupos: dict[str, list[Time]] = field(default_factory=dict)
    rodadas: list[int] = field(default_factory=list)
    pares: list[tuple[str, str]] = field(default_factory=list)
    jogos: list[Partida] = field(default_factory=list)
    vencedores: list[Time] = field(default_factory=list)
    concluida: bool = False


class TorneioRegional:
    """Rio-SP, Sul-Minas ou Copa do Nordeste: grupos + mata-mata curto."""

    def __init__(
        self,
        times: list[Time],
        chave: str,
        temporada: int = 2026,
        deslocamento: int = 0,
        semente: int | None = None,
    ):
        chave = str(chave).upper()
        if chave not in REGIONAIS:
            raise ValueError(f"Torneio regional desconhecido: {chave!r}")
        self.chave = chave
        self.regiao = REGIONAIS[chave]
        self.nome = self.regiao.nome
        self.temporada = temporada
        self.engine = MatchEngine()
        self.rng = random.Random(semente)
        self.noticias: list[Noticia] = []
        self.campeao: Time | None = None
        self.vice: Time | None = None
        self._resultados: dict[int, list[Partida]] = {}

        da_regiao = [t for t in times if t.estado in self.regiao.estados]
        ordenados = sorted(da_regiao, key=lambda t: (-t.reputacao, t.nome))[:12]
        if len(ordenados) < 8:
            raise ValueError(
                f"{self.nome} precisa de 8 clubes da região; há {len(ordenados)}."
            )
        self.times = ordenados
        self._por_nome: dict[str, Time] = {t.nome: t for t in ordenados}

        self.grupos = self._distribuir_grupos(ordenados)
        self.datas = [deslocamento + i for i in range(1, 8)]
        self._calendario_grupos = self._calendario_dos_grupos()
        self.fases: list[FaseRegional] = [
            FaseRegional(
                nome="Fase de grupos",
                tipo="grupos",
                grupos=self.grupos,
                rodadas=self.datas[:3],
            )
        ]
        self._jogo_atual = 0

    # ---- montagem ----------------------------------------------------
    @staticmethod
    def _distribuir_grupos(times: list[Time]) -> dict[str, list[Time]]:
        """Serpente: os mais fortes espalhados nos grupos A, B e C."""
        letras = "ABC"
        n_grupos = 3 if len(times) >= 12 else 2
        grupos: dict[str, list[Time]] = {letra: [] for letra in letras[:n_grupos]}
        for i, time in enumerate(times):
            indice = i % n_grupos
            letra = letras[indice] if (i // n_grupos) % 2 == 0 else letras[:n_grupos][::-1][indice]
            grupos[letra].append(time)
        return grupos

    def _calendario_dos_grupos(self) -> list[list[tuple[str, str, str]]]:
        rodadas: list[list[tuple[str, str, str]]] = [[], [], []]
        for letra, clubes in self.grupos.items():
            tabela = _round_robin([t.nome for t in clubes], ida_e_volta=False)
            for i, jogos in enumerate(tabela[:3]):
                rodadas[i].extend((letra, casa, fora) for casa, fora in jogos)
        return rodadas

    # ---- situação ----------------------------------------------------
    @property
    def fase_atual(self) -> FaseRegional:
        return self.fases[-1]

    @property
    def rodada_atual(self) -> int:
        if self._jogo_atual >= len(self.datas):
            return self.datas[-1]
        return self.datas[self._jogo_atual]

    @property
    def total_rodadas(self) -> int:
        return 7

    @property
    def encerrada(self) -> bool:
        return self.campeao is not None

    @property
    def resultados(self) -> dict[int, list[Partida]]:
        return self._resultados

    # ---- tabela ------------------------------------------------------
    def tabela(self, grupo: str) -> list[dict]:
        clubes = self.grupos.get(grupo, [])
        dados: dict[str, dict] = {
            t.nome: {
                "time": t,
                "pts": 0,
                "j": 0,
                "v": 0,
                "e": 0,
                "d": 0,
                "gp": 0,
                "gc": 0,
                "sg": 0,
            }
            for t in clubes
        }
        for partidas in self._resultados.values():
            for partida in partidas:
                if partida.fase != "Fase de grupos" or partida.grupo != grupo:
                    continue
                for nome, pro, contra in (
                    (partida.time_casa, partida.gols_casa, partida.gols_fora),
                    (partida.time_fora, partida.gols_fora, partida.gols_casa),
                ):
                    linha = dados.get(nome)
                    if linha is None:
                        continue
                    linha["j"] += 1
                    linha["gp"] += pro
                    linha["gc"] += contra
                    if pro > contra:
                        linha["v"] += 1
                        linha["pts"] += 3
                    elif pro < contra:
                        linha["d"] += 1
                    else:
                        linha["e"] += 1
                        linha["pts"] += 1
        for linha in dados.values():
            linha["sg"] = linha["gp"] - linha["gc"]
        return sorted(
            dados.values(),
            key=lambda x: (-x["pts"], -x["v"], -x["sg"], -x["gp"], x["time"].nome),
        )

    def classificados(self) -> list[Time]:
        """8 classificados: 2 por grupo + os 2 melhores terceiros."""
        primeiros: list[Time] = []
        segundos: list[Time] = []
        terceiros: list[tuple[dict, Time]] = []
        for letra in sorted(self.grupos):
            tabela = self.tabela(letra)
            if len(tabela) >= 1:
                primeiros.append(tabela[0]["time"])
            if len(tabela) >= 2:
                segundos.append(tabela[1]["time"])
            if len(tabela) >= 3:
                terceiros.append((tabela[2], tabela[2]["time"]))
        terceiros.sort(key=lambda x: (-x[0]["pts"], -x[0]["sg"], -x[0]["gp"]))
        vagas = 8 - len(primeiros) - len(segundos)
        return primeiros + segundos + [t for _, t in terceiros[: max(0, vagas)]]

    # ---- simulação ---------------------------------------------------
    def simular_rodada_global(
        self, rodada: int, time_jogador: str = ""
    ) -> list[Partida]:
        """Joga o jogo do torneio que cai nesta rodada da temporada."""
        if self.encerrada or self._jogo_atual >= len(self.datas):
            return []
        if self.datas[self._jogo_atual] > rodada:
            return []
        indice = self._jogo_atual
        if indice < 3:
            jogos = self._jogar_grupos(indice, rodada, time_jogador)
        elif indice == 3:
            jogos = self._jogar_mata(rodada, time_jogador)
        elif indice == 4:
            jogos = self._jogar_mata(rodada, time_jogador)
        else:
            jogos = self._jogar_final(rodada, time_jogador)
        self._jogo_atual += 1
        return jogos

    def _jogar_grupos(
        self, indice: int, rodada: int, time_jogador: str
    ) -> list[Partida]:
        fase = self.fases[0]
        jogos: list[Partida] = []
        for grupo, casa, fora in self._calendario_grupos[indice]:
            partida = self._simular(casa, fora, rodada, time_jogador)
            partida.fase = fase.nome
            partida.grupo = grupo
            fase.jogos.append(partida)
            jogos.append(partida)
        self._resultados.setdefault(rodada, []).extend(jogos)
        if indice == 2:
            fase.concluida = True
            self.fases.append(
                FaseRegional(
                    nome=NOMES_MATA[8],
                    tipo="mata",
                    rodadas=self.datas[3:4],
                )
            )
        return jogos

    def _jogar_mata(self, rodada: int, time_jogador: str) -> list[Partida]:
        fase = self.fase_atual
        if not fase.pares:
            participantes = (
                self.classificados()
                if fase.nome == NOMES_MATA[8]
                else self.fases[-2].vencedores
            )
            fase.pares = self._chavear(participantes)
        jogos: list[Partida] = []
        for casa, fora in fase.pares:
            partida = self._simular(casa, fora, rodada, time_jogador)
            partida.fase = fase.nome
            partida.grupo = "Jogo único"
            partida.eventos.insert(0, f"🏆 {self.nome} · {fase.nome}")
            fase.jogos.append(partida)
            jogos.append(partida)
        self._resultados.setdefault(rodada, []).extend(jogos)
        if len(fase.rodadas) == 1:
            self._resolver_jogo_unico(fase)
            if len(fase.vencedores) == 4:
                self.fases.append(
                    FaseRegional(
                        nome=NOMES_MATA[4], tipo="mata", rodadas=self.datas[4:5]
                    )
                )
            elif len(fase.vencedores) == 2:
                self.fases.append(
                    FaseRegional(
                        nome=NOMES_MATA[2], tipo="mata", rodadas=self.datas[5:7]
                    )
                )
        return jogos

    def _jogar_final(self, rodada: int, time_jogador: str) -> list[Partida]:
        fase = self.fase_atual
        finalistas = self.fases[-2].vencedores
        if not finalistas:
            return []
        forte, fraco = (
            (finalistas[0], finalistas[1])
            if finalistas[0].reputacao >= finalistas[1].reputacao
            else (finalistas[1], finalistas[0])
        )
        perna = len(fase.jogos) // 2
        casa, fora = (fraco, forte) if perna == 0 else (forte, fraco)
        partida = self._simular(casa.nome, fora.nome, rodada, time_jogador)
        partida.fase = fase.nome
        partida.grupo = "Volta" if perna else "Ida"
        partida.eventos.insert(0, f"🏆 {self.nome} · Final · jogo de {partida.grupo.lower()}")
        fase.jogos.append(partida)
        self._resultados.setdefault(rodada, []).extend([partida])

        if len(fase.jogos) >= 2:
            fase.concluida = True
            gols_forte = gols_fraco = 0
            for jogo in fase.jogos:
                if jogo.time_casa == forte.nome:
                    gols_forte += jogo.gols_casa
                    gols_fraco += jogo.gols_fora
                else:
                    gols_forte += jogo.gols_fora
                    gols_fraco += jogo.gols_casa
            if gols_forte == gols_fraco:
                vencedor = self._penaltis(forte, fraco)
                fase.jogos[-1].eventos.append(
                    f"🥅 Pênaltis: {vencedor.nome} vence a final"
                )
            else:
                vencedor = forte if gols_forte > gols_fraco else fraco
            self.campeao = vencedor
            self.vice = fraco if vencedor is forte else forte
            fase.vencedores = [vencedor]
            self.noticias.append(
                Noticia(
                    titulo=f"🏆 {vencedor.nome} é campeão do {self.nome}!",
                    texto=f"{vencedor.nome} venceu o {self.nome} de {self.temporada}.",
                    rodada=rodada,
                    tipo="geral",
                )
            )
        return [partida]

    def _resolver_jogo_unico(self, fase: FaseRegional) -> None:
        vencedores: list[Time] = []
        for casa, fora in fase.pares:
            partida = next(
                (
                    p
                    for p in fase.jogos
                    if p.time_casa == casa and p.time_fora == fora
                ),
                None,
            )
            a, b = self._por_nome[casa], self._por_nome[fora]
            if partida is None:
                vencedores.append(a)
                continue
            if partida.gols_casa == partida.gols_fora:
                vencedor = self._penaltis(a, b)
                partida.eventos.append(f"🥅 Pênaltis: {vencedor.nome} avança")
            else:
                vencedor = a if partida.gols_casa > partida.gols_fora else b
            vencedores.append(vencedor)
        fase.vencedores = vencedores

    @staticmethod
    def _chavear(participantes: list[Time]) -> list[tuple[str, str]]:
        """1º x 8º, 2º x 7º, 3º x 6º, 4º x 5º (mando do melhor)."""
        pares: list[tuple[str, str]] = []
        metade = len(participantes) // 2
        for i in range(metade):
            pares.append((participantes[i].nome, participantes[-1 - i].nome))
        return pares

    def _simular(
        self, casa: str, fora: str, rodada: int, time_jogador: str
    ) -> Partida:
        return self.engine.simular(
            self._por_nome[casa],
            self._por_nome[fora],
            rodada,
            is_player_home=(casa == time_jogador),
            is_player_away=(fora == time_jogador),
        )

    def _penaltis(self, a: Time, b: Time) -> Time:
        p = 0.5 + (a.overall_time - b.overall_time) / 300
        p = max(0.2, min(0.8, p))
        return a if self.rng.random() < p else b

    # ---- consultas ---------------------------------------------------
    def partida(self, rodada: int, casa: str, fora: str) -> Partida | None:
        for partida in self._resultados.get(rodada, []):
            if partida.time_casa == casa and partida.time_fora == fora:
                return partida
        return None

    def confrontos_da_rodada(
        self, rodada: int
    ) -> list[tuple[str, str, Partida | None]]:
        """Jogos marcados (ou disputados) numa rodada da temporada."""
        jogados: list[tuple[str, str, Partida | None]] = [
            (p.time_casa, p.time_fora, p) for p in self._resultados.get(rodada, [])
        ]
        if jogados:
            return jogados
        if rodada in self.datas:
            indice = self.datas.index(rodada)
            if indice == self._jogo_atual and indice < 3:
                return [
                    (casa, fora, None)
                    for _, casa, fora in self._calendario_grupos[indice]
                ]
            fase = self.fase_atual
            if indice >= 3 and fase.pares and len(fase.rodadas) == 1:
                return [(casa, fora, None) for casa, fora in fase.pares if fora]
        return []

    def jogos_do_time(
        self, nome: str
    ) -> list[tuple[int, str, str, Partida | None]]:
        """Jogos do clube no torneio: ``(rodada, casa, fora, partida)``."""
        jogos: list[tuple[int, str, str, Partida | None]] = []
        for rodada, partidas in sorted(self._resultados.items()):
            for partida in partidas:
                if nome in (partida.time_casa, partida.time_fora):
                    jogos.append(
                        (rodada, partida.time_casa, partida.time_fora, partida)
                    )
        return jogos

    def proximo_jogo(self, nome: str) -> tuple[int, str, str] | None:
        """Próximo jogo do clube (``None`` se já foi eliminado ou acabou)."""
        if self.encerrada or self._jogo_atual >= len(self.datas):
            return None
        indice = self._jogo_atual
        rodada = self.datas[indice]
        if indice < 3:
            for _, casa, fora in self._calendario_grupos[indice]:
                if nome in (casa, fora):
                    return (rodada, casa, fora)
            return None
        fase = self.fase_atual
        if fase.nome == NOMES_MATA[2]:
            finalistas = self.fases[-2].vencedores
            if nome not in (t.nome for t in finalistas):
                return None
            forte, fraco = sorted(
                finalistas, key=lambda t: (-t.reputacao, t.nome)
            )
            perna = len(fase.jogos) // 2
            casa, fora = (fraco, forte) if perna == 0 else (forte, fraco)
            return (rodada, casa.nome, fora.nome)
        if not fase.pares:
            if fase.nome == NOMES_MATA[8]:
                participantes = self.classificados()
                if nome not in (t.nome for t in participantes):
                    return None
                pares = self._chavear(participantes)
            else:
                vencedores = self.fases[-2].vencedores
                if nome not in (t.nome for t in vencedores):
                    return None
                pares = self._chavear(vencedores)
        else:
            pares = fase.pares
        for casa, fora in pares:
            if nome in (casa, fora):
                return (rodada, casa, fora)
        return None

    def artilharia(self, top: int = 10) -> list[tuple[Jogador, str]]:
        artilheiros = [
            (jogador, time.sigla)
            for time in self.times
            for jogador in time.jogadores
            if jogador.gols > 0
        ]
        artilheiros.sort(key=lambda x: (-x[0].gols, -x[0].assistencias))
        return artilheiros[:top]

    def resumo(self) -> str:
        if self.campeao is not None:
            return f"{self.nome}: campeão {self.campeao.nome}"
        return (
            f"{self.nome}: {self.fase_atual.nome} · "
            f"jogo {min(self._jogo_atual + 1, len(self.datas))}/{len(self.datas)}"
        )
