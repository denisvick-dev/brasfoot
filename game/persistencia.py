"""
Persistência das criações (clubes, jogadores e campeonatos) em JSON.

Tudo fica em ``dados/`` na raiz do projeto, um arquivo por tipo, cada um com
vários slots identificados por um slug derivado do nome:

    dados/clubes.json       -> {"flamengo": {"nome": ..., "dados": {...}}, ...}
    dados/jogadores.json
    dados/campeonatos.json

As funções de (des)serialização também guardam os campos extras que o banco de
dados anexa ao ``Time`` (divisão, estádio, capacidade, fundação, rival).
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import asdict, fields
from datetime import datetime
from pathlib import Path
from typing import Any

from game.modelos import Jogador, Time

DADOS_DIR = Path(__file__).resolve().parent.parent / "dados"

TIPOS = ("clube", "jogador", "campeonato")
ARQUIVOS = {
    "clube": "clubes.json",
    "jogador": "jogadores.json",
    "campeonato": "campeonatos.json",
}

# campos que não existem na dataclass Time, mas que o jogo anexa
CAMPOS_EXTRA_TIME = ("divisao", "estadio", "capacidade", "fundacao", "rival", "origem")


# ============================================================
# utilidades
# ============================================================
def slugify(texto: str) -> str:
    """Converte um nome em slug: 'America-RJ' -> 'america-rj'."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicomb(c))
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto


def unicomb(c: str) -> bool:
    return unicodedata.combining(c)


def _caminho(tipo: str) -> Path:
    if tipo not in TIPOS:
        raise ValueError(f"Tipo inválido: {tipo!r}. Use um de {TIPOS}.")
    DADOS_DIR.mkdir(parents=True, exist_ok=True)
    return DADOS_DIR / ARQUIVOS[tipo]


def _ler(tipo: str) -> dict:
    caminho = _caminho(tipo)
    if not caminho.exists():
        return {}
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _gravar(tipo: str, registros: dict):
    _caminho(tipo).write_text(
        json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ============================================================
# API de slots
# ============================================================
def salvar(tipo: str, nome: str, dados: Any) -> str:
    """Salva (ou substitui) um registro e devolve o slug."""
    registros = _ler(tipo)
    base = slugify(nome) or tipo
    slug = base
    i = 2
    while slug in registros and registros[slug]["nome"] != nome:
        slug = f"{base}-{i}"
        i += 1

    registros[slug] = {
        "nome": nome,
        "slug": slug,
        "atualizado_em": datetime.now().isoformat(timespec="seconds"),
        "dados": dados,
    }
    _gravar(tipo, registros)
    return slug


def listar(tipo: str) -> list[dict]:
    """Lista os registros salvos de um tipo, em ordem alfabética."""
    return sorted(_ler(tipo).values(), key=lambda r: r["nome"].lower())


def carregar(tipo: str, slug: str) -> dict | None:
    """Devolve o registro completo (nome, slug, dados) ou None."""
    return _ler(tipo).get(slug)


def excluir(tipo: str, slug: str) -> bool:
    registros = _ler(tipo)
    if slug not in registros:
        return False
    del registros[slug]
    _gravar(tipo, registros)
    return True


def total(tipo: str) -> int:
    return len(_ler(tipo))


# ============================================================
# (des)serialização
# ============================================================
def jogador_para_dict(j: Jogador) -> dict:
    return asdict(j)


def jogador_de_dict(d: dict) -> Jogador:
    nomes = {f.name for f in fields(Jogador)}
    return Jogador(**{k: v for k, v in d.items() if k in nomes})


def time_para_dict(t: Time) -> dict:
    d = asdict(t)
    for campo in CAMPOS_EXTRA_TIME:
        d[campo] = getattr(t, campo, None)
    return d


def time_de_dict(d: dict) -> Time:
    nomes = {f.name for f in fields(Time)}
    kwargs = {k: v for k, v in d.items() if k in nomes}
    kwargs["jogadores"] = [jogador_de_dict(j) for j in kwargs.get("jogadores", [])]
    time = Time(**kwargs)
    for campo in CAMPOS_EXTRA_TIME:
        if d.get(campo) is not None:
            try:
                setattr(time, campo, d[campo])
            except Exception:
                pass
    return time
