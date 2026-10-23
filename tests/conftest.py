"""Fixtures compartilhadas pelos testes.

A suíte é **determinística**: antes de cada teste o `random` global é semeado com
um valor fixo (`BRASFOOT_SEED`, padrão 2026). Assim o CI não falha "do nada"
porque uma simulação caiu num placar diferente, e um teste que quebra no CI pode
ser reproduzido na máquina local com a mesma semente::

    BRASFOOT_SEED=1234 pytest

Para varrer várias sementes (caça a testes frágeis)::

    for s in $(seq 1 50); do BRASFOOT_SEED=$s pytest -q || break; done
"""

import os
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from game.banco_dados import criar_times  # noqa: E402

SEMENTE_PADRAO = 2026


@pytest.fixture(autouse=True)
def semente_fixa():
    """Semeia o `random` global e restaura o estado anterior ao fim do teste.

    Quase todo o jogo sorteia com o `random` do módulo (motor de partida,
    calendário, mercado, rotina). Sem isso cada execução produzia um universo
    diferente e alguns testes estatísticos falhavam de vez em quando.
    """
    estado = random.getstate()
    semente = int(os.environ.get("BRASFOOT_SEED", SEMENTE_PADRAO))
    random.seed(semente)
    try:
        yield semente
    finally:
        random.setstate(estado)


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
