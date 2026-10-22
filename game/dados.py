"""
Alias de compatibilidade.

O módulo de dados chama-se ``game.banco_dados`` (é o nome que ``mercado.py``
importa). Este arquivo só faz com que ``game.dados`` aponte para ele, para que
qualquer código escrito com o nome antigo continue funcionando.
"""

import sys

from game import banco_dados

sys.modules[__name__] = banco_dados
