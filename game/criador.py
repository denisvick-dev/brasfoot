"""
Criadores de clubes e jogadores personalizados.

Uso rápido
----------
>>> from game.criador import criar_clube, criar_jogador, salvar_clube
>>> aurora = criar_clube("Aurora FC", "AUR", cidade="Curitiba", estado="PR")
>>> salvar_clube(aurora)          # -> 'aurora-fc' (salvo em dados/clubes.json)
>>> from game.criador import criar_jogador
>>> craque = criar_jogador("Zico", "MEI", 25, 90, 78, 88, 92, 55, 70)
"""

from __future__ import annotations

import random

from game import persistencia
from game.banco_dados import (
    TIMES_DATA,
    _gerar_elenco,
    _gerar_jogadores_posicao,
    _next_id,
    _nome_aleatorio,
    criar_times_por_nome,
    nomes_conhecidos,
)
from game.modelos import Jogador, Time

POSICOES = ("GOL", "ZAG", "LAT", "VOL", "MEI", "ATA")
DIVISOES = ("A", "B", "C", "D")

ATRIBUTOS = (
    "habilidade",
    "velocidade",
    "finalizacao",
    "passe",
    "defesa",
    "fisico",
)

# perfis para geração rápida: (idade, base dos atributos)
PERFIS: dict[str, dict[str, tuple[int, int]]] = {
    "Promessa (17-21)": {"idade": (17, 21), "base": (45, 66)},
    "Mediano (22-28)": {"idade": (22, 28), "base": (52, 72)},
    "Craque (24-31)": {"idade": (24, 31), "base": (74, 93)},
    "Veterano (33-38)": {"idade": (33, 38), "base": (48, 68)},
}

ESCUDOS = ["⚽", "🔴", "🔵", "🟢", "🟡", "🟣", "🟠", "⚫", "⚪", "🦅", "🦁", "🐯", "🐺", "⭐"]


# ============================================================
# Jogadores
# ============================================================
def criar_jogador(
    nome: str | None,
    posicao: str,
    idade: int = 24,
    habilidade: int = 60,
    velocidade: int = 60,
    finalizacao: int = 60,
    passe: int = 60,
    defesa: int = 60,
    fisico: int = 60,
) -> Jogador:
    """Cria um jogador com os atributos informados (já com salário e valor)."""
    if posicao not in POSICOES:
        raise ValueError(f"Posição inválida: {posicao!r}. Use uma de {POSICOES}.")

    valores = {
        "habilidade": habilidade,
        "velocidade": velocidade,
        "finalizacao": finalizacao,
        "passe": passe,
        "defesa": defesa,
        "fisico": fisico,
    }
    for attr, valor in valores.items():
        if not 1 <= int(valor) <= 99:
            raise ValueError(f"{attr} deve estar entre 1 e 99 (veio {valor}).")

    return Jogador(
        id=_next_id(),
        nome=(nome or _nome_aleatorio()).strip(),
        posicao=posicao,
        idade=max(16, min(45, int(idade))),
        habilidade=max(1, min(99, int(habilidade))),
        velocidade=max(1, min(99, int(velocidade))),
        finalizacao=max(1, min(99, int(finalizacao))),
        passe=max(1, min(99, int(passe))),
        defesa=max(1, min(99, int(defesa))),
        fisico=max(1, min(99, int(fisico))),
    )


def gerar_jogador_aleatorio(
    posicao: str | None = None, perfil: str = "Mediano (22-28)"
) -> Jogador:
    """Sorteia um jogador dentro de um perfil (promessa, mediano, craque...)."""
    cfg = PERFIS.get(perfil, PERFIS["Mediano (22-28)"])
    posicao = posicao or random.choice(POSICOES)
    base = random.randint(*cfg["base"])
    v = 12
    return criar_jogador(
        _nome_aleatorio(),
        posicao,
        idade=random.randint(*cfg["idade"]),
        habilidade=base + random.randint(-v, v),
        velocidade=base + random.randint(-v, v),
        finalizacao=base + random.randint(-v, v),
        passe=base + random.randint(-v, v),
        defesa=base + random.randint(-v, v),
        fisico=base + random.randint(-v, v),
    )


def salvar_jogador(jogador: Jogador) -> str:
    """Salva o jogador em dados/jogadores.json e devolve o slug."""
    return persistencia.salvar(
        "jogador", jogador.nome, persistencia.jogador_para_dict(jogador)
    )


def jogadores_salvos() -> list[dict]:
    """Registros de jogadores salvos (dict com nome, slug e dados)."""
    return persistencia.listar("jogador")


def jogador_salvo(slug: str) -> Jogador | None:
    registro = persistencia.carregar("jogador", slug)
    if not registro or not isinstance(registro.get("dados"), dict):
        return None
    return persistencia.jogador_de_dict(registro["dados"])


