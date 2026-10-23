"""Ranking de pontos acumulados: histórico dos clubes e a temporada em curso."""

import streamlit as st

from game.banco_dados import NOMES_DIVISAO
from game.escudos import imagem as escudo_img
from game.ranking import Ranking, ranking_da_temporada
from ui.apoio import (
    get_meu_time,
    get_piramide,
    hero,
    secao,
    sigla_de,
)

MEDALHAS = {1: "🥇", 2: "🥈", 3: "🥉"}


def tela_ranking():
    """Duas visões: o acumulado das temporadas e a tabela do ano corrente."""
    time = get_meu_time()
    if time is None:
        st.error("Nenhum time selecionado. Escolha um clube para continuar.")
        return

    ranking = ranking_atual()
    lider = ranking.ordenar()[0] if not ranking.vazio else None

    hero(
        "Ranking de pontos",
        "Pontos acumulados por clube, temporada após temporada",
        kicker="📈 Histórico",
        emoji="",
        chips=(
            f"{len(ranking.linhas)} clubes",
            f"{ranking.total_temporadas} temporada(s) registrada(s)",
            f"Líder: {lider.clube} ({lider.pontos} pts)"
            if lider is not None
            else "Nenhuma temporada fechada ainda",
        ),
    )

    aba_acumulado, aba_temporada, aba_historico = st.tabs(
        ["🏆 Acumulado", "📅 Temporada atual", "🗂️ Temporadas"]
    )

    with aba_acumulado:
        _aba_acumulado(ranking, time.nome)

    with aba_temporada:
        _aba_temporada(time.nome)

    with aba_historico:
        _aba_historico(ranking)


def ranking_atual() -> Ranking:
    """Ranking guardado na sessão (cria na primeira visita)."""
    ranking = st.session_state.get("ranking")
    if not isinstance(ranking, Ranking):
        ranking = Ranking()
        st.session_state.ranking = ranking
    return ranking


def registrar_temporada_atual() -> bool:
    """Soma a temporada que está terminando no ranking histórico.

    Chamado pelo botão de nova temporada; devolve `False` se não havia nada
    para registrar (ou se a temporada já estava no ranking).
    """
    time = get_meu_time()
    if time is None:
        return False

    ranking = ranking_atual()
    piramide = get_piramide()
    league = st.session_state.get("league")
    times = st.session_state.get("times") or []
    if not times:
        return False

    temporada = (
        piramide.temporada if piramide is not None else getattr(league, "temporada", 0)
    )
    campeao = None
    campeao_copa = None
    regionais: list = []
    acessos: list[str] = []
    rebaixados: list[str] = []
    posicoes: dict[str, int] = {}

    if piramide is not None:
        if "A" in piramide.divisoes:
            campeao = piramide.divisoes["A"].campeao
            posicoes = {
                clube.nome: indice
                for indice, clube in enumerate(
                    piramide.divisoes["A"].classificacao, start=1
                )
            }
        if piramide.copa is not None:
            campeao_copa = piramide.copa.campeao
        regionais = [t.campeao for t in piramide.regionais if t.campeao is not None]
        movimentos = piramide.acesso_descenso()
        for movimento in movimentos.values():
            acessos.extend(clube.nome for clube in movimento.get("promovidos", []))
            rebaixados.extend(clube.nome for clube in movimento.get("rebaixados", []))
    elif league is not None and getattr(league, "classificacao", None):
        campeao = league.classificacao[0]
        posicoes = {
            clube.nome: indice
            for indice, clube in enumerate(league.classificacao, start=1)
        }

    registrou = ranking.registrar_temporada(
        temporada,
        times,
        campeao=campeao,
        campeao_copa=campeao_copa,
        campeoes_regionais=regionais,
        acessos=acessos,
        rebaixados=rebaixados,
    )
    if registrou:
        ranking.registrar_posicoes(temporada, posicoes)
        st.session_state.ranking = ranking
    return registrou


