"""
Alias de compatibilidade.

O módulo de dados chama-se ``game.banco_dados`` (é o nome que ``mercado.py``
importa). Este arquivo só reexporta tudo, para que qualquer código escrito
com o nome antigo (``game.dados``) continue funcionando.
"""

from game.banco_dados import *  # noqa: F401,F403
from game.banco_dados import (  # noqa: F401  (helpers "privados" usados fora)
    _criar_jogador,
    _criar_time_de_ficha,
    _gerar_elenco,
    _gerar_jogadores_posicao,
    _next_id,
    _nome_aleatorio,
)
