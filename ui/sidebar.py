"""
Menu lateral de navegação e ações rápidas.
"""

import streamlit as st

from game.escudos import imagem as escudo_img
from ui.apoio import (
    divisao_do_jogador,
    formatar_dinheiro,
    get_meu_time,
    posicao_na_tabela,
)


def sidebar():
    time = get_meu_time()
    if time is None:
        return

    league = st.session_state.league

    pos_sidebar = posicao_na_tabela(league, time.nome)
    posicao_html = f' <span class="pill p-ok">{pos_sidebar}º lugar</span>' if pos_sidebar else ""

    with st.sidebar:
        st.markdown(
            f"""
        <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.4rem;">
            <div class="club-crest" style="--c1:{time.cor_primaria};--c2:{time.cor_secundaria}">
                {escudo_img(time.sigla, time.escudo_emoji, "escudo-crest")}
            </div>
            <div>
                <div style="font-family:var(--font-display);font-weight:800;font-size:1.15rem;line-height:1.1">
                    {time.nome}
                </div>
                <div class="club-meta">Temporada {league.temporada} · {time.cidade}/{time.estado}</div>
                <div style="margin-top:.3rem">
                    <span class="pill p-info">Série {divisao_do_jogador()}</span>{posicao_html}
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.progress(
            min(1.0, league.rodada_atual / max(1, league.total_rodadas)),
            text=f"Rodada {league.rodada_atual}/{league.total_rodadas}",
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Caixa", formatar_dinheiro(time.financas))
        with col2:
            st.metric("⭐ Overall", time.overall_time)

        col3, col4 = st.columns(2)
        with col3:
            st.metric(
                "📊 Posição", f"{posicao_na_tabela(league, time.nome)}º"
            )
        with col4:
            st.metric("🎭 Moral", f"{time.moral_time}%")

        prox = league.proximo_adversario(time.nome)
        st.markdown(
            f"""
        <div style="border:1px dashed var(--line);border-radius:12px;padding:.6rem .8rem;
                    background:var(--surface-2)">
            <div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;
                        color:var(--ink-3);font-weight:800">Próximo jogo</div>
            <div style="font-weight:700;margin-top:.15rem">📅 {prox}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        paginas = {
            "painel": "🏠 Painel",
            "elenco": "👥 Elenco",
            "tatica": "📋 Tática",
            "jogar": "⚽ Jogar Rodada",
            "classificacao": "🏆 Classificações",
            "calendario": "📅 Calendário",
            "mercado": "🏪 Mercado",
            "resultados": "📊 Resultados",
            "noticias": "📰 Notícias",
            "criador": "🛠️ Criador",
        }

        if st.session_state.get("competicao") is not None:
            paginas["competicao"] = "🏆 Competição"

        for key, label in paginas.items():
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if st.session_state.pagina == key else "secondary",
            ):
                st.session_state.pagina = key
                st.rerun()

        st.markdown("---")

        if st.button("🔄 Novo Jogo", use_container_width=True):
            # preserva o que foi criado no Criador (clubes e competição em curso)
            preservar = {
                k: st.session_state[k]
                for k in ("clubes_custom", "competicao")
                if k in st.session_state
            }
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.update(preservar)
            st.rerun()


