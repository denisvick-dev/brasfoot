"""
Objetivo da diretoria: a meta da temporada para cada série.

Como no Brasfoot, o clube começa o ano com uma missão definida pela diretoria.
Cumprir ou não a meta muda o clima no clube no fim da temporada.
"""

from __future__ import annotations

from dataclasses import dataclass

from game.modelos import Time

# posicao_max: até que posição a meta é considerada cumprida.
METAS: dict[str, tuple[str, int]] = {
    "A": ("Terminar entre os 6 primeiros e garantir vaga continental", 6),
    "B": ("Subir para a Série A (terminar entre os 4 primeiros)", 4),
    "C": ("Subir para a Série B (terminar entre os 4 primeiros)", 4),
    "D": ("Terminar entre os 8 primeiros da sua chave", 8),
}


@dataclass
class Objetivo:
    """Meta da diretoria para o clube na temporada."""

    divisao: str
    descricao: str
    posicao_max: int

    def cumprido(self, posicao: int) -> bool:
        """``True`` se a posição atual já cumpre a meta."""
        return 0 < posicao <= self.posicao_max

    def situacao(self, posicao: int) -> str:
        """Texto curto da situação da meta (para o painel)."""
        if posicao <= 0:
            return "Temporada ainda não começou"
        if self.cumprido(posicao):
            return "Meta encaminhada"
        if posicao <= self.posicao_max + 3:
            return "Em risco"
        return "Abaixo do esperado"


def objetivo_do_time(time: Time) -> Objetivo:
    """Objetivo da diretoria para o clube, conforme a divisão."""
    divisao = (getattr(time, "divisao", "") or "A").upper()
    descricao, posicao_max = METAS.get(divisao, METAS["A"])
    return Objetivo(divisao=divisao, descricao=descricao, posicao_max=posicao_max)


def cor_da_situacao(situacao: str) -> str:
    """Cor (hex) usada para pintar a situação da meta na interface."""
    if situacao.startswith("Meta"):
        return "#16A34A"
    if situacao == "Em risco":
        return "#D97706"
    if situacao == "Temporada ainda não começou":
        return "#64748B"
    return "#DC2626"
