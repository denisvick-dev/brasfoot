"""
Competições personalizadas.

Três formatos:

* ``pontos_corridos``  — todos contra todos (turno e returno opcional)
* ``copa``             — mata-mata com chaves de ida e volta (final opcionalmente única)
* ``grupos_mata``      — fase de grupos + eliminatórias

Uso rápido
----------
>>> from game.competicoes import Campeonato
>>> camp = Campeonato("Copa do Brasil", times, formato="copa")
>>> camp.avancar()          # simula a próxima rodada/fase
>>> camp.tabela()           # classificação (pontos corridos / grupos)
>>> camp.encerrado, camp.campeao
>>> camp.salvar()           # salva em dados/campeonatos.json
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable

from game import persistencia
from game.jogo_engine import MatchEngine
from game.modelos import Partida, Time

FORMATOS = {
    "pontos_corridos": "Pontos corridos (todos contra todos)",
    "copa": "Copa (mata-mata)",
    "grupos_mata": "Grupos + eliminatórias",
}

NOMES_MATA = {
    2: "Final",
    4: "Semifinal",
    8: "Quartas de final",
    16: "Oitavas de final",
    32: "Dezesseis-avos",
    64: "Trinta e dois-avos",
}

LETRAS_GRUPOS = "ABCDEFGHIJKL"


# ============================================================
# Estruturas
# ============================================================
@dataclass
class Confronto:
    """Um confronto de mata-mata (1 ou 2 jogos)."""

    a: Time | None = None
    b: Time | None = None
    jogos: list[Partida] = field(default_factory=list)
    vencedor: Time | None = None

    def gols(self, time: Time) -> int:
        total = 0
        for p in self.jogos:
            if p.time_casa == time.nome:
                total += p.gols_casa
            elif p.time_fora == time.nome:
                total += p.gols_fora
        return total


@dataclass
class Fase:
    """Uma fase da competição: grupos (com rodadas) ou mata-mata (com chaves)."""

    nome: str
    tipo: str  # "grupos" | "mata"
    grupos: dict[str, list[Time]] = field(default_factory=dict)
    rodadas: list[list[tuple[str, str, str]]] = field(default_factory=list)
    rodada_atual: int = 0
    confrontos: list[Confronto] = field(default_factory=list)
    jogos: list[Partida] = field(default_factory=list)
    classificados: int = 0
    ida_e_volta: bool = False
    concluida: bool = False

    @property
    def total_rodadas(self) -> int:
        return len(self.rodadas)


def _round_robin(nomes: list[str], ida_e_volta: bool = True) -> list[list[tuple[str, str]]]:
    """Gera as rodadas de um todos-contra-todos (algoritmo circle method)."""
    times = list(nomes)
    bye = None
    if len(times) % 2:
        bye = "__BYE__"
        times.append(bye)

    n = len(times)
    fixo, rotativos = times[0], times[1:]
    rodadas = []

    for r in range(n - 1):
        atual = [fixo] + rotativos
        jogos = []
        for i in range(n // 2):
            casa, fora = atual[i], atual[n - 1 - i]
            if casa == bye or fora == bye:
                continue
            jogos.append((casa, fora) if r % 2 == 0 else (fora, casa))
        rodadas.append(jogos)
        rotativos = [rotativos[-1]] + rotativos[:-1]

    if ida_e_volta:
        primeiro_turno = rodadas[:]
        rodadas += [[(fora, casa) for casa, fora in jogos] for jogos in primeiro_turno]

    return rodadas


def _proxima_potencia_de_dois(n: int) -> int:
    size = 1
    while size < n:
        size *= 2
    return size


def _nome_fase_mata(n_times: int) -> str:
    return NOMES_MATA.get(n_times, f"Fase de {n_times}")


# ============================================================
# Campeonato
# ============================================================
class Campeonato:
    """Gerencia uma competição personalizada."""

    def __init__(
        self,
        nome: str,
        times: list[Time],
        formato: str = "pontos_corridos",
        temporada: int = 2024,
        ida_e_volta: bool = True,
        n_grupos: int = 4,
        classificados_por_grupo: int = 2,
        promovidos: int = 0,
        rebaixados: int = 0,
        final_unica: bool = True,
        semente: int | None = None,
    ):
        if not nome:
            raise ValueError("O campeonato precisa de um nome.")
        if len(times) < 2:
            raise ValueError("É preciso de ao menos 2 times.")
        if formato not in FORMATOS:
            raise ValueError(f"Formato inválido: {formato!r}. Use um de {list(FORMATOS)}.")

        self.nome = nome
        self.times = list(times)
        self.formato = formato
        self.temporada = temporada
        self.ida_e_volta = ida_e_volta
        self.n_grupos = n_grupos
        self.classificados_por_grupo = classificados_por_grupo
        self.promovidos = promovidos
        self.rebaixados = rebaixados
        self.final_unica = final_unica

        self.engine = MatchEngine()
        self.rng = random.Random(semente)
        self.fases: list[Fase] = []
        self.fase_idx = 0
        self.resultados: list[Partida] = []
        self.campeao: Time | None = None
        self._por_nome: dict[str, Time] = {t.nome: t for t in self.times}

        self._montar()

    # ---- estado -----------------------------------------------------
    @property
    def encerrado(self) -> bool:
        return self.fase_idx >= len(self.fases)

    @property
    def fase_atual(self) -> Fase | None:
        return None if self.encerrado else self.fases[self.fase_idx]

    @property
    def progresso(self) -> str:
        if self.encerrado:
            return "Encerrado"
        fase = self.fase_atual
        if fase.tipo == "grupos":
            return f"{fase.nome}: rodada {fase.rodada_atual}/{fase.total_rodadas}"
        return f"{fase.nome}: {len(fase.confrontos)} confronto(s)"

    @property
    def botao_avancar(self) -> str:
        """Rótulo do botão de avanço conforme a fase atual."""
        fase = self.fase_atual
        if fase is None:
            return "Encerrado"
        if fase.tipo == "grupos":
            return "▶️ Simular próxima rodada"
        return f"▶️ Simular {fase.nome}"

    # ---- montagem ---------------------------------------------------
    def _montar(self):
        if self.formato == "copa":
            self._montar_copa()
        elif self.formato == "grupos_mata":
            self._montar_grupos_mata()
        else:
            self._montar_pontos_corridos()

    def _montar_pontos_corridos(self):
        nomes = [t.nome for t in self.times]
        rodadas = _round_robin(nomes, ida_e_volta=self.ida_e_volta)
        fase = Fase(
            nome="Pontos corridos",
            tipo="grupos",
            grupos={"Geral": list(self.times)},
            rodadas=[[("", casa, fora) for casa, fora in jogos] for jogos in rodadas],
            classificados=0,
            ida_e_volta=self.ida_e_volta,
        )
        self.fases = [fase]

    def _fases_mata(self, n_times: int, primeira_eh_grupos: bool) -> list[Fase]:
        fases = []
        restantes = n_times
        while restantes >= 2:
            fases.append(
                Fase(
                    nome=_nome_fase_mata(restantes),
                    tipo="mata",
                    confrontos=[Confronto() for _ in range(restantes // 2)],
                    ida_e_volta=True,
                )
            )
            restantes //= 2
        for fase in fases[:-1]:
            fase.ida_e_volta = self.ida_e_volta
        fases[-1].ida_e_volta = not self.final_unica
        return fases

    def _montar_copa(self):
        size = _proxima_potencia_de_dois(len(self.times))
        participantes = list(self.times) + [None] * (size - len(self.times))
        self.rng.shuffle(participantes)

        self.fases = self._fases_mata(size, primeira_eh_grupos=False)
        for i, confronto in enumerate(self.fases[0].confrontos):
            confronto.a = participantes[2 * i]
            confronto.b = participantes[2 * i + 1]

    def _montar_grupos_mata(self):
        times = list(self.times)
        self.rng.shuffle(times)

        n_grupos = max(2, min(self.n_grupos, len(times) // 2))
        grupos: dict[str, list[Time]] = {LETRAS_GRUPOS[i]: [] for i in range(n_grupos)}
        for i, time in enumerate(times):  # distribuição "snake"
            ordem = list(grupos)
            if (i // n_grupos) % 2 == 0:
                grupos[ordem[i % n_grupos]].append(time)
            else:
                grupos[ordem[::-1][i % n_grupos]].append(time)

        fase_grupos = Fase(
            nome="Fase de grupos",
            tipo="grupos",
            grupos=grupos,
            classificados=max(1, self.classificados_por_grupo),
            ida_e_volta=True,
        )
        fase_grupos.rodadas = self._rodadas_para(fase_grupos)

        total_classificados = n_grupos * fase_grupos.classificados
        size = _proxima_potencia_de_dois(total_classificados)
        self.fases = [fase_grupos] + self._fases_mata(size, primeira_eh_grupos=True)
        self.n_grupos = n_grupos

    def _rodadas_para(self, fase: Fase) -> list[list[tuple[str, str, str]]]:
        """Reconstrói as rodadas de uma fase de grupos a partir dos grupos."""
        por_grupo = {}
        for grupo, times in fase.grupos.items():
            por_grupo[grupo] = _round_robin([t.nome for t in times], fase.ida_e_volta)

        total = max((len(r) for r in por_grupo.values()), default=0)
        rodadas: list[list[tuple[str, str, str]]] = [[] for _ in range(total)]
        for grupo, rodadas_grupo in por_grupo.items():
            for i, jogos in enumerate(rodadas_grupo):
                rodadas[i] += [(grupo, casa, fora) for casa, fora in jogos]
        return rodadas

    # ---- simulação --------------------------------------------------
    def avancar(self) -> list[Partida]:
        """Simula a próxima rodada (grupos) ou a fase inteira (mata-mata)."""
        if self.encerrado:
            return []
        fase = self.fase_atual
        if fase.tipo == "grupos":
            jogos = self._jogar_rodada(fase)
            if fase.rodada_atual >= fase.total_rodadas:
                self._concluir_grupos(fase)
            return jogos
        return self._jogar_mata(fase)

    def simular_tudo(self) -> int:
        """Simula o campeonato inteiro. Devolve o número de partidas."""
        n = 0
        while not self.encerrado:
            n += len(self.avancar())
        return n

    def _simular(self, casa: str, fora: str, rodada: int, fase: str, grupo: str) -> Partida:
        t_casa, t_fora = self._por_nome[casa], self._por_nome[fora]
        partida = self.engine.simular(t_casa, t_fora, rodada)
        partida.fase = fase
        partida.grupo = grupo
        self.resultados.append(partida)
        return partida

    def _jogar_rodada(self, fase: Fase) -> list[Partida]:
        rodada = fase.rodadas[fase.rodada_atual]
        fase.rodada_atual += 1
        jogos = []
        for grupo, casa, fora in rodada:
            partida = self._simular(
                casa, fora, rodada=fase.rodada_atual, fase=fase.nome, grupo=grupo
            )
            fase.jogos.append(partida)
            jogos.append(partida)
        return jogos

    def _concluir_grupos(self, fase: Fase):
        fase.concluida = True
        proxima = self.fases[self.fase_idx + 1] if self.fase_idx + 1 < len(self.fases) else None
        if proxima is None:
            tabela = self.tabela(fase)
            self.campeao = tabela[0]["time"] if tabela else None
        else:
            self._popular_mata(proxima, self._classificados_dos_grupos(fase))
        self.fase_idx += 1

    def _jogar_mata(self, fase: Fase) -> list[Partida]:
        jogos = []
        for confronto in fase.confrontos:
            if confronto.a is None and confronto.b is None:
                continue
            if confronto.b is None:
                confronto.vencedor = confronto.a  # folga (BYE)
                continue
            if confronto.a is None:
                confronto.vencedor = confronto.b
                continue

            ida = self._simular(confronto.a.nome, confronto.b.nome, 1, fase.nome, "")
            confronto.jogos.append(ida)
            jogos.append(ida)

            if fase.ida_e_volta:
                volta = self._simular(confronto.b.nome, confronto.a.nome, 2, fase.nome, "")
                confronto.jogos.append(volta)
                jogos.append(volta)

            confronto.vencedor = self._vencedor_confronto(confronto)

        fase.concluida = True
        proxima = self.fases[self.fase_idx + 1] if self.fase_idx + 1 < len(self.fases) else None
        if proxima is None:
            self.campeao = fase.confrontos[0].vencedor
        else:
            self._popular_mata(
                proxima, [c.vencedor for c in fase.confrontos if c.vencedor]
            )
        self.fase_idx += 1
        return jogos

    def _vencedor_confronto(self, confronto: Confronto) -> Time:
        a, b = confronto.a, confronto.b
        gols_a, gols_b = confronto.gols(a), confronto.gols(b)
        if gols_a > gols_b:
            return a
        if gols_b > gols_a:
            return b

        # empate no agregado: pênaltis (probabilidade levemente favorável ao
        # time de maior overall)
        p = 0.5 + (a.overall_time - b.overall_time) / 300
        p = max(0.2, min(0.8, p))
        vencedor, perdedor = (a, b) if random.random() < p else (b, a)

        placar_v, placar_p = (4, 3) if random.random() < 0.7 else (5, 4)
        if confronto.jogos:
            confronto.jogos[-1].eventos.append(
                f"🥅 Pênaltis: {vencedor.nome} vence por {placar_v} x {placar_p}"
            )
        return vencedor

    def _popular_mata(self, fase: Fase, classificados: list[Time]):
        """Preenche as chaves cruzando os classificados (1º x último, etc.)."""
        size = len(fase.confrontos) * 2
        for i, confronto in enumerate(fase.confrontos):
            ia, ib = i, size - 1 - i
            confronto.a = classificados[ia] if ia < len(classificados) else None
            confronto.b = (
                classificados[ib] if (ib < len(classificados) and ib > ia) else None
            )

    def _classificados_dos_grupos(self, fase: Fase) -> list[Time]:
        tabelas = {g: self.tabela(fase, g) for g in sorted(fase.grupos)}
        classificados = []
        for pos in range(fase.classificados):
            for grupo in sorted(fase.grupos):
                tabela = tabelas[grupo]
                if pos < len(tabela):
                    classificados.append(tabela[pos]["time"])
        return classificados

    # ---- consultas --------------------------------------------------
    def tabela(self, fase: Fase | None = None, grupo: str | None = None) -> list[dict]:
        """Classificação de uma fase de grupos (ou de um grupo específico)."""
        fase = fase or self.fases[min(self.fase_idx, len(self.fases) - 1)]
        if fase.tipo != "grupos":
            return []

        if grupo:
            times = fase.grupos.get(grupo, [])
        else:
            times = [t for g in fase.grupos.values() for t in g]

        dados = {
            t.nome: dict(time=t, pts=0, j=0, v=0, e=0, d=0, gp=0, gc=0) for t in times
        }

        jogos = [
            p
            for p in fase.jogos
            if p.jogada and (grupo is None or p.grupo == grupo)
        ]
        for p in jogos:
            lados = (
                (p.time_casa, p.gols_casa, p.gols_fora),
                (p.time_fora, p.gols_fora, p.gols_casa),
            )
            for nome, pro, contra in lados:
                if nome not in dados:
                    continue
                linha = dados[nome]
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
            if grupo is None and p.grupo:
                pass

        for linha in dados.values():
            linha["sg"] = linha["gp"] - linha["gc"]

        return sorted(
            dados.values(),
            key=lambda x: (-x["pts"], -x["v"], -x["sg"], -x["gp"], x["time"].nome),
        )

    def grupos_da_fase(self, fase: Fase | None = None) -> list[str]:
        fase = fase or self.fase_atual
        return sorted(fase.grupos) if fase and fase.tipo == "grupos" else []

    def artilharia(self, top: int = 10) -> list[tuple]:
        jogadores = []
        for time in self.times:
            for j in time.jogadores:
                if j.gols > 0:
                    jogadores.append((j, time.sigla))
        jogadores.sort(key=lambda x: (-x[0].gols, -x[0].assistencias))
        return jogadores[:top]

    def resumo_final(self) -> dict:
        """Resumo do campeonato (campeão, promovidos e rebaixados)."""
        tabela = self.tabela(self.fases[0]) if self.fases else []
        return {
            "campeao": self.campeao or (tabela[0]["time"] if tabela else None),
            "promovidos": [l["time"] for l in tabela[: self.promovidos]],
            "rebaixados": [l["time"] for l in tabela[-self.rebaixados :]]
            if self.rebaixados
            else [],
            "tabela": tabela,
        }

    def jogos_da_fase(self, fase_idx: int | None = None) -> list[Partida]:
        idx = self.fase_idx if fase_idx is None else fase_idx
        if idx >= len(self.fases):
            return []
        fase = self.fases[idx]
        if fase.tipo == "mata":
            return [p for c in fase.confrontos for p in c.jogos]
        return list(fase.jogos)

    # ---- persistência -----------------------------------------------
    def to_dict(self) -> dict:
        resultados = []
        for fi, fase in enumerate(self.fases):
            if fase.tipo == "mata":
                for ci, confronto in enumerate(fase.confrontos):
                    for oi, p in enumerate(confronto.jogos):
                        resultados.append(
                            self._partida_para_dict(p, fi, grupo="", confronto=ci, ordem=oi)
                        )
            else:
                for p in fase.jogos:
                    resultados.append(
                        self._partida_para_dict(
                            p, fi, grupo=p.grupo, confronto=-1, ordem=-1
                        )
                    )

        return {
            "nome": self.nome,
            "formato": self.formato,
            "temporada": self.temporada,
            "ida_e_volta": self.ida_e_volta,
            "n_grupos": self.n_grupos,
            "classificados_por_grupo": self.classificados_por_grupo,
            "promovidos": self.promovidos,
            "rebaixados": self.rebaixados,
            "final_unica": self.final_unica,
            "fase_idx": self.fase_idx,
            "campeao": self.campeao.nome if self.campeao else None,
            "times": [t.nome for t in self.times],
            "fases": [
                {
                    "nome": f.nome,
                    "tipo": f.tipo,
                    "classificados": f.classificados,
                    "ida_e_volta": f.ida_e_volta,
                    "concluida": f.concluida,
                    "rodada_atual": f.rodada_atual,
                    "grupos": {
                        g: [t.nome for t in ts] for g, ts in f.grupos.items()
                    },
                    "confrontos": [
                        [
                            c.a.nome if c.a else None,
                            c.b.nome if c.b else None,
                            c.vencedor.nome if c.vencedor else None,
                        ]
                        for c in f.confrontos
                    ],
                }
                for f in self.fases
            ],
            "resultados": resultados,
        }

    @staticmethod
    def _partida_para_dict(
        p: Partida, fase_idx: int, grupo: str, confronto: int, ordem: int
    ) -> dict:
        return {
            "fase_idx": fase_idx,
            "grupo": grupo,
            "confronto": confronto,
            "ordem": ordem,
            "rodada": p.rodada,
            "time_casa": p.time_casa,
            "time_fora": p.time_fora,
            "gols_casa": p.gols_casa,
            "gols_fora": p.gols_fora,
            "publico": p.publico,
            "fase": p.fase,
        }

    @classmethod
    def de_dict(cls, dados: dict, resolver: Callable[[str], Time | None]) -> "Campeonato":
        """Reconstrói um campeonato salvo. ``resolver`` converte nome -> Time."""
        times = [t for t in (resolver(n) for n in dados["times"]) if t]
        camp = cls(
            nome=dados["nome"],
            times=times,
            formato=dados["formato"],
            temporada=dados.get("temporada", 2024),
            ida_e_volta=dados.get("ida_e_volta", True),
            n_grupos=dados.get("n_grupos", 4),
            classificados_por_grupo=dados.get("classificados_por_grupo", 2),
            promovidos=dados.get("promovidos", 0),
            rebaixados=dados.get("rebaixados", 0),
            final_unica=dados.get("final_unica", True),
        )

        # fases salvas (substituem o sorteio feito no __init__)
        camp.fases = []
        for fd in dados["fases"]:
            fase = Fase(
                nome=fd["nome"],
                tipo=fd["tipo"],
                classificados=fd["classificados"],
                ida_e_volta=fd["ida_e_volta"],
                concluida=fd["concluida"],
                rodada_atual=fd["rodada_atual"],
            )
            if fase.tipo == "grupos":
                fase.grupos = {
                    g: [t for t in (resolver(n) for n in nomes) if t]
                    for g, nomes in fd["grupos"].items()
                }
                fase.rodadas = camp._rodadas_para(fase)
            else:
                fase.confrontos = [
                    Confronto(
                        a=resolver(a) if a else None,
                        b=resolver(b) if b else None,
                        vencedor=resolver(v) if v else None,
                    )
                    for a, b, v in fd["confrontos"]
                ]
            camp.fases.append(fase)

        # partidas já disputadas
        camp.resultados = []
        for rd in dados.get("resultados", []):
            if rd["fase_idx"] >= len(camp.fases):
                continue
            partida = Partida(
                rodada=rd.get("rodada", 1),
                time_casa=rd["time_casa"],
                time_fora=rd["time_fora"],
                gols_casa=rd["gols_casa"],
                gols_fora=rd["gols_fora"],
                jogada=True,
                publico=rd.get("publico", 0),
                fase=rd.get("fase", ""),
                grupo=rd.get("grupo", ""),
            )
            fase = camp.fases[rd["fase_idx"]]
            if rd.get("confronto", -1) >= 0 and rd["confronto"] < len(fase.confrontos):
                fase.confrontos[rd["confronto"]].jogos.append(partida)
            else:
                fase.jogos.append(partida)
            camp.resultados.append(partida)

        camp.fase_idx = dados.get("fase_idx", 0)
        camp.campeao = resolver(dados["campeao"]) if dados.get("campeao") else None
        return camp

    def salvar(self) -> str:
        """Salva o campeonato (configuração + placares) e devolve o slug."""
        return persistencia.salvar("campeonato", self.nome, self.to_dict())


def campeonatos_salvos() -> list[dict]:
    return persistencia.listar("campeonato")


def excluir_campeonato(slug: str) -> bool:
    return persistencia.excluir("campeonato", slug)
