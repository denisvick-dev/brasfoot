"""
Modelos de dados do jogo: Jogador, Time, Partida, etc.
"""

import random
from dataclasses import dataclass, field


@dataclass
class Jogador:
    """Representa um jogador de futebol."""

    id: int
    nome: str
    posicao: str  # GOL, ZAG, LAT, VOL, MEI, ATA
    idade: int
    habilidade: int  # 1 a 100
    velocidade: int
    finalizacao: int
    passe: int
    defesa: int
    fisico: int
    moral: int = 70
    energia: int = 100
    gols: int = 0
    assistencias: int = 0
    cartoes_amarelos: int = 0
    cartoes_vermelhos: int = 0
    jogos: int = 0
    salario: int = 0
    valor_mercado: int = 0
    lesionado: bool = False
    suspenso: bool = False
    jogos_suspenso: int = 0  # jogos que ainda precisa cumprir de suspensão
    titular: bool = False

    def __post_init__(self):
        if self.salario == 0:
            self.salario = self._calcular_salario()
        if self.valor_mercado == 0:
            self.valor_mercado = self._calcular_valor()

    def _calcular_salario(self) -> int:
        base = self.overall * 1000
        return int(base * random.uniform(0.8, 1.3))

    def _calcular_valor(self) -> int:
        base = self.overall * 50000
        fator_idade = max(0.5, 1.5 - (self.idade - 22) * 0.05)
        return int(base * fator_idade * random.uniform(0.8, 1.2))

    @property
    def overall(self) -> int:
        """Calcula o overall baseado na posição."""
        pesos = {
            "GOL": {
                "habilidade": 0.3,
                "velocidade": 0.05,
                "finalizacao": 0.0,
                "passe": 0.1,
                "defesa": 0.4,
                "fisico": 0.15,
            },
            "ZAG": {
                "habilidade": 0.15,
                "velocidade": 0.1,
                "finalizacao": 0.05,
                "passe": 0.1,
                "defesa": 0.4,
                "fisico": 0.2,
            },
            "LAT": {
                "habilidade": 0.15,
                "velocidade": 0.25,
                "finalizacao": 0.05,
                "passe": 0.2,
                "defesa": 0.2,
                "fisico": 0.15,
            },
            "VOL": {
                "habilidade": 0.2,
                "velocidade": 0.1,
                "finalizacao": 0.05,
                "passe": 0.25,
                "defesa": 0.25,
                "fisico": 0.15,
            },
            "MEI": {
                "habilidade": 0.25,
                "velocidade": 0.15,
                "finalizacao": 0.15,
                "passe": 0.3,
                "defesa": 0.05,
                "fisico": 0.1,
            },
            "ATA": {
                "habilidade": 0.2,
                "velocidade": 0.2,
                "finalizacao": 0.35,
                "passe": 0.1,
                "defesa": 0.0,
                "fisico": 0.15,
            },
        }
        p = pesos.get(self.posicao, pesos["MEI"])
        ovr = (
            self.habilidade * p["habilidade"]
            + self.velocidade * p["velocidade"]
            + self.finalizacao * p["finalizacao"]
            + self.passe * p["passe"]
            + self.defesa * p["defesa"]
            + self.fisico * p["fisico"]
        )
        return int(ovr)

    @property
    def posicao_emoji(self) -> str:
        emojis = {
            "GOL": "🧤",
            "ZAG": "🛡️",
            "LAT": "🏃",
            "VOL": "⚙️",
            "MEI": "🎯",
            "ATA": "⚡",
        }
        return emojis.get(self.posicao, "⚽")

    def recuperar_energia(self, valor: int = 30):
        self.energia = min(100, self.energia + valor)

    def desgastar(self, valor: int = 20):
        self.energia = max(0, self.energia - valor)


