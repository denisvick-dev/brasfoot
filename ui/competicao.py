"""
Detalhes de uma competição personalizada (súmula, tabela e chaves).
"""

import streamlit as st

from game.competicoes import (
    FORMATOS,
)
from game.escudos import imagem as escudo_img
from ui.apoio import _html_tabela, secao
from ui.jogar import _linha_do_tempo


def tela_competicao():
    camp = st.session_state.get("competicao")
    if camp is None:
        st.info(
            "Nenhuma competição em andamento. Crie uma em 🛠️ Criador → Campeonato "
            "ou abra uma salva em 📁 Meus dados."
        )
        return

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">🏆 {camp.nome}</h1>
        <p>{FORMATOS.get(camp.formato, camp.formato)} · {len(camp.times)} times ·
        {len(camp.resultados)} jogos disputados · {camp.progresso}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if camp.encerrado:
        campeao = camp.campeao
        if campeao:
            st.balloons()
            st.markdown(
                f"""
            <div class="hero" style="background:linear-gradient(120deg,#92400E 0%,#F5B301 55%,#FDE68A 100%);
                                     color:#1F1300;padding:1.6rem">
                <h1 style="color:#1F1300;font-size:1.6rem">🏆 {escudo_img(campeao.sigla, campeao.escudo_emoji)} {campeao.nome} CAMPEÃO</h1>
            </div>
            """,
                unsafe_allow_html=True,
            )
        if camp.formato == "pontos_corridos":
            resumo = camp.resumo_final()
            if resumo["promovidos"]:
                st.success(
                    "⬆️ Promovidos: "
                    + ", ".join(t.nome for t in resumo["promovidos"])
                )
            if resumo["rebaixados"]:
                st.error(
                    "⬇️ Rebaixados: "
                    + ", ".join(t.nome for t in resumo["rebaixados"])
                )
        if st.button("💾 Salvar resultado"):
            camp.salvar()
            st.success("✅ Campeonato salvo!")
    else:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(
                f'<div class="stat" style="--accent:#2563EB">'
                f'<div class="lbl">Fase atual</div>'
                f'<div class="val" style="font-size:1.3rem;font-family:var(--font-ui)!important">'
                f'{camp.progresso}</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown("<div style='height:1.55rem'></div>", unsafe_allow_html=True)
            if st.button(camp.botao_avancar, type="primary", use_container_width=True):
                camp.avancar()
                camp.salvar()
                st.rerun()

    fase = camp.fase_atual or (camp.fases[-1] if camp.fases else None)
    if fase is None:
        return

    # ---- grupos / pontos corridos
    if fase.tipo == "grupos":
        grupos = camp.grupos_da_fase(fase)
        colunas = st.columns(min(3, max(1, len(grupos))))
        for i, grupo in enumerate(grupos):
            with colunas[i % len(colunas)]:
                titulo = (
                    f"Grupo {grupo}"
                    if len(grupos) > 1 or grupo != "Geral"
                    else "Classificação"
                )
                st.markdown(
                    f"<div class='sec-title' style='font-size:1rem'>{titulo}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    _html_tabela(camp.tabela(fase, grupo)), unsafe_allow_html=True
                )
                if len(grupos) > 1:
                    st.caption(
                        f"Classificam-se os {fase.classificados} primeiros"
                    )

    # ---- mata-mata
    else:
        secao(fase.nome, "Chaves")
        for confronto in fase.confrontos:
            a, b = confronto.a, confronto.b
            if a is None and b is None:
                continue
            if a is None:
                st.markdown(
                    f'<div class="res">🎟️ <b>{escudo_img(b.sigla, b.escudo_emoji)} {b.nome}</b> '
                    f'<span class="tag e" style="margin-left:auto">Folga (BYE)</span></div>',
                    unsafe_allow_html=True,
                )
                continue
            if b is None:
                st.markdown(
                    f'<div class="res">🎟️ <b>{escudo_img(a.sigla, a.escudo_emoji)} {a.nome}</b> '
                    f'<span class="tag e" style="margin-left:auto">Folga (BYE)</span></div>',
                    unsafe_allow_html=True,
                )
                continue

            gols_a, gols_b = confronto.gols(a), confronto.gols(b)
            vencedor = confronto.vencedor
            cls_a = "v" if vencedor is a else ("d" if vencedor else "")
            cls_b = "v" if vencedor is b else ("d" if vencedor else "")

            jogos_txt = " · ".join(
                f"{p.time_casa} {p.gols_casa}x{p.gols_fora} {p.time_fora}"
                for p in confronto.jogos
            )
            st.markdown(
                f"""
            <div class="res" style="flex-wrap:wrap">
                <span class="tag {cls_a}">{a.sigla}</span>
                <span><b>{escudo_img(a.sigla, a.escudo_emoji)} {a.nome}</b></span>
                <span style="font-size:1.25rem"><b>{gols_a} x {gols_b}</b></span>
                <span><b>{escudo_img(b.sigla, b.escudo_emoji)} {b.nome}</b></span>
                <span class="tag {cls_b}">{b.sigla}</span>
                <span style="margin-left:auto" class="club-meta">{jogos_txt or 'aguardando'}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )
        st.caption("Ida e volta" if fase.ida_e_volta else "Jogo único")

        # disputa de 3º lugar (configurada no criador)
        jogo_3 = camp.jogo_terceiro_lugar
        if jogo_3 is not None:
            st.markdown(
                f'<div class="res" style="flex-wrap:wrap">'
                f"<span>🥉</span>"
                f"<span><b>{jogo_3.time_casa}</b> <b>{jogo_3.gols_casa} x {jogo_3.gols_fora}</b> "
                f"<b>{jogo_3.time_fora}</b></span>"
                f'<span class="club-meta" style="margin-left:auto">Disputa de 3º lugar</span>'
                f"</div>",
                unsafe_allow_html=True,
            )
        elif camp.terceiro is not None and camp.terceiro.a and camp.terceiro.b:
            st.caption(
                f"🥉 Disputa de 3º lugar: {camp.terceiro.a.nome} x "
                f"{camp.terceiro.b.nome} — acontece junto com a final."
            )

    # ---- jogos da fase
    jogos = camp.jogos_da_fase()
    if jogos:
        secao("Jogos", f"{len(jogos)} partidas nesta fase")
        for p in jogos[-12:]:
            with st.expander(f"⚽ {p.resultado_str}"):
                if p.eventos:
                    _linha_do_tempo(p.eventos)
                else:
                    st.caption("Sem eventos registrados.")

    artilheiros = camp.artilharia(5)
    if artilheiros:
        secao("Artilharia", "Top 5")
        for j, sigla in artilheiros:
            st.markdown(
                f'<div class="res">⚽ <b>{j.nome}</b> '
                f'<span class="club-meta">{sigla} · {j.posicao}</span>'
                f'<span style="margin-left:auto"><b>{j.gols} gols</b> · '
                f'{j.assistencias} assist</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    if st.button("💾 Salvar progresso", use_container_width=True):
        camp.salvar()
        st.success("✅ Progresso salvo!")