# ---- abas -----------------------------------------------------------
def _aba_acumulado(ranking: Ranking, meu_time: str) -> None:
    if ranking.vazio:
        _vazio(
            "Ainda não há temporada fechada",
            "O ranking soma a campanha de todos os clubes quando você clica em "
            "🔄 Nova Temporada. Enquanto isso, veja a aba “Temporada atual”.",
        )
        return

    linhas = ranking.ordenar()
    minha_posicao = ranking.posicao(meu_time)
    minha_linha = ranking.linha(meu_time)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="stat" style="--accent:#F5B301">'
            f'<div class="lbl">🥇 Líder do ranking</div>'
            f'<div class="val" style="font-size:1.1rem;'
            f'font-family:var(--font-ui)!important">'
            f"{escudo_img(sigla_de(linhas[0].clube))} {linhas[0].clube}</div>"
            f'<div class="club-meta">{linhas[0].pontos} pts em '
            f"{linhas[0].temporadas} temporada(s)</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        texto_pos = f"{minha_posicao}º" if minha_posicao else "—"
        st.markdown(
            f'<div class="stat" style="--accent:#2563EB">'
            f'<div class="lbl">📍 Seu clube</div>'
            f'<div class="val" style="font-size:1.1rem;'
            f'font-family:var(--font-ui)!important">'
            f"{escudo_img(sigla_de(meu_time))} {meu_time}</div>"
            f'<div class="club-meta">{texto_pos} com '
            f"{minha_linha.pontos if minha_linha else 0} pts</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        melhor = max(linhas, key=lambda linha: linha.pontos / max(1, linha.temporadas))
        st.markdown(
            f'<div class="stat" style="--accent:#16A34A">'
            f'<div class="lbl">📊 Média de pontos</div>'
            f'<div class="val" style="font-size:1.1rem;'
            f'font-family:var(--font-ui)!important">'
            f"{escudo_img(sigla_de(melhor.clube))} {melhor.clube}</div>"
            f'<div class="club-meta">{melhor.media_pontos:.1f} pts por '
            f"temporada</div></div>",
            unsafe_allow_html=True,
        )

    secao("Acumulado por clube", f"{len(linhas)} clubes")
    st.markdown(_tabela_ranking(linhas, meu_time), unsafe_allow_html=True)
    st.caption(
        "Critérios: pontos → vitórias → saldo de gols → gols pró. "
        "Títulos contam só a Série A; 🏆 são Copas do Brasil e 🌎 os regionais."
    )


def _aba_temporada(meu_time: str) -> None:
    times = st.session_state.get("times") or []
    ordenados = ranking_da_temporada(times)
    if not ordenados:
        _vazio(
            "A temporada ainda não começou",
            "Assim que as rodadas forem simuladas, os clubes aparecem aqui "
            "ordenados pelos pontos do ano.",
        )
        return

    secao("Pontos da temporada", f"{len(ordenados)} clubes com jogos")
    st.markdown(_tabela_temporada(ordenados, meu_time), unsafe_allow_html=True)

    pos = next(
        (i for i, clube in enumerate(ordenados, start=1) if clube.nome == meu_time),
        None,
    )
    if pos is not None:
        st.caption(
            f"📍 {meu_time} é o {pos}º clube com mais pontos na temporada, "
            f"somando todas as divisões."
        )


def _aba_historico(ranking: Ranking) -> None:
    if not ranking.temporadas:
        _vazio(
            "Nenhuma temporada registrada",
            "Cada vez que você fecha uma temporada, ela entra aqui com o "
            "campeão brasileiro, o campeão da Copa e quem mais pontuou.",
        )
        return
    secao("Temporadas fechadas", f"{ranking.total_temporadas} no histórico")
    linhas = "".join(
        f'<div class="res"><b>{registro.temporada}</b>'
        f"<span>{registro.clubes} clubes</span>"
        f'<span style="margin-left:auto">🇧🇷 {registro.campeao or "—"}</span>'
        f'<span class="muted">🏆 {registro.campeao_copa or "—"}</span></div>'
        for registro in reversed(ranking.temporadas)
    )
    st.markdown(linhas, unsafe_allow_html=True)


# ---- tabelas --------------------------------------------------------
def _tabela_ranking(linhas, meu_time: str) -> str:
    corpo = []
    for posicao, linha in enumerate(linhas, start=1):
        me = " class='me'" if linha.clube == meu_time else ""
        medalha = MEDALHAS.get(posicao, f"{posicao}º")
        trofeus = "".join(
            [
                "🏆" * min(linha.titulos, 5),
                "🏅" * min(linha.copas, 5),
                "🌎" * min(linha.regionais, 5),
            ]
        )
        corpo.append(
            f"<tr{me}>"
            f"<td class='num'><b>{medalha}</b></td>"
            f"<td>{escudo_img(linha.sigla or sigla_de(linha.clube))} "
            f"{linha.clube}"
            f"<span class='rank-div'>{NOMES_DIVISAO.get(linha.divisao, linha.divisao)}"
            "</span></td>"
            f"<td class='num'>{linha.temporadas}</td>"
            f"<td class='num'>{linha.jogos}</td>"
            f"<td class='num'>{linha.vitorias}</td>"
            f"<td class='num'>{linha.empates}</td>"
            f"<td class='num'>{linha.derrotas}</td>"
            f"<td class='num'>{linha.gols_pro}</td>"
            f"<td class='num'>{linha.gols_contra}</td>"
            f"<td class='num'>{linha.saldo_gols:+d}</td>"
            f"<td class='num'><b>{linha.pontos}</b></td>"
            f"<td class='num'>{linha.media_pontos:.1f}</td>"
            f"<td>{trofeus or '—'}</td>"
            "</tr>"
        )
    return (
        "<table class='tbl tbl-rank'><thead><tr>"
        "<th class='num'>#</th><th>Clube</th><th class='num'>Temp.</th>"
        "<th class='num'>J</th><th class='num'>V</th><th class='num'>E</th>"
        "<th class='num'>D</th><th class='num'>GP</th><th class='num'>GC</th>"
        "<th class='num'>SG</th><th class='num'>Pts</th><th class='num'>Média</th>"
        "<th>Títulos</th>"
        "</tr></thead><tbody>" + "".join(corpo) + "</tbody></table>"
    )


def _tabela_temporada(times, meu_time: str) -> str:
    corpo = []
    for posicao, clube in enumerate(times, start=1):
        me = " class='me'" if clube.nome == meu_time else ""
        medalha = MEDALHAS.get(posicao, f"{posicao}º")
        corpo.append(
            f"<tr{me}>"
            f"<td class='num'><b>{medalha}</b></td>"
            f"<td>{escudo_img(clube.sigla, clube.escudo_emoji)} {clube.nome}"
            f"<span class='rank-div'>Série {clube.divisao}</span></td>"
            f"<td class='num'>{clube.pontos}</td>"
            f"<td class='num'>{clube.jogos_campeonato}</td>"
            f"<td class='num'>{clube.vitorias}</td>"
            f"<td class='num'>{clube.empates}</td>"
            f"<td class='num'>{clube.derrotas}</td>"
            f"<td class='num'>{clube.gols_pro}</td>"
            f"<td class='num'>{clube.gols_contra}</td>"
            f"<td class='num'>{clube.saldo_gols:+d}</td>"
            f"<td class='num'>{100.0 * clube.pontos / max(1, 3 * clube.jogos_campeonato):.0f}%</td>"
            "</tr>"
        )
    return (
        "<table class='tbl'><thead><tr>"
        "<th class='num'>#</th><th>Clube</th><th class='num'>Pts</th>"
        "<th class='num'>J</th><th class='num'>V</th><th class='num'>E</th>"
        "<th class='num'>D</th><th class='num'>GP</th><th class='num'>GC</th>"
        "<th class='num'>SG</th><th class='num'>%</th>"
        "</tr></thead><tbody>" + "".join(corpo) + "</tbody></table>"
    )


def _vazio(titulo: str, texto: str) -> None:
    st.markdown(
        f'<div class="vazio"><div class="vazio-ico">📈</div>'
        f"<b>{titulo}</b><p>{texto}</p></div>",
        unsafe_allow_html=True,
    )
