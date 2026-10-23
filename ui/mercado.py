"""
Mercado de transferências: contratações e vendas.
"""

import streamlit as st

from game.modelos import Noticia
from ui.apoio import (
    badge_overall,
    cor_posicao,
    formatar_dinheiro,
    get_meu_time,
    hero,
    secao,
)


def tela_mercado():
    time = get_meu_time()
    if time is None:
        st.warning("Selecione um time antes de acessar o mercado de transferências.")
        return

    market = st.session_state.market

    hero(
        "Mercado de Transferências",
        f"Orçamento disponível: {formatar_dinheiro(time.financas)} · "
        f"elenco: {len(time.jogadores)}/30 jogadores",
        kicker="🏪 Mercado",
        time=time,
        chips=(
            f"💰 {formatar_dinheiro(time.financas)}",
            f"👥 {len(time.jogadores)} jogadores",
        ),
    )

    tab1, tab2, tab3 = st.tabs(["🛒 Comprar", "💸 Vender", "📊 Jogadores Livres"])

    with tab1:
        secao("Jogadores Disponíveis", "Ofertas")
        col_a, col_b, col_c = st.columns([2, 2, 1])
        with col_a:
            filtro_pos = st.selectbox(
                "Posição",
                ["Todas", "GOL", "ZAG", "LAT", "VOL", "MEI", "ATA"],
                key="filtro_compra",
            )
        with col_b:
            filtro_max = st.number_input(
                "Preço máximo (R$)",
                min_value=0,
                value=max(0, time.financas),
                step=500_000,
                key="preco_max",
            )
        with col_c:
            st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
            if st.button("🔄 Atualizar Mercado"):
                market.atualizar_mercado()
                st.rerun()

        ofertas = market.ofertas_disponiveis
        if filtro_pos != "Todas":
            ofertas = [(j, t, p) for j, t, p in ofertas if j.posicao == filtro_pos]
        ofertas = [(j, t, p) for j, t, p in ofertas if p <= filtro_max]
        ofertas = [(j, t, p) for j, t, p in ofertas if t.nome != time.nome]
        ofertas.sort(key=lambda x: x[0].overall, reverse=True)

        if ofertas:
            for j, t_vendedor, preco in ofertas[:20]:
                with st.container(border=True):
                    cols = st.columns([2.2, 0.7, 0.7, 1, 1, 1])
                    cols[0].markdown(
                        f"**{cor_posicao(j.posicao)} {j.nome}** "
                        f"<span style='color:var(--ink-3)'>· {t_vendedor.sigla}</span>",
                        unsafe_allow_html=True,
                    )
                    cols[1].markdown(badge_overall(j.overall), unsafe_allow_html=True)
                    cols[2].markdown(f"🎂 {j.idade}")
                    cols[3].markdown(f"💰 **{formatar_dinheiro(preco)}**")
                    cols[4].markdown(
                        f"<span style='color:var(--ink-3)'>💵 {formatar_dinheiro(j.salario)}/mês</span>",
                        unsafe_allow_html=True,
                    )
                    with cols[5]:
                        if st.button(
                            "Comprar",
                            key=f"buy_{j.id}",
                            type="primary",
                            use_container_width=True,
                        ):
                            sucesso, msg = market.comprar_jogador(
                                j, t_vendedor, time, preco
                            )
                            if sucesso:
                                st.session_state.league.noticias.append(
                                    Noticia(
                                        titulo=f"📋 {time.nome} contrata {j.nome}!",
                                        texto=f"{j.nome} chega do {t_vendedor.nome} "
                                        f"por {formatar_dinheiro(preco)}",
                                        rodada=st.session_state.league.rodada_atual,
                                        tipo="transferencia",
                                    )
                                )
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("Nenhum jogador disponível com os filtros selecionados.")

    with tab2:
        secao("Vender Jogadores", f"{len(time.jogadores)} no elenco")
        for j in sorted(time.jogadores, key=lambda x: x.overall, reverse=True):
            with st.container(border=True):
                cols = st.columns([2.2, 0.7, 0.7, 1, 1, 1])
                cols[0].markdown(
                    f"**{cor_posicao(j.posicao)} {j.nome}**"
                    f"{' ⭐' if j.titular else ''}",
                    unsafe_allow_html=True,
                )
                cols[1].markdown(badge_overall(j.overall), unsafe_allow_html=True)
                cols[2].markdown(f"🎂 {j.idade}")
                cols[3].markdown(f"💎 {formatar_dinheiro(j.valor_mercado)}")
                cols[4].markdown(
                    f"<span style='color:var(--ink-3)'>💵 {formatar_dinheiro(j.salario)}/mês</span>",
                    unsafe_allow_html=True,
                )
                with cols[5]:
                    if st.button(
                        "Vender", key=f"sell_{j.id}", use_container_width=True
                    ):
                        sucesso, msg = market.vender_jogador(j, time)
                        if sucesso:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    with tab3:
        secao("Jogadores Livres", "Sem contrato")
        st.caption("Custo de contratação: 6 meses de salário adiantados.")
        if st.button("🔍 Buscar Jogadores Livres", type="primary"):
            livres = [market.gerar_jogador_livre() for _ in range(8)]
            st.session_state["jogadores_livres"] = livres

        if st.session_state.get("jogadores_livres"):
            for j in st.session_state["jogadores_livres"]:
                with st.container(border=True):
                    cols = st.columns([2.2, 0.7, 0.7, 1, 1, 1])
                    cols[0].markdown(
                        f"**{cor_posicao(j.posicao)} {j.nome}**", unsafe_allow_html=True
                    )
                    cols[1].markdown(badge_overall(j.overall), unsafe_allow_html=True)
                    cols[2].markdown(f"🎂 {j.idade}")
                    cols[3].markdown(f"💵 {formatar_dinheiro(j.salario)}/mês")
                    cols[4].markdown(f"💎 {formatar_dinheiro(j.valor_mercado)}")
                    with cols[5]:
                        custo = j.salario * 6
                        if st.button(
                            f"Contratar {formatar_dinheiro(custo)}",
                            key=f"free_{j.id}",
                            type="primary",
                            use_container_width=True,
                        ):
                            if len(time.jogadores) >= 30:
                                st.error("❌ Elenco lotado!")
                            elif time.financas < custo:
                                st.error("❌ Dinheiro insuficiente!")
                            else:
                                time.financas -= custo
                                time.jogadores.append(j)
                                time.auto_escalar()
                                st.session_state["jogadores_livres"].remove(j)
                                st.success(f"✅ {j.nome} contratado!")
                                st.rerun()