@dataclass
class Time:
    """Representa um time de futebol."""

    id: int
    nome: str
    sigla: str
    cidade: str
    estado: str
    cor_primaria: str
    cor_secundaria: str
    escudo_emoji: str
    jogadores: list[Jogador] = field(default_factory=list)
    financas: int = 5_000_000
    torcida: int = 50
    reputacao: int = 50
    formacao: str = "4-4-2"
    tatica_ofensiva: int = 50  # 0=retranca, 100=ataque total
    moral_time: int = 70

    # Estatísticas do campeonato
    pontos: int = 0
    vitorias: int = 0
    empates: int = 0
    derrotas: int = 0
    gols_pro: int = 0
    gols_contra: int = 0
    jogos_campeonato: int = 0

    # ---- ficha do clube (preenchida pelo banco de dados / criador) ----
    divisao: str = "A"
    estadio: str = ""
    capacidade: int = 30_000
    fundacao: int = 0
    rival: str | None = None
    origem: str = "banco"

    # ---- finanças ----
    # cada lançamento é um dict {rodada, tipo, descricao, valor};
    # o valor é positivo (receita) ou negativo (despesa).
    extrato: list[dict] = field(default_factory=list)

    @property
    def saldo_gols(self) -> int:
        return self.gols_pro - self.gols_contra

    @property
    def titulares(self) -> list[Jogador]:
        return [j for j in self.jogadores if j.titular]

    @property
    def reservas(self) -> list[Jogador]:
        return [j for j in self.jogadores if not j.titular]

    @property
    def overall_time(self) -> int:
        tits = self.titulares
        if not tits:
            return 0
        return int(sum(j.overall for j in tits) / len(tits))

    @property
    def forca_ataque(self) -> int:
        atacantes = [j for j in self.titulares if j.posicao in ("ATA", "MEI")]
        if not atacantes:
            return 0
        return int(sum(j.overall for j in atacantes) / len(atacantes))

    @property
    def forca_defesa(self) -> int:
        defensores = [
            j for j in self.titulares if j.posicao in ("GOL", "ZAG", "LAT", "VOL")
        ]
        if not defensores:
            return 0
        return int(sum(j.overall for j in defensores) / len(defensores))

    @property
    def folha_salarial(self) -> int:
        return sum(j.salario for j in self.jogadores)

    @property
    def valor_elenco(self) -> int:
        return sum(j.valor_mercado for j in self.jogadores)

    def peso_escalacao(
        self, jogador: Jogador, considerar_energia: bool = True
    ) -> float:
        """
        Nota usada para escolher os titulares.

        Com ``considerar_energia``, um jogador cansado perde espaço para o
        reserva — é o que faz o rodízio de elenco existir ao longo do
        campeonato (energia cheia = 1,0 | energia 50 = 0,8).
        """
        if not considerar_energia:
            return float(jogador.overall)
        return jogador.overall * (0.60 + 0.40 * (jogador.energia / 100))

    def auto_escalar(self, considerar_energia: bool = True):
        """Escala automaticamente os melhores jogadores disponíveis."""
        for j in self.jogadores:
            j.titular = False

        formacao_map = {
            "4-4-2": {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 1, "MEI": 3, "ATA": 2},
            "4-3-3": {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 1, "MEI": 2, "ATA": 3},
            "3-5-2": {"GOL": 1, "ZAG": 3, "LAT": 0, "VOL": 2, "MEI": 3, "ATA": 2},
            "4-5-1": {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 2, "MEI": 3, "ATA": 1},
            "5-3-2": {"GOL": 1, "ZAG": 3, "LAT": 2, "VOL": 1, "MEI": 2, "ATA": 2},
        }
        necessidades = formacao_map.get(self.formacao, formacao_map["4-4-2"])

        for posicao, qtd in necessidades.items():
            disponiveis = sorted(
                [
                    j
                    for j in self.jogadores
                    if j.posicao == posicao
                    and not j.titular
                    and not j.lesionado
                    and not j.suspenso
                ],
                key=lambda x: self.peso_escalacao(x, considerar_energia),
                reverse=True,
            )
            for j in disponiveis[:qtd]:
                j.titular = True

    def resetar_campeonato(self):
        self.pontos = 0
        self.vitorias = 0
        self.empates = 0
        self.derrotas = 0
        self.gols_pro = 0
        self.gols_contra = 0
        self.jogos_campeonato = 0
        for j in self.jogadores:
            j.gols = 0
            j.assistencias = 0
            j.cartoes_amarelos = 0
            j.cartoes_vermelhos = 0
            j.jogos = 0


@dataclass
class Partida:
    """Resultado de uma partida."""

    rodada: int
    time_casa: str
    time_fora: str
    gols_casa: int = 0
    gols_fora: int = 0
    eventos: list[str] = field(default_factory=list)
    jogada: bool = False
    publico: int = 0
    # usados pelas competições personalizadas (fase / grupo ou chave)
    fase: str = ""
    grupo: str = ""

    @property
    def resultado_str(self) -> str:
        return f"{self.time_casa} {self.gols_casa} x {self.gols_fora} {self.time_fora}"


@dataclass
class Noticia:
    """Uma notícia do jogo."""

    titulo: str
    texto: str
    rodada: int
    tipo: str = "geral"  # geral, transferencia, resultado, lesao
