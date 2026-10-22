"""
⚽ BRASFOOT — jogo de gerenciamento de futebol brasileiro.

Ponto de entrada do app Streamlit: configura a página, prepara a sessão e
roteia para a tela escolhida no menu. As telas ficam em ``ui/`` e a simulação
do jogo em ``game/``.
"""

import streamlit as st

from ui.apoio import init_game
from ui.competicao import tela_competicao
from ui.competicoes import tela_calendario, tela_classificacao, tela_resultados
from ui.criador import tela_criador
from ui.elenco import tela_elenco
from ui.estilos import carregar_estilos, configurar_pagina
from ui.inicial import tela_inicial
from ui.jogar import tela_jogar
from ui.mercado import tela_mercado
from ui.noticias import tela_noticias
from ui.painel import tela_painel
from ui.sidebar import sidebar
from ui.tatica import tela_tatica

TELAS = {
    "elenco": tela_elenco,
    "tatica": tela_tatica,
    "jogar": tela_jogar,
    "classificacao": tela_classificacao,
    "calendario": tela_calendario,
    "mercado": tela_mercado,
    "resultados": tela_resultados,
    "noticias": tela_noticias,
    "criador": tela_criador,
    "competicao": tela_competicao,
}


def main() -> None:
    """Desenha a tela atual (ou a tela inicial, antes de o jogo começar)."""
    configurar_pagina()
    init_game()
    carregar_estilos()

    if not st.session_state.game_started:
        tela_inicial()
        return

    sidebar()
    TELAS.get(st.session_state.pagina, tela_painel)()


if __name__ == "__main__":
    main()
