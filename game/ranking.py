"""Ranking de pontos acumulados: a tabela histórica dos clubes.

Cada fim de temporada guarda a campanha de todos os clubes (pontos, jogos,
vitórias, gols) e soma na linha do clube. O ranking é, portanto, o acumulado
das temporadas jogadas — quem soma mais pontos aparece primeiro, com os
critérios de desempate do Brasileirão (vitórias, saldo e gols pró).

O módulo não conhece Streamlit: quem chama (a tela de jogo) passa os dados.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field

from game.modelos import Time


@dataclass
class LinhaRanking:
    """Campanha acumulada de um clube no ranking."""

    clube: str
    sigla: str = ""
    divisao: str = "A"
    temporadas: int = 0
    jogos: int = 0
    vitorias: int = 0
    empates: int = 0
    derrotas: int = 0
    gols_pro: int = 0
    gols_contra: int = 0
    pontos: int = 0
    titulos: int = 0  # títulos brasileiros (Série A)
    copas: int = 0  # Copas do Brasil
    regionais: int = 0  # torneios regionais
    acessos: int = 0
    rebaixamentos: int = 0
    melhor_posicao: int = 0  # melhor colocação na Série A (0 = nunca jogou)

    @property
    def saldo_gols(self) -> int:
        return self.gols_pro - self.gols_contra

    @property
    def aproveitamento(self) -> float:
        """Pontos conquistados sobre os pontos disputados (0 a 100)."""
        if self.jogos <= 0:
            return 0.0
        return round(100.0 * self.pontos / (3 * self.jogos), 1)

    @property
    def media_pontos(self) -> float:
        """Pontos por temporada disputada."""
        if self.temporadas <= 0:
            return 0.0
        return round(self.pontos / self.temporadas, 1)

    @property
    def chave(self) -> tuple[int, int, int, int]:
        """Critérios de ordenação (pontos, vitórias, saldo, gols pró)."""
        return (self.pontos, self.vitorias, self.saldo_gols, self.gols_pro)


@dataclass
class TemporadaRegistrada:
    """Resumo de uma temporada fechada (para o histórico do ranking)."""

    temporada: int
    clubes: int = 0
    campeao: str = ""
    campeao_copa: str = ""
    lider: str = ""  # quem mais somou pontos naquela temporada

    def descricao(self) -> str:
        partes = [f"{self.temporada}: {self.clubes} clubes"]
        if self.campeao:
            partes.append(f"🇧🇷 {self.campeao}")
        if self.campeao_copa:
            partes.append(f"🏆 {self.campeao_copa}")
        return " · ".join(partes)


@dataclass
class Ranking:
    """Acumulado de pontos dos clubes em todas as temporadas jogadas."""

    linhas: dict[str, LinhaRanking] = field(default_factory=dict)
    temporadas: list[TemporadaRegistrada] = field(default_factory=list)

    # ---- registro ---------------------------------------------------
    def registrar_temporada(
        self,
        temporada: int,
        clubes: Iterable[Time],
        *,
        campeao: Time | None = None,
        campeao_copa: Time | None = None,
        campeoes_regionais: Iterable[Time] = (),
        acessos: Iterable[str] = (),
        rebaixados: Iterable[str] = (),
    ) -> bool:
        """Soma a campanha dos clubes no acumulado.

        Devolve ``False`` se a temporada já foi registrada (o botão de nova
        temporada pode ser clicado duas vezes; o ranking não pode dobrar).
        """
        if any(t.temporada == temporada for t in self.temporadas):
            return False

        promovidos = set(acessos)
        caidos = set(rebaixados)
        lider: LinhaRanking | None = None
        registrados = 0

        for time in clubes:
            if time.jogos_campeonato <= 0:
                continue
            linha = self._linha_de(time)
            linha.divisao = time.divisao
            linha.sigla = time.sigla
            linha.temporadas += 1
            linha.jogos += time.jogos_campeonato
            linha.vitorias += time.vitorias
            linha.empates += time.empates
            linha.derrotas += time.derrotas
            linha.gols_pro += time.gols_pro
            linha.gols_contra += time.gols_contra
            linha.pontos += time.pontos
            if time.nome in promovidos:
                linha.acessos += 1
            if time.nome in caidos:
                linha.rebaixamentos += 1
            registrados += 1
            if lider is None or linha.pontos > lider.pontos:
                lider = linha

        if registrados == 0:
            return False

        if campeao is not None:
            self._linha_de(campeao).titulos += 1
        if campeao_copa is not None:
            self._linha_de(campeao_copa).copas += 1
        for clube in campeoes_regionais:
            self._linha_de(clube).regionais += 1

        self.temporadas.append(
            TemporadaRegistrada(
                temporada=temporada,
                clubes=registrados,
                campeao=campeao.nome if campeao is not None else "",
                campeao_copa=campeao_copa.nome if campeao_copa is not None else "",
                lider=lider.clube if lider is not None else "",
            )
        )
        return True

    def registrar_posicoes(self, temporada: int, posicoes: dict[str, int]) -> None:
        """Guarda a melhor colocação na Série A (chamado ao fechar a temporada).

        ``posicoes`` mapeia nome do clube para a posição final na elite.
        """
        registro = next((t for t in self.temporadas if t.temporada == temporada), None)
        if registro is None:
            return
        for clube, posicao in posicoes.items():
            if posicao <= 0:
                continue
            linha = self._linha_de_nome(clube)
            if linha.melhor_posicao == 0 or posicao < linha.melhor_posicao:
                linha.melhor_posicao = posicao

    def _linha_de(self, time: Time) -> LinhaRanking:
        linha = self._linha_de_nome(time.nome)
        linha.sigla = time.sigla or linha.sigla
        return linha

    def _linha_de_nome(self, nome: str) -> LinhaRanking:
        linha = self.linhas.get(nome)
        if linha is None:
            linha = LinhaRanking(clube=nome)
            self.linhas[nome] = linha
        return linha

    # ---- consulta ---------------------------------------------------
    @property
    def vazio(self) -> bool:
        return not self.linhas

    @property
    def total_temporadas(self) -> int:
        return len(self.temporadas)

    def ultima_temporada(self) -> TemporadaRegistrada | None:
        return self.temporadas[-1] if self.temporadas else None

    def ordenar(self) -> list[LinhaRanking]:
        """Todas as linhas, da maior pontuação para a menor."""
        return sorted(
            self.linhas.values(),
            key=lambda linha: (*linha.chave, linha.clube),
            reverse=True,
        )

    def top(self, quantidade: int = 20) -> list[LinhaRanking]:
        return self.ordenar()[:quantidade]

    def posicao(self, clube: str) -> int | None:
        """Posição do clube no ranking (1 = líder) ou ``None`` se não está."""
        for indice, linha in enumerate(self.ordenar(), start=1):
            if linha.clube == clube:
                return indice
        return None

    def linha(self, clube: str) -> LinhaRanking | None:
        return self.linhas.get(clube)

    def resumo(self) -> str:
        if self.vazio:
            return "Ranking vazio: feche uma temporada para começar a acumular."
        linha = self.ordenar()[0]
        return (
            f"Ranking com {len(self.linhas)} clubes e {len(self.temporadas)} "
            f"temporada(s) · líder {linha.clube} ({linha.pontos} pts)"
        )


def ranking_da_temporada(clubes: Iterable[Time]) -> list[Time]:
    """Clubes de hoje ordenados pelos pontos da temporada em andamento."""
    return sorted(
        (time for time in clubes if time.jogos_campeonato > 0),
        key=lambda time: (
            time.pontos,
            time.vitorias,
            time.saldo_gols,
            time.gols_pro,
        ),
        reverse=True,
    )
