"""
Tela do elenco: jogadores, salários, lesões e suspensões.
"""

import streamlit as st

from game.modelos import Jogador
from ui.apoio import (
    badge_overall,
    barra_energia,
    cor_posicao,
    formatar_dinheiro,
    get_meu_time,
    hero,
    secao,
)


def tela_elenco():
    time = get_meu_time()
    if time is None:
        st.error("Não foi possível encontrar o time selecionado.")
        return

    hero(
        time.nome,
        f"{len(time.jogadores)} jogadores · overall {time.overall_time} · "
        f"valor de elenco {formatar_dinheiro(time.valor_elenco)}",
        kicker="👥 Elenco",
        time=time,
        chips=(
            f"⭐ overall {time.overall_time}",
            f"💼 folha {formatar_dinheiro(sum(j.salario for j in time.jogadores))}",
            f"📋 {time.formacao}",
        ),
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Jogadores", len(time.jogadores))
    with col2:
        st.metric("⭐ Overall Médio", time.overall_time)
    with col3:
        st.metric("💰 Folha Salarial", formatar_dinheiro(time.folha_salarial))
    with col4:
        st.metric("💎 Valor do Elenco", formatar_dinheiro(time.valor_elenco))

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_pos = st.selectbox(
            "Filtrar por posição",
            ["Todos", "GOL", "ZAG", "LAT", "VOL", "MEI", "ATA"],
        )
    with col_f2:
        ordenar = st.selectbox(
            "Ordenar por", ["Overall", "Nome", "Idade", "Gols", "Posição"]
        )

    jogadores = time.jogadores[:]
    if filtro_pos != "Todos":
        jogadores = [j for j in jogadores if j.posicao == filtro_pos]

    sort_map = {
        "Overall": lambda j: j.overall,
        "Nome": lambda j: j.nome,
        "Idade": lambda j: j.idade,
        "Gols": lambda j: j.gols,
        "Posição": lambda j: j.posicao,
    }
    jogadores.sort(
        key=sort_map.get(ordenar, lambda j: j.overall), reverse=(ordenar != "Nome")
    )

    secao("Titulares", f"{len([j for j in jogadores if j.titular])} em campo")
    _mostrar_jogadores_tabela([j for j in jogadores if j.titular])

    secao("Reservas", f"{len([j for j in jogadores if not j.titular])} no banco")
    _mostrar_jogadores_tabela([j for j in jogadores if not j.titular])


def _mostrar_jogadores_tabela(jogadores: list[Jogador]):
    if not jogadores:
        st.caption("Nenhum jogador.")
        return

    linhas = []
    for j in jogadores:
        if j.lesionado:
            status = '<span class="pill p-bad">🏥 Lesionado</span>'
        elif j.suspenso:
            status = '<span class="pill p-warn">🚫 Suspenso</span>'
        else:
            status = '<span class="pill p-ok">✅ Disponível</span>'

        linhas.append(
            "<tr>"
            f"<td>{cor_posicao(j.posicao)} {j.posicao}</td>"
            f"<td><b>{j.nome}</b></td>"
            f"<td class='num'>{badge_overall(j.overall)}</td>"
            f"<td class='num'>{j.idade}</td>"
            f"<td class='num'>⚽ {j.gols}</td>"
            f"<td class='num'>🅰️ {j.assistencias}</td>"
            f"<td class='num'>📋 {j.jogos}</td>"
            f"<td style='width:120px'>{barra_energia(j.energia)}</td>"
            f"<td>{status}</td>"
            f"<td class='num'>{formatar_dinheiro(j.salario)}</td>"
            "</tr>"
        )

    st.markdown(
        "<table class='tbl'><thead><tr>"
        "<th>Pos</th><th>Nome</th><th class='num'>OVR</th><th class='num'>Idade</th>"
        "<th class='num'>Gols</th><th class='num'>Assist</th><th class='num'>Jogos</th>"
        "<th>Energia</th><th>Status</th><th class='num'>Salário</th>"
        "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table>",
        unsafe_allow_html=True,
    )
