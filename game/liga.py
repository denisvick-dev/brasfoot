"""
Alias de compatibilidade.

O app Streamlit importa ``from game.liga import League``; a implementação
mora em ``game.campeonato``. Este arquivo apenas reexporta o módulo, então
os dois nomes (``game.liga`` e ``game.campeonato``) funcionam.
"""

from game.campeonato import *  # noqa: F401,F403
from game.campeonato import League  # noqa: F401  (símbolo usado pelo app)
