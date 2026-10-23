"""Fixtures compartilhadas pelos testes."""

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from game.banco_dados import criar_times  # noqa: E402


@pytest.fixture
def banco():
    """Os 156 clubes do banco (recriados a cada teste: a simulação os altera)."""
    return criar_times(None, semente=1)


@pytest.fixture
def times(banco):
    """Cópia rasa do banco (a simulação mexe nos objetos)."""
    return list(banco)


@pytest.fixture
def times8():
    """Oito clubes para simulações rápidas."""
    return criar_times(8, semente=3)
