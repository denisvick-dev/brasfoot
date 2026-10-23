"""
Tela de tática: formação, estilo de jogo e escalação.
"""

import streamlit as st

from game.modelos import Jogador, Time
from ui.apoio import (
    badge_overall,
    cor_posicao,
    get_meu_time,
    hero,
    secao,
)


def tela_tatica():
    time = get_meu_time()
    if time is None:
        st.warning("Nenhum time selecionado.")
        return

    hero(
        time.nome,
        f"Formação {time.formacao} · estilo {_nome_estilo(time.tatica_ofensiva)}",
        kicker="📋 Tática",
        time=time,
        chips=(
            f"⚙️ agressividade {time.tatica_ofensiva}",
            f"⭐ {time.overall_time}",
            f"🎭 moral {time.moral_time}%",
        ),
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        secao("Formação", "Esquema")
        formacoes = ["4-4-2", "4-3-3", "3-5-2", "4-5-1", "5-3-2"]
        formacao = st.selectbox(
            "Escolha a formação",
            formacoes,
            index=formacoes.index(time.formacao) if time.formacao in formacoes else 0,
            label_visibility="collapsed",
        )
        if formacao != time.formacao:
            time.formacao = formacao
            time.auto_escalar()
            st.success(f"Formação alterada para {formacao}!")
            st.rerun()

    with col2:
        secao("Estilo de Jogo", "Tática")
        tatica = st.slider(
            "Defensivo ↔ Ofensivo",
            min_value=0,
            max_value=100,
            value=time.tatica_ofensiva,
            format="%d%%",
        )
        time.tatica_ofensiva = tatica
        st.info(_descricao_estilo(tatica))

    secao("Escalação", "Campo")
    _desenhar_campo(time)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("⭐ Overall Médio", time.overall_time)
    with col_b:
        st.metric("⚔️ Força Ataque", time.forca_ataque)
    with col_c:
        st.metric("🛡️ Força Defesa", time.forca_defesa)

    secao("Escalar Manualmente", "Elenco")
    col_e1, col_e2 = st.columns([2, 1])

    with col_e1:
        posicoes_ordem = ["GOL", "ZAG", "LAT", "VOL", "MEI", "ATA"]
        for pos in posicoes_ordem:
            jogadores_pos = sorted(
                [j for j in time.jogadores if j.posicao == pos],
                key=lambda x: x.overall,
                reverse=True,
            )
            if jogadores_pos:
                st.markdown(f"**{cor_posicao(pos)} {pos}**")
                for j in jogadores_pos:
                    status = ""
                    if j.lesionado:
                        status = " 🏥"
                    elif j.suspenso:
                        status = " 🚫"

                    novo = st.checkbox(
                        f"{j.nome} · {badge_overall(j.overall)} · ⚡{j.energia}%{status}",
                        value=j.titular,
                        key=f"esc_{j.id}",
                        disabled=j.lesionado or j.suspenso,
                    )
                    if novo != j.titular:
                        j.titular = novo

    with col_e2:
        titulares = time.titulares
        st.metric("Titulares", f"{len(titulares)}/11")
        if len(titulares) != 11:
            st.warning(
                f"⚠️ Você precisa ter exatamente 11 titulares! (Atual: {len(titulares)})"
            )
        if st.button("🔄 Auto-Escalar", type="primary", use_container_width=True):
            time.auto_escalar()
            st.success("Time escalado automaticamente!")
            st.rerun()


def _nome_estilo(valor: int) -> str:
    if valor < 30:
        return "Retranca"
    if valor < 50:
        return "Defensivo"
    if valor < 60:
        return "Equilibrado"
    if valor < 80:
        return "Ofensivo"
    return "Ataque Total"


def _descricao_estilo(valor: int) -> str:
    if valor < 30:
        return "🛡️ **Retranca** — prioridade total na defesa, contra-ataque."
    if valor < 50:
        return "🛡️ **Defensivo** — jogo cauteloso, posse curta."
    if valor < 60:
        return "⚖️ **Equilibrado** — defesa e ataque balanceados."
    if valor < 80:
        return "⚔️ **Ofensivo** — pressão no campo de ataque."
    return "🔥 **Ataque Total** — todos no ataque, defesa exposta."


def _chip(j: Jogador) -> str:
    return (
        f"<span class='chip'>{cor_posicao(j.posicao)} {j.nome} "
        f"<span class='ovr'>{j.overall}</span> "
        f"<span class='en'>⚡{j.energia}%</span></span>"
    )


def _desenhar_campo(time: Time):
    """Desenha o campo com os jogadores."""
    titulares = time.titulares
    grupos = [
        [j for j in titulares if j.posicao == "ATA"],
        [j for j in titulares if j.posicao == "MEI"],
        [j for j in titulares if j.posicao == "VOL"],
        [j for j in titulares if j.posicao == "LAT"],
        [j for j in titulares if j.posicao == "ZAG"],
        [j for j in titulares if j.posicao == "GOL"],
    ]

    html = ['<div class="pitch">']
    for grupo in grupos:
        if not grupo:
            continue
        chips = "".join(_chip(j) for j in grupo)
        html.append(f'<div class="pitch-row">{chips}</div>')
    if not titulares:
        html.append(
            '<div class="pitch-row"><span class="chip">Nenhum titular escalado</span></div>'
        )
    html.append("</div>")

    st.markdown("".join(html), unsafe_allow_html=True)
