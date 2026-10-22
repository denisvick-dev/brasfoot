"""
Alias de compatibilidade.

O app Streamlit importa ``from game.liga import League``; a implementação
mora em ``game.campeonato``. Este arquivo faz os dois nomes apontarem para
o mesmo módulo.
"""

import sys

from game import campeonato

sys.modules[__name__] = campeonato
