"""
Tela inicial: escolha/criação do clube e início da temporada.
"""

import streamlit as st

from game.banco_dados import (
    DIVISOES,
    NOMES_DIVISAO,
    criar_times,
)
from game.campeonato import League
from game.escudos import imagem as escudo_img
from game.mercado import Market
from game.piramide import Piramide
from ui.apoio import formatar_dinheiro, secao


def tela_inicial():
    st.markdown(
        """
    <div class="hero">
        <h1>⚽ BRASFOOT</h1>
        <p>Gerenciador de futebol brasileiro — escolha seu clube, monte a equipe
        e busque o título do Brasileirão.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # banco completo (156 clubes): as quatro divisões jogam ao mesmo tempo
    if st.session_state.times is None:
        st.session_state.times = criar_times(None)

    banco = list(st.session_state.times)

    col_div, col_info = st.columns([1, 3])
    with col_div:
        divisao = (
            st.selectbox(
                "Divisão",
                list(DIVISOES),
                index=0,
                format_func=lambda d: NOMES_DIVISAO.get(d, str(d)),
                key="divisao_inicial",
            )
            or "A"
        )
    clubes_divisao = [t for t in banco if t.divisao == divisao]
    with col_info:
        st.caption(
            f"**{NOMES_DIVISAO.get(divisao, divisao)}** — {len(clubes_divisao)} clubes. "
            "As quatro divisões jogam juntas: você disputa a sua e acompanha "
            "as demais em Calendário e Classificações."
        )

    secao(
        "Escolha seu time para começar a temporada", NOMES_DIVISAO.get(divisao, divisao)
    )

    custom = [
        t
        for t in st.session_state.get("clubes_custom", [])
        if t.nome not in {x.nome for x in banco}
    ]
    times = list(clubes_divisao)
    if custom:
        incluir = st.toggle(f"Incluir meus clubes criados ({len(custom)})", value=True)
        if incluir:
            times += custom

    cols_per_row = 4
    for i in range(0, len(times), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(times):
                continue
            time = times[idx]
            with col:
                st.markdown(
                    f"""
                <div class="club-card">
                    <div class="stripe" style="--c1:{time.cor_primaria}"></div>
                    <div class="body">
                        <div class="club-top">
                            <div class="club-crest"
                                 style="--c1:{time.cor_primaria};--c2:{time.cor_secundaria}">
                                {escudo_img(time.sigla, time.escudo_emoji, "escudo-crest")}
                            </div>
                            <div>
                                <div class="club-name">{time.nome}</div>
                                <div class="club-meta">📍 {time.cidade}/{time.estado}</div>
                            </div>
                        </div>
                        <div class="kv"><span>Força</span><b>⭐ {time.overall_time}</b></div>
                        <div class="kv"><span>Caixa</span><b>{formatar_dinheiro(time.financas)}</b></div>
                        <div class="kv"><span>Elenco</span><b>{len(time.jogadores)} jogadores</b></div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    f"Escolher {time.sigla}",
                    key=f"btn_{time.sigla}_{idx}",
                    use_container_width=True,
                    type="primary",
                ):
                    # a temporada inteira entra no jogo: banco + clubes criados
                    elenco = banco + custom
                    st.session_state.times = elenco
                    st.session_state.meu_time = time.nome
                    try:
                        piramide = Piramide(elenco)
                    except ValueError as erro:
                        st.error(f"❌ {erro}")
                        st.stop()
                    st.session_state.piramide = piramide
                    st.session_state.league = piramide.league_de(time.nome) or League(
                        elenco
                    )
                    st.session_state.market = Market(elenco)
                    st.session_state.game_started = True
                    st.session_state.pagina = "painel"
                    st.rerun()
                st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
