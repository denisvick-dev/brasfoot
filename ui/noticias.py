"""
Central de notícias do jogo.
"""

import streamlit as st


def tela_noticias():
    league = st.session_state.league

    st.markdown(
        """
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">📰 Notícias</h1>
        <p>Tudo o que acontece no Brasileirão</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if not league.noticias:
        st.info("Nenhuma notícia no momento. Jogue algumas rodadas!")
        return

    tipo_emoji = {
        "geral": "📰",
        "transferencia": "📋",
        "resultado": "⚽",
        "lesao": "🏥",
    }

    for noticia in reversed(league.noticias):
        emoji = tipo_emoji.get(noticia.tipo, "📰")
        with st.container(border=True):
            st.markdown(
                f"""
            <div style="display:flex;gap:.7rem;align-items:flex-start">
                <div style="font-size:1.4rem">{emoji}</div>
                <div>
                    <div style="font-family:var(--font-display);font-weight:800;font-size:1.02rem">
                        {noticia.titulo}
                    </div>
                    <div style="color:var(--ink-2);margin-top:.15rem">{noticia.texto}</div>
                    <div class="club-meta" style="margin-top:.3rem">Rodada {noticia.rodada}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