# ============================================================
# Clubes
# ============================================================
def _ajustar_elenco(elenco: list[Jogador], tamanho: int) -> list[Jogador]:
    """Corta ou completa o elenco mantendo ao menos 2 goleiros."""
    tamanho = max(11, min(30, tamanho))
    if len(elenco) == tamanho:
        return elenco

    if len(elenco) > tamanho:
        gols = sorted(
            [j for j in elenco if j.posicao == "GOL"], key=lambda j: j.overall, reverse=True
        )[:2]
        restantes = sorted(
            [j for j in elenco if all(j is not g for g in gols)],
            key=lambda j: j.overall,
            reverse=True,
        )
        return gols + restantes[: max(0, tamanho - len(gols))]

    # precisa crescer: sorteia posições e gera reforços
    elenco = list(elenco)
    base = sum(j.overall for j in elenco) / len(elenco)
    f_min, f_max = max(30, int(base) - 12), min(95, int(base) + 8)
    while len(elenco) < tamanho:
        posicao = random.choice(POSICOES)
        elenco += _gerar_jogadores_posicao(posicao, 1, f_min, f_max)
    return elenco


def criar_clube(
    nome: str,
    sigla: str,
    cidade: str = "",
    estado: str = "",
    escudo_emoji: str = "⚽",
    cor_primaria: str = "#16A34A",
    cor_secundaria: str = "#FFFFFF",
    forca_min: int = 45,
    forca_max: int = 70,
    financas: int = 10_000_000,
    torcida: int = 40,
    reputacao: int = 50,
    estadio: str = "",
    capacidade: int = 30_000,
    fundacao: int = 2000,
    divisao: str = "A",
    rival: str | None = None,
    tamanho_elenco: int = 22,
    formacao: str = "4-4-2",
    tatica_ofensiva: int = 50,
) -> Time:
    """Cria um clube novo, com elenco gerado na faixa de força pedida."""
    if not nome or not sigla:
        raise ValueError("Nome e sigla são obrigatórios.")
    if not 1 <= forca_min <= forca_max <= 99:
        raise ValueError("Faixa de força inválida: use 1 <= mínimo <= máximo <= 99.")

    sigla = sigla.strip().upper()[:4]
    elenco = _ajustar_elenco(_gerar_elenco(forca_min, forca_max), tamanho_elenco)

    time = Time(
        id=len(TIMES_DATA) + random.randint(1000, 9999),  # evita colisão com o banco
        nome=nome.strip(),
        sigla=sigla,
        cidade=cidade.strip(),
        estado=estado.strip().upper()[:2],
        escudo_emoji=escudo_emoji or "⚽",
        cor_primaria=cor_primaria,
        cor_secundaria=cor_secundaria,
        jogadores=elenco,
        financas=int(financas),
        torcida=max(1, min(100, int(torcida))),
        reputacao=max(1, min(100, int(reputacao))),
        formacao=formacao,
        tatica_ofensiva=max(0, min(100, int(tatica_ofensiva))),
    )

    time.divisao = divisao
    time.estadio = estadio or f"Estádio {nome}"
    time.capacidade = int(capacidade)
    time.fundacao = int(fundacao)
    time.rival = (rival or "").upper()[:4] or None
    time.origem = "custom"

    time.auto_escalar()
    return time


def salvar_clube(time: Time) -> str:
    """Salva o clube (com elenco e estatísticas) em dados/clubes.json."""
    return persistencia.salvar("clube", time.nome, persistencia.time_para_dict(time))


def clubes_salvos() -> list[dict]:
    """Registros de clubes salvos (dict com nome, slug e dados)."""
    return persistencia.listar("clube")


def clube_salvo(slug: str) -> Time | None:
    registro = persistencia.carregar("clube", slug)
    if not registro or not isinstance(registro.get("dados"), dict):
        return None
    return persistencia.time_de_dict(registro["dados"])


def excluir_clube(slug: str) -> bool:
    return persistencia.excluir("clube", slug)


def excluir_jogador(slug: str) -> bool:
    return persistencia.excluir("jogador", slug)


# ============================================================
# Pool de times para os campeonatos
# ============================================================
def pool_de_times() -> tuple[list[str], list[str]]:
    """
    Nomes disponíveis para montar um campeonato.

    Devolve ``(nomes_do_banco, nomes_customizados)``.
    """
    banco = nomes_conhecidos()
    custom = [r["nome"] for r in clubes_salvos()]
    return banco, custom


def resolver_times(nomes: list[str]) -> list[Time]:
    """
    Converte nomes em objetos Time, buscando no banco e nos clubes salvos.

    Clubes salvos têm prioridade (permitem sobrescrever um clube do banco).
    """
    salvos = {r["nome"]: r["slug"] for r in clubes_salvos()}
    times = []
    nomes_banco = []

    for nome in nomes:
        if nome in salvos:
            time = clube_salvo(salvos[nome])
            if time:
                times.append(time)
            else:
                nomes_banco.append(nome)
        else:
            nomes_banco.append(nome)

    times += criar_times_por_nome(nomes_banco)

    # mantém a ordem pedida pelo usuário
    ordem = {nome: i for i, nome in enumerate(nomes)}
    times.sort(key=lambda t: ordem.get(t.nome, 999))
    return times
