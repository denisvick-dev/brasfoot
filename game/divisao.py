"""
Temporada de uma divisão, com o regulamento de cada série.

Cada divisão tem o seu formato (e não apenas o velho turno e returno):

* **Série A / Série B** — turno único (todos contra todos); os **8 melhores**
  vão para a segunda fase, em **dois grupos de 4** (turno e returno); os líderes
  de cada grupo disputam a **final em ida e volta**. Na Série B, o **1º e o 2º de
  cada grupo** garantem o acesso à Série A.
* **Série C** — turno único; os **4 primeiros** garantem o acesso.
* **Série D** — formato real: grupos regionais de até 6 clubes em turno único, os
  dois melhores de cada grupo avançam para o mata-mata (16-avos → oitavas →
  quartas → semifinal → final), sempre em ida e volta; os **4 semifinalistas**
  sobem para a Série C.

Uso
---
>>> from game.divisao import TemporadaDivisao
>>> serie_a = TemporadaDivisao(times_da_a, "A")
>>> serie_a.total_rodadas              # 19 + 6 + 2 = 27
>>> serie_a.simular_rodada("Flamengo") # joga a próxima rodada da fase atual
>>> serie_a.fase_atual.nome            # 'Primeira fase' | 'Segunda fase' | 'Final'
>>> serie_a.classificacao[0].nome      # líder da primeira fase
>>> serie_a.campeao.nome, serie_a.promovidos, serie_a.rebaixados
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from game.jogo_engine import MatchEngine
from game.modelos import Jogador, Noticia, Partida, Time

# fases do mata-mata pelo número de clubes na chave
NOMES_MATA = {
    32: "16-avos de final",
    16: "Oitavas de final",
    8: "Quartas de final",
    4: "Semifinal",
    2: "Final",
}

REGULAMENTOS: dict[str, list[str]] = {
    "A": [
        "1ª fase: turno único, todos contra todos (19 rodadas).",
        "Os 8 melhores avançam para a 2ª fase.",
        "2ª fase: dois grupos de 4, em turno e returno (6 rodadas).",
        "Os líderes de cada grupo disputam a final em ida e volta.",
        "Os 4 últimos da 1ª fase são rebaixados para a Série B.",
    ],
    "B": [
        "1ª fase: turno único, todos contra todos (19 rodadas).",
        "Os 8 melhores avançam para a 2ª fase.",
        "2ª fase: dois grupos de 4, em turno e returno (6 rodadas).",
        "O 1º e o 2º de cada grupo garantem o acesso à Série A.",
        "Os líderes de cada grupo disputam a final em ida e volta.",
        "Os 4 últimos da 1ª fase são rebaixados para a Série C.",
    ],
    "C": [
        "Fase única: turno único, todos contra todos (19 rodadas).",
        "Os 4 primeiros garantem o acesso à Série B.",
        "O campeão é o líder da tabela.",
        "Os 4 últimos são rebaixados para a Série D.",
    ],
    "D": [
        "1ª fase: 16 grupos regionais de 6 clubes, em turno único (5 rodadas).",
        "Os dois melhores de cada grupo avançam (32 clubes).",
        "Mata-mata em ida e volta: 16-avos, oitavas, quartas, semifinal e final.",
        "Os 4 semifinalistas sobem para a Série C.",
        "Não há rebaixamento na Série D.",
    ],
}


# ============================================================
# Estruturas
# ============================================================
@dataclass
class Fase:
    """Uma fase da temporada: rodadas, grupos e confrontos."""

    nome: str
    tipo: str  # "pontos" | "grupos" | "mata"
    grupos: dict[str, list[Time]] = field(default_factory=dict)
    rodadas: list[list[tuple[str, str, str]]] = field(default_factory=list)
    ida_e_volta: bool = True
    rodada_atual: int = 0
    jogos: list[Partida] = field(default_factory=list)
    pares: list[tuple[str, str]] = field(default_factory=list)
    vencedores: list[Time] = field(default_factory=list)
    concluida: bool = False

    @property
    def total_rodadas(self) -> int:
        return len(self.rodadas)


# ============================================================
# Helpers de calendário
# ============================================================
def _round_robin(nomes: list[str], ida_e_volta: bool = False) -> list[list[tuple[str, str]]]:
    """Rodadas de um todos-contra-todos (método do círculo)."""
    times = list(nomes)
    valor_bye = None
    if len(times) % 2:
        valor_bye = "__BYE__"
        times.append(valor_bye)

    n = len(times)
    fixo, rotativos = times[0], times[1:]
    rodadas: list[list[tuple[str, str]]] = []

    for r in range(n - 1):
        atual = [fixo] + rotativos
        jogos = []
        for i in range(n // 2):
            casa, fora = atual[i], atual[n - 1 - i]
            if casa == valor_bye or fora == valor_bye:
                continue
            jogos.append((casa, fora) if r % 2 == 0 else (fora, casa))
        rodadas.append(jogos)
        rotativos = [rotativos[-1]] + rotativos[:-1]

    if ida_e_volta:
        primeiro = rodadas[:]
        rodadas += [[(fora, casa) for casa, fora in jogos] for jogos in primeiro]
    return rodadas


def _fase_pontos(nome: str, times: list[Time], ida_e_volta: bool = False) -> Fase:
    """Fase de tabela única (todos contra todos)."""
    rodadas = _round_robin([t.nome for t in times], ida_e_volta=ida_e_volta)
    return Fase(
        nome=nome,
        tipo="pontos",
        grupos={"Geral": list(times)},
        rodadas=[[("Geral", casa, fora) for casa, fora in jogos] for jogos in rodadas],
        ida_e_volta=ida_e_volta,
    )


def _fase_grupos(
    nome: str, grupos: dict[str, list[Time]], ida_e_volta: bool = False
) -> Fase:
    """Fase de grupos: cada grupo joga entre si."""
    por_grupo = {
        letra: _round_robin([t.nome for t in clubes], ida_e_volta=ida_e_volta)
        for letra, clubes in grupos.items()
    }
    total = max((len(r) for r in por_grupo.values()), default=0)
    rodadas: list[list[tuple[str, str, str]]] = [[] for _ in range(total)]
    for letra, rodadas_grupo in por_grupo.items():
        for i, jogos in enumerate(rodadas_grupo):
            rodadas[i] += [(letra, casa, fora) for casa, fora in jogos]
    return Fase(
        nome=nome,
        tipo="grupos",
        grupos={k: list(v) for k, v in grupos.items()},
        rodadas=rodadas,
        ida_e_volta=ida_e_volta,
    )


def _fase_mata(nome: str, pares: list[tuple[str, str]], ida_e_volta: bool = True) -> Fase:
    """Fase eliminatória: uma rodada de ida e uma de volta."""
    rodadas = [[(nome, casa, fora) for casa, fora in pares]]
    if ida_e_volta:
        rodadas.append([(nome, fora, casa) for casa, fora in pares])
    return Fase(
        nome=nome,
        tipo="mata",
        rodadas=rodadas,
        pares=pares,
        ida_e_volta=ida_e_volta,
    )


def _distribuir_grupos(times: list[Time], n_grupos: int) -> dict[str, list[Time]]:
    """Distribui os clubes em grupos equilibrados (formato serpente)."""
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:n_grupos]
    grupos: dict[str, list[Time]] = {letra: [] for letra in letras}
    for i, time in enumerate(times):
        if (i // n_grupos) % 2 == 0:
            grupos[letras[i % n_grupos]].append(time)
        else:
            grupos[letras[::-1][i % n_grupos]].append(time)
    return grupos


# ============================================================
# Temporada da divisão
# ============================================================
class TemporadaDivisao:
    """Uma divisão jogando o seu regulamento, rodada a rodada."""

    def __init__(
        self,
        times: list[Time],
        divisao: str = "A",
        temporada: int = 2026,
        semente: int | None = None,
    ):
        if len(times) < 2:
            raise ValueError("É preciso de ao menos 2 clubes para montar a divisão.")
        self.divisao = str(divisao).upper()
        self.times = list(times)
        self.temporada = temporada
        self.engine = MatchEngine()
        self.rng = random.Random(semente)
        self.noticias: list[Noticia] = []
        self.fases: list[Fase] = []
        self.campeao: Time | None = None
        self._promovidos: list[Time] = []
        self._rebaixados: list[Time] = []
        self._resultados: dict[int, list[Partida]] = {}
        self._encerrada = False
        self._por_nome: dict[str, Time] = {t.nome: t for t in self.times}

        self.fases = [self._fase_inicial()]
        self._total_previsto = self._planejar_rodadas()

    # ---- regras -----------------------------------------------------
    @property
    def acesso(self) -> int:
        return {"B": 4, "C": 4, "D": 4}.get(self.divisao, 0)

    @property
    def descenso(self) -> int:
        return {"A": 4, "B": 4, "C": 4}.get(self.divisao, 0)

    @property
    def promovidos(self) -> list[Time]:
        return list(self._promovidos)

    @property
    def rebaixados(self) -> list[Time]:
        return list(self._rebaixados)

    # ---- montagem ---------------------------------------------------
    def _fase_inicial(self) -> Fase:
        if self.divisao == "D":
            n = len(self.times)
            # grupos de até 6; a quantidade é potência de 2 para a chave fechar
            n_grupos = 2
            while n_grupos * 2 <= max(2, n // 4):
                n_grupos *= 2
            n_grupos = min(n_grupos, 16, max(2, n // 2))
            ordem = sorted(self.times, key=lambda t: (-t.reputacao, t.nome))
            return _fase_grupos(
                "Primeira fase",
                _distribuir_grupos(ordem, n_grupos),
                ida_e_volta=False,
            )
        return _fase_pontos(
            "Primeira fase", self.times, ida_e_volta=False
        )

    def _planejar_rodadas(self) -> int:
        """Quantas rodadas a temporada terá (as fases futuras já são contadas)."""
        total = sum(f.total_rodadas for f in self.fases)
        if self.divisao in ("A", "B") and len(self.times) >= 8:
            total += 6  # dois grupos de 4, turno e returno
            total += 2  # final em ida e volta
        elif self.divisao == "D":
            classificados = 2 * len(self.fases[0].grupos)
            while classificados >= 2:
                total += 2  # cada fase do mata-mata é ida e volta
                classificados //= 2
        return total

    # ---- estado -----------------------------------------------------
    @property
    def fase_atual(self) -> Fase:
        return self.fases[-1]

    @property
    def fase_idx(self) -> int:
        return len(self.fases) - 1

    @property
    def rodada_atual(self) -> int:
        return sum(f.rodada_atual for f in self.fases)

    @property
    def total_rodadas(self) -> int:
        return self._total_previsto

    @property
    def encerrada(self) -> bool:
        """``True`` quando a última fase terminou e a temporada foi fechada."""
        return self._encerrada

    @property
    def campeonato_encerrado(self) -> bool:
        return self.encerrada

    @property
    def calendario(self) -> list[list[tuple[str, str]]]:
        """Rodadas já definidas, na ordem em que serão jogadas."""
        return [
            [(casa, fora) for _, casa, fora in rodada]
            for fase in self.fases
            for rodada in fase.rodadas
        ]

    @property
    def resultados(self) -> dict[int, list[Partida]]:
        return self._resultados

    def _get_time_por_nome(self, nome: str) -> Time:
        try:
            return self._por_nome[nome]
        except KeyError:
            raise ValueError(f"Time '{nome}' não encontrado!") from None

    # ---- simulação --------------------------------------------------
    def simular_rodada(self, time_jogador: str = "") -> list[Partida]:
        """Joga a próxima rodada da fase atual e devolve as partidas."""
        if self.encerrada:
            return []
        fase = self.fase_atual
        if fase.tipo != "mata" and fase.rodada_atual >= fase.total_rodadas:
            return []

        fase.rodada_atual += 1
        rodada_global = sum(f.rodada_atual for f in self.fases[:-1]) + fase.rodada_atual
        jogos: list[Partida] = []
        for grupo, casa, fora in fase.rodadas[fase.rodada_atual - 1]:
            partida = self.engine.simular(
                self._get_time_por_nome(casa),
                self._get_time_por_nome(fora),
                rodada_global,
                is_player_home=(casa == time_jogador),
                is_player_away=(fora == time_jogador),
            )
            partida.fase = fase.nome
            partida.grupo = grupo if fase.tipo != "mata" else ""
            fase.jogos.append(partida)
            jogos.append(partida)

        self._resultados.setdefault(rodada_global, []).extend(jogos)
        if fase.rodada_atual >= fase.total_rodadas:
            self._concluir_fase(fase)
        return jogos

    def simular_restante(self) -> int:
        """Simula o que falta da temporada. Devolve o número de partidas."""
        total = 0
        while not self.encerrada:
            partidas = self.simular_rodada()
            if not partidas:
                break
            total += len(partidas)
        return total

    def _concluir_fase(self, fase: Fase) -> None:
        fase.concluida = True
        if fase.tipo == "mata":
            self._resolver_mata(fase)
        self._proxima_fase(fase)

    def _proxima_fase(self, fase: Fase) -> None:
        if fase.tipo == "mata":
            if len(fase.vencedores) >= 2:
                proxima = self._fase_mata_de(fase.vencedores)
                if proxima is not None:
                    self.fases.append(proxima)
                    return
            self._fechar_temporada()
            return

        if self.divisao in ("A", "B"):
            if fase.tipo == "pontos":
                if len(self.times) >= 8:
                    self.fases.append(self._segunda_fase())
                    return
                self._fechar_temporada()
                return
            # fase de grupos: líderes de cada grupo vão à final
            lideres = []
            for letra in sorted(fase.grupos):
                tabela = self.tabela(fase, letra)
                if tabela:
                    lideres.append(tabela[0]["time"])
            self._definir_acesso(fase)
            if len(lideres) == 2:
                self.fases.append(
                    _fase_mata("Final", [(lideres[0].nome, lideres[1].nome)])
                )
                return
            self._fechar_temporada()
            return

        if self.divisao == "D":
            if fase.tipo == "grupos":
                classificados = self._classificados_dos_grupos(fase)
                self.fases.append(self._chave_mata(classificados))
                return
            self._fechar_temporada()
            return

        # Série C: fase única
        self._fechar_temporada()

    def _segunda_fase(self) -> Fase:
        tabela = self.tabela(self.fases[0])
        classificados = [linha["time"] for linha in tabela[:8]]
        # chaveamento clássico: 1º,4º,5º,8º no grupo A; 2º,3º,6º,7º no grupo B
        grupos = {
            "A": [classificados[i] for i in (0, 3, 4, 7)],
            "B": [classificados[i] for i in (1, 2, 5, 6)],
        }
        return _fase_grupos("Segunda fase", grupos, ida_e_volta=True)

    def _classificados_dos_grupos(self, fase: Fase) -> list[Time]:
        classificados: list[Time] = []
        for letra in sorted(fase.grupos):
            tabela = self.tabela(fase, letra)
            classificados.extend(linha["time"] for linha in tabela[:2])
        return classificados

    def _chave_mata(self, classificados: list[Time]) -> Fase:
        """
        Monta a chave da Série D cruzando grupos diferentes.

        Os líderes de grupo enfrentam os segundos de outro grupo (metade de
        distância na tabela), como no regulamento real.
        """
        n_grupos = len(classificados) // 2
        lideres = classificados[0::2]
        segundos = classificados[1::2]
        deslocamento = max(1, n_grupos // 2)
        pares = [
            (lideres[i].nome, segundos[(i + deslocamento) % n_grupos].nome)
            for i in range(n_grupos)
        ]
        nome = NOMES_MATA.get(len(classificados), f"Fase de {len(classificados)}")
        return _fase_mata(nome, pares)

    def _fase_mata_de(self, vencedores: list[Time]) -> Fase | None:
        """Próxima fase eliminatória a partir dos classificados."""
        if len(vencedores) < 2:
            return None
        nome = NOMES_MATA.get(len(vencedores), f"Fase de {len(vencedores)}")
        pares = [
            (vencedores[i].nome, vencedores[i + 1].nome)
            for i in range(0, len(vencedores) - 1, 2)
        ]
        return _fase_mata(nome, pares)

    def _resolver_mata(self, fase: Fase) -> None:
        """Decide os classificados da fase eliminatória (agregado + pênaltis)."""
        vencedores: list[Time] = []
        for casa, fora in fase.pares:
            a, b = self._por_nome[casa], self._por_nome[fora]
            gols_a = gols_b = 0
            for partida in fase.jogos:
                if partida.time_casa in (a.nome, b.nome) and partida.time_fora in (
                    a.nome,
                    b.nome,
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
        fase.vencedores = vencedores
        # Série D: quem chega à semifinal sobe para a Série C
        if self.divisao == "D" and fase.nome == "Semifinal":
            self._promovidos = [self._por_nome[nome] for par in fase.pares for nome in par]
        if fase.nome == "Final" and vencedores:
            self.campeao = vencedores[0]

    def _penaltis(self, a: Time, b: Time) -> Time:
        p = 0.5 + (a.overall_time - b.overall_time) / 300
        p = max(0.2, min(0.8, p))
        return a if self.rng.random() < p else b

    def _anotar_penaltis(self, fase: Fase, a: Time, b: Time, vencedor: Time) -> None:
        perdedor = b if vencedor is a else a
        placar_v, placar_p = (4, 3) if self.rng.random() < 0.7 else (5, 4)
        if fase.jogos:
            fase.jogos[-1].eventos.append(
                f"🥅 Pênaltis: {vencedor.nome} vence por {placar_v} x {placar_p}"
            )
        _ = perdedor

    def _definir_acesso(self, fase_grupos: Fase) -> None:
        """Série B: os dois primeiros de cada grupo sobem."""
        if self.divisao != "B":
            return
        promovidos: list[Time] = []
        for letra in sorted(fase_grupos.grupos):
            tabela = self.tabela(fase_grupos, letra)
            promovidos.extend(linha["time"] for linha in tabela[:2])
        self._promovidos = promovidos

    def _fechar_temporada(self) -> None:
        tabela = self.tabela(self.fases[0])
        if self.campeao is None and tabela:
            self.campeao = tabela[0]["time"]

        if self.divisao == "D" and not self._promovidos:
            # sem mata-mata (poucos clubes): sobem os 4 melhores da 1ª fase
            self._promovidos = [linha["time"] for linha in tabela[:4]]
        if self.divisao == "C":
            self._promovidos = [linha["time"] for linha in tabela[: self.acesso]]
        if self.divisao == "B" and not self._promovidos:
            # sem 2ª fase (poucos clubes): sobem os 4 melhores da 1ª fase
            self._promovidos = [linha["time"] for linha in tabela[: self.acesso]]

        if self.descenso and len(tabela) > self.descenso:
            self._rebaixados = [linha["time"] for linha in tabela[-self.descenso :]]

        self._encerrada = True
        if self.campeao is not None:
            self.noticias.append(
                Noticia(
                    titulo=f"🏆 {self.campeao.nome} é campeão da Série {self.divisao}!",
                    texto=(
                        f"{self.campeao.nome} levantou o título da Série "
                        f"{self.divisao} de {self.temporada}."
                    ),
                    rodada=self.rodada_atual,
                    tipo="geral",
                )
            )

    # ---- consultas --------------------------------------------------
    def tabela(
        self, fase: Fase | None = None, grupo: str | None = None
    ) -> list[dict]:
        """Classificação de uma fase (ou de um grupo) da temporada."""
        fase = fase or self.fases[0]
        if fase.tipo == "mata":
            return []
        clubes = (
            fase.grupos.get(grupo, []) if grupo else [t for g in fase.grupos.values() for t in g]
        )
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
        for partida in fase.jogos:
            if not partida.jogada:
                continue
            if grupo and partida.grupo != grupo:
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

    @property
    def classificacao(self) -> list[Time]:
        """Classificação da primeira fase (base da posição na temporada)."""
        return [linha["time"] for linha in self.tabela(self.fases[0])]

    def jogos_do_time(self, nome: str) -> list[tuple[int, str, str, Partida | None]]:
        """Calendário do clube na temporada: ``(rodada, casa, fora, partida)``."""
        jogos = []
        rodada = 0
        for fase in self.fases:
            for confrontos in fase.rodadas:
                rodada += 1
                for _, casa, fora in confrontos:
                    if nome in (casa, fora):
                        jogos.append(
                            (rodada, casa, fora, self.partida(rodada, casa, fora))
                        )
        return jogos

    def partida(self, rodada: int, casa: str, fora: str) -> Partida | None:
        for partida in self._resultados.get(rodada, []):
            if partida.time_casa == casa and partida.time_fora == fora:
                return partida
        return None

    def confrontos_da_rodada(
        self, rodada: int
    ) -> list[tuple[str, str, Partida | None]]:
        """Jogos de uma rodada (1-based) da temporada, com o resultado."""
        calendario = self.calendario
        if rodada < 1 or rodada > len(calendario):
            return []
        return [
            (casa, fora, self.partida(rodada, casa, fora))
            for casa, fora in calendario[rodada - 1]
        ]

    def jogo_do_jogador(self, nome: str, rodada: int) -> Partida | None:
        for partida in self._resultados.get(rodada, []):
            if nome in (partida.time_casa, partida.time_fora):
                return partida
        return None

    def proximo_adversario(self, nome: str) -> str:
        if self.encerrada:
            return "Temporada encerrada"
        calendario = self.calendario
        if self.rodada_atual >= len(calendario):
            return "Aguardando a próxima fase"
        for casa, fora in calendario[self.rodada_atual]:
            if casa == nome:
                return f"vs {fora} (Casa)"
            if fora == nome:
                return f"vs {casa} (Fora)"
        return "Folga"

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
        return (
            f"Série {self.divisao}: {self.rodada_atual}/{self.total_rodadas} "
            f"rodadas · {self.fase_atual.nome}"
        )
