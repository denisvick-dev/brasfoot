"""
Painel do clube: resumo da temporada, próximos jogos e notícias.
"""

import streamlit as st

from game.diretoria import cor_da_situacao, objetivo_do_time
from game.escudos import imagem as escudo_img
from ui.apoio import (
    formatar_dinheiro,
    get_meu_time,
    get_piramide,
    posicao_na_tabela,
    secao,
    stat_card,
)


def tela_painel():
    time = get_meu_time()
    if time is None:
        st.error("Não foi possível encontrar o time selecionado.")
        return

    league = st.session_state.league
    pos = posicao_na_tabela(league, time.nome)

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">🏠 {escudo_img(time.sigla, time.escudo_emoji)} {time.nome}</h1>
        <p>Rodada {league.rodada_atual} de {league.total_rodadas} ·
        {pos}º colocado · {formatar_dinheiro(time.financas)} em caixa</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        stat_card("📊 Posição", f"{pos}º", "#2563EB")
    with col2:
        stat_card("🏆 Pontos", time.pontos, "#16A34A")
    with col3:
        stat_card("⚽ Gols", f"{time.gols_pro}/{time.gols_contra}", "#D97706")
    with col4:
        stat_card("💰 Caixa", formatar_dinheiro(time.financas), "#6A1B9A")
    with col5:
        stat_card("🎭 Moral", f"{time.moral_time}%", "#DC2626")

    objetivo = objetivo_do_time(time)
    situacao = objetivo.situacao(pos)
    st.markdown(
        f"""
    <div class="card" style="border-left:4px solid {cor_da_situacao(situacao)}">
        <span class="kicker">🎯 Objetivo da diretoria</span>
        <div style="font-weight:700;margin-top:.2rem">{objetivo.descricao}</div>
        <div class="muted">Situação: <b style="color:{cor_da_situacao(situacao)}">
        {situacao}</b></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    piramide_painel = get_piramide()
    if piramide_painel is not None:
        proximo = piramide_painel.proximo_jogo(time.nome)
        if proximo is not None:
            competicao, rodada_prox, casa_prox, fora_prox = proximo
            adversario_prox = fora_prox if casa_prox == time.nome else casa_prox
            st.caption(
                f"🎯 **{competicao}** — "
                f"{'🏠 em casa' if casa_prox == time.nome else '✈️ fora de casa'} "
                f"contra **{adversario_prox}** (rodada {rodada_prox} de "
                f"{piramide_painel.total_rodadas_global})"
            )

    col_left, col_right = st.columns([3, 2])

    with col_left:
        secao("Últimos Resultados", "Histórico")
        resultados_time = []
        for rod in range(max(1, league.rodada_atual - 4), league.rodada_atual + 1):
            jogo = league.jogo_do_jogador(time.nome, rod)
            if jogo:
                resultados_time.append(jogo)

        if resultados_time:
            for jogo in reversed(resultados_time):
                if time.nome == jogo.time_casa:
                    meus_gols = jogo.gols_casa
                    gols_adv = jogo.gols_fora
                else:
                    meus_gols = jogo.gols_fora
                    gols_adv = jogo.gols_casa

                if meus_gols > gols_adv:
                    tag, cls = "V", "v"
                elif meus_gols < gols_adv:
                    tag, cls = "D", "d"
                else:
                    tag, cls = "E", "e"

                st.markdown(
                    f"""
                <div class="res">
                    <span class="tag {cls}">{tag}</span>
                    <span style="color:var(--ink-3);font-size:.8rem">Rod. {jogo.rodada}</span>
                    <span><b>{jogo.time_casa}</b> {jogo.gols_casa} x {jogo.gols_fora} <b>{jogo.time_fora}</b></span>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nenhum jogo disputado ainda. Vá em ⚽ Jogar Rodada!")

    with col_right:
        secao("Classificação", "Top 8")
        classif = league.classificacao
        linhas = []
        for i, t in enumerate(classif[:8]):
            posicao = i + 1
            if posicao <= 4:
                zona = "#16A34A"
            elif posicao <= 6:
                zona = "#F5B301"
            elif posicao >= len(classif) - 3:
                zona = "#DC2626"
            else:
                zona = "#CBD5E1"
            me = "me" if t.nome == time.nome else ""
            linhas.append(
                f"<tr class='{me}'><td class='num'>{posicao}º</td>"
                f"<td><span class='zona' style='background:{zona}'></span></td>"
                f"<td>{escudo_img(t.sigla, t.escudo_emoji)} {t.sigla}</td>"
                f"<td class='num'><b>{t.pontos}</b></td>"
                f"<td class='num'>{t.vitorias}V {t.empates}E {t.derrotas}D</td></tr>"
            )
        if pos > 8:
            linhas.append(
                f"<tr class='me'><td class='num'>{pos}º</td><td></td>"
                f"<td>{escudo_img(time.sigla, time.escudo_emoji)} {time.sigla}</td>"
                f"<td class='num'><b>{time.pontos}</b></td>"
                f"<td class='num'>{time.vitorias}V {time.empates}E {time.derrotas}D</td></tr>"
            )
        st.markdown(
            "<table class='tbl'><thead><tr><th class='num'>#</th><th></th>"
            "<th>Time</th><th class='num'>Pts</th><th class='num'>Campanha</th>"
            "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table>",
            unsafe_allow_html=True,
        )

    if league.noticias:
        secao("Últimas Notícias", "Midia")
        for noticia in league.noticias[-5:][::-1]:
            st.info(
                f"**{noticia.titulo}** (Rodada {noticia.rodada})\n\n{noticia.texto}"
            )
