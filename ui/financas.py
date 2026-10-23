"""
Tela de finanças: caixa, folha, receitas, despesas e extrato do clube.
"""

import streamlit as st

from game import financas as financas_jogo
from game.diretoria import cor_da_situacao, objetivo_do_time
from ui.apoio import (
    formatar_dinheiro,
    get_meu_time,
    posicao_na_tabela,
    secao,
    stat_card,
)


def _linha_extrato(lancamento: dict) -> str:
    valor = lancamento["valor"]
    cor = "#16A34A" if valor >= 0 else "#DC2626"
    sinal = "+" if valor >= 0 else "−"
    tipo = financas_jogo.TIPOS.get(lancamento["tipo"], lancamento["tipo"])
    return (
        "<tr>"
        f"<td class='num'>{lancamento['rodada']}</td>"
        f"<td>{tipo}</td>"
        f"<td>{lancamento['descricao']}</td>"
        f"<td class='num' style='color:{cor};font-weight:700'>"
        f"{sinal} {formatar_dinheiro(abs(valor))}</td>"
        "</tr>"
    )


def tela_financas():
    """Finanças do clube: visão geral, resumo por tipo e extrato."""
    time = get_meu_time()
    if time is None:
        st.info("Escolha um clube para ver as finanças.")
        return

    league = st.session_state.league
    receitas = financas_jogo.receitas(time)
    despesas = financas_jogo.despesas(time)
    saldo = receitas - despesas

    secao("Finanças", f"Temporada {league.temporada}")
    st.markdown(
        f"<p class='muted'>Caixa, folha salarial e o extrato de tudo que entrou "
        f"e saiu do {time.nome} nesta temporada.</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stat_card("💰 Caixa", formatar_dinheiro(time.financas), "#16A34A")
    with col2:
        stat_card(
            "💼 Folha salarial", formatar_dinheiro(time.folha_salarial), "#C2410C"
        )
    with col3:
        stat_card("📈 Receitas", formatar_dinheiro(receitas), "#0E7490")
    with col4:
        cor_saldo = "#16A34A" if saldo >= 0 else "#DC2626"
        stat_card("📊 Saldo do ano", formatar_dinheiro(saldo), cor_saldo)

    if time.financas < 0:
        st.warning(
            "Caixa negativo: a diretoria espera corte de gastos. "
            "Venda um jogador ou reduza a folha salarial."
        )

    # ---- objetivo da diretoria -------------------------------------
    objetivo = objetivo_do_time(time)
    posicao = posicao_na_tabela(league, time.nome)
    situacao = objetivo.situacao(posicao)
    st.markdown(
        f"""
    <div class="card" style="border-left:4px solid {cor_da_situacao(situacao)}">
        <div class="kicker">Objetivo da diretoria</div>
        <div style="font-weight:700;margin:.2rem 0">{objetivo.descricao}</div>
        <div class="muted">Situação: <b style="color:{cor_da_situacao(situacao)}">
        {situacao}</b>{f" · {posicao}º lugar na Série {objetivo.divisao}" if posicao else ""}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ---- resumo por tipo -------------------------------------------
    secao("De onde vem o dinheiro", "Resumo da temporada")
    resumo = financas_jogo.resumo(time)
    if not resumo:
        st.info("Ainda não houve nenhum lançamento nesta temporada.")
    else:
        linhas = []
        for tipo, valor in resumo.items():
            rotulo = financas_jogo.TIPOS.get(tipo, tipo)
            cor = "#16A34A" if valor >= 0 else "#DC2626"
            linhas.append(
                "<tr>"
                f"<td>{rotulo}</td>"
                f"<td class='num' style='color:{cor};font-weight:700'>"
                f"{'+' if valor >= 0 else '−'} {formatar_dinheiro(abs(valor))}</td>"
                "</tr>"
            )
        st.markdown(
            "<table class='tbl'><thead><tr><th>Origem</th><th>Total</th>"
            "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table>",
            unsafe_allow_html=True,
        )

    # ---- extrato ----------------------------------------------------
    secao("Extrato", "Últimos lançamentos")
    ultimos = financas_jogo.ultimos(time, 25)
    if not ultimos:
        st.info("O extrato começa a ser preenchido assim que as partidas acontecem.")
        return
    html = (
        "<table class='tbl'><thead><tr>"
        "<th>Rod.</th><th>Tipo</th><th>Descrição</th><th>Valor</th>"
        "</tr></thead><tbody>"
        + "".join(_linha_extrato(item) for item in ultimos)
        + "</tbody></table>"
    )
    st.markdown(html, unsafe_allow_html=True)
    st.caption(
        "Bilheteria e cota de TV entram a cada jogo em casa; a folha salarial "
        "é paga a cada 6 rodadas; a premiação cai no fim da temporada."
    )
