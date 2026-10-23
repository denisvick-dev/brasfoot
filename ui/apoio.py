"""
Funções de apoio: leitura do estado do jogo, formatação e tabelas.
"""

import datetime as dt

import streamlit as st

from game.banco_dados import (
    DIVISOES,
    NOMES_DIVISAO,
)
from game.campeonato import League
from game.divisao import Fase as FaseDivisao
from game.escudos import imagem as escudo_img
from game.modelos import Partida, Time
from game.piramide import Piramide, data_da_rodada as data_semana
from game.regional import TorneioRegional


def init_game():
    """Inicializa um novo jogo."""
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
    if "times" not in st.session_state:
        st.session_state.times = None
    if "league" not in st.session_state:
        st.session_state.league = None
    if "piramide" not in st.session_state:
        st.session_state.piramide = None
    if "market" not in st.session_state:
        st.session_state.market = None
    if "meu_time" not in st.session_state:
        st.session_state.meu_time = None
    if "ultimo_resultado" not in st.session_state:
        st.session_state.ultimo_resultado = None
    if "ultima_rodada" not in st.session_state:
        st.session_state.ultima_rodada = []
    if "pagina" not in st.session_state:
        st.session_state.pagina = "inicio"


def get_meu_time() -> Time | None:
    """Retorna o time do jogador."""
    if not st.session_state.times:
        return None
    for t in st.session_state.times:
        if t.nome == st.session_state.meu_time:
            return t
    return None


def barra_status() -> None:
    """Barra superior com o resumo do clube (clube, série, rodada, posição, caixa)."""
    time = get_meu_time()
    if time is None:
        return
    league = st.session_state.league
    posicao = posicao_na_tabela(league, time.nome)
    posicao_html = f"{posicao}º" if posicao else "—"
    st.markdown(
        f"""
    <div class="status-bar">
        <div class="sb-clube">
            {escudo_img(time.sigla, time.escudo_emoji, "escudo-mini")}
            <span>{time.nome}</span>
        </div>
        <div class="sb-item">Série <b>{divisao_do_jogador()}</b></div>
        <div class="sb-item">Rodada <b>{league.rodada_atual}/{league.total_rodadas}</b></div>
        <div class="sb-item">Posição <b>{posicao_html}</b></div>
        <div class="sb-item sb-right">💰 Caixa <b>{formatar_dinheiro(time.financas)}</b></div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def formatar_dinheiro(valor: int) -> str:
    """Formata valor monetário."""
    if valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.1f}M"
    elif valor >= 1_000:
        return f"R$ {valor / 1_000:.0f}K"
    return f"R$ {valor:,.0f}"


def cor_posicao(posicao: str) -> str:
    """Retorna cor da posição."""
    cores = {
        "GOL": "🟡",
        "ZAG": "🔵",
        "LAT": "🟢",
        "VOL": "🟠",
        "MEI": "🟣",
        "ATA": "🔴",
    }
    return cores.get(posicao, "⚪")


def badge_overall(ovr: int) -> str:
    """Crachá colorido de overall."""
    if ovr >= 80:
        classe = "b-80"
    elif ovr >= 70:
        classe = "b-70"
    elif ovr >= 60:
        classe = "b-60"
    else:
        classe = "b-50"
    return f'<span class="badge {classe}">{ovr}</span>'


def barra_energia(valor: int) -> str:
    """Cria barra visual de energia."""
    if valor >= 70:
        cor = "#16A34A"
    elif valor >= 40:
        cor = "#F5B301"
    else:
        cor = "#DC2626"
    return (
        f'<div class="energy" title="{valor}%">'
        f'<i style="width:{max(0, min(100, valor))}%;'
        f'background:linear-gradient(90deg,{cor},{cor}BB)"></i></div>'
    )


def secao(titulo: str, kicker: str = ""):
    """Título de seção padronizado."""
    k = f'<span class="kicker">{kicker}</span>' if kicker else ""
    st.markdown(f'<div class="sec-title">{k}{titulo}</div>', unsafe_allow_html=True)


def stat_card(titulo: str, valor, cor: str = "#16A34A"):
    """Cria um card de estatística."""
    st.markdown(
        f"""
    <div class="stat" style="--accent:{cor}">
        <div class="lbl">{titulo}</div>
        <div class="val">{valor}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def posicao_na_tabela(league: League, nome: str) -> int:
    """Posição do time na classificação (1-based)."""
    for i, t in enumerate(league.classificacao):
        if t.nome == nome:
            return i + 1
    return 0


def get_piramide() -> Piramide | None:
    """A temporada com todas as divisões, se a carreira já começou."""
    return st.session_state.get("piramide")


def get_copa():
    """A Copa do Brasil da temporada (``None`` se não existir)."""
    piramide = get_piramide()
    return piramide.copa if piramide is not None else None


def copa_da_rodada(rodada: int) -> list[tuple[str, str, Partida | None]]:
    """Jogos da Copa do Brasil numa rodada da temporada (resultado ou tabela)."""
    copa = get_copa()
    if copa is None:
        return []
    jogados: list[tuple[str, str, Partida | None]] = [
        (p.time_casa, p.time_fora, p) for p in copa.resultados.get(rodada, [])
    ]
    return jogados or copa.confrontos_da_rodada(rodada)


def copa_rodadas_com_jogos() -> list[int]:
    """Rodadas da temporada em que a Copa do Brasil tem jogos."""
    piramide = get_piramide()
    if piramide is None or piramide.copa is None:
        return []
    return [r for r in range(1, piramide.total_rodadas_global + 1) if copa_da_rodada(r)]


def get_regionais() -> list[TorneioRegional]:
    """Torneios regionais da temporada (Rio-SP, Sul-Minas, Nordeste)."""
    piramide = get_piramide()
    return piramide.regionais if piramide is not None else []


def time_por_nome(nome: str) -> Time | None:
    """Objeto ``Time`` a partir do nome do clube."""
    for time in st.session_state.get("times") or []:
        if time.nome == nome:
            return time
    return None


def sigla_de(nome: str) -> str:
    """Sigla de um clube da temporada."""
    for time in st.session_state.get("times") or []:
        if time.nome == nome:
            return time.sigla
    return nome[:3].upper()


def divisoes_da_temporada() -> list[str]:
    """Divisões que existem na temporada atual (a do jogador primeiro)."""
    piramide = get_piramide()
    if piramide is None:
        return [DIVISOES[0]]
    ordem = piramide.ordem
    minha = divisao_do_jogador()
    if minha in ordem:
        ordem = [minha] + [d for d in ordem if d != minha]
    return ordem


def divisao_do_jogador() -> str:
    """Divisão em que o clube do jogador está jogando."""
    time = get_meu_time()
    piramide = get_piramide()
    if time is None:
        return DIVISOES[0]
    if piramide is not None:
        return piramide.divisao_de(time.nome) or time.divisao
    return time.divisao


def classificacao_de(divisao: str) -> list[Time]:
    """Classificação de uma divisão (cai na liga atual se não houver pirâmide)."""
    piramide = get_piramide()
    if piramide is not None and divisao in piramide.divisoes:
        return piramide.classificacao(divisao)
    league = st.session_state.get("league")
    return league.classificacao if league is not None else []


def rodada_de(divisao: str) -> int:
    piramide = get_piramide()
    if piramide is not None and divisao in piramide.divisoes:
        return piramide.rodada(divisao)
    league = st.session_state.get("league")
    return league.rodada_atual if league is not None else 0


def total_rodadas_de(divisao: str) -> int:
    piramide = get_piramide()
    if piramide is not None and divisao in piramide.divisoes:
        return piramide.total_rodadas(divisao)
    league = st.session_state.get("league")
    return league.total_rodadas if league is not None else 0


def calendario_de(divisao: str) -> list[list[tuple[str, str]]]:
    piramide = get_piramide()
    if piramide is not None and divisao in piramide.divisoes:
        return piramide.calendario(divisao)
    league = st.session_state.get("league")
    return league.calendario if league is not None else []


def confrontos_da_rodada(
    divisao: str, rodada: int
) -> list[tuple[str, str, Partida | None]]:
    """Jogos de uma rodada (1-based), com o resultado quando já disputado."""
    piramide = get_piramide()
    if piramide is not None and divisao in piramide.divisoes:
        return piramide.confrontos_da_rodada(divisao, rodada)
    league = st.session_state.get("league")
    if league is None:
        return []
    partidas = {
        p.time_casa + "|" + p.time_fora: p for p in league.resultados.get(rodada, [])
    }
    return [
        (casa, fora, partidas.get(f"{casa}|{fora}"))
        for casa, fora in (
            league.calendario[rodada - 1] if rodada <= len(league.calendario) else []
        )
    ]


def jogos_do_time(
    nome: str, divisao: str
) -> list[tuple[int, str, str, Partida | None]]:
    """Calendário de um clube: ``(rodada, casa, fora, partida)``."""
    piramide = get_piramide()
    if piramide is not None and divisao in piramide.divisoes:
        return piramide.jogos_do_time(nome, divisao)
    league = st.session_state.get("league")
    if league is None:
        return []
    jogos: list[tuple[int, str, str, Partida | None]] = []
    for rodada, jogos_rodada in enumerate(league.calendario, start=1):
        for casa, fora in jogos_rodada:
            if nome not in (casa, fora):
                continue
            partida = next(
                (
                    p
                    for p in league.resultados.get(rodada, [])
                    if p.time_casa == casa and p.time_fora == fora
                ),
                None,
            )
            jogos.append((rodada, casa, fora, partida))
    return jogos


def data_da_rodada(divisao: str, rodada: int) -> dt.date:
    """Data (fictícia, semanal) de uma rodada — a temporada começa nos regionais."""
    piramide = get_piramide()
    league = st.session_state.get("league")
    temporada = (
        piramide.temporada if piramide else (league.temporada if league else 2026)
    )
    deslocamento = piramide.rodadas_regionais if piramide is not None else 0
    return data_semana(rodada + deslocamento, temporada)


def data_global(rodada: int, temporada: int | None = None) -> dt.date:
    """Data (semanal) de uma rodada global da temporada."""
    ano = temporada if temporada is not None else temporada_atual()
    return data_semana(rodada, ano)


def temporada_atual() -> int:
    """Ano da temporada em curso."""
    piramide = get_piramide()
    if piramide is not None:
        return piramide.temporada
    league = st.session_state.get("league")
    return league.temporada if league is not None else 2026


def zona_da_posicao(divisao: str, pos: int, total: int) -> tuple[str, str]:
    """(cor, rótulo) da faixa da tabela em que a posição cai."""
    if divisao == "A":
        if pos <= 4:
            return "#16A34A", "Libertadores"
        if pos <= 6:
            return "#F5B301", "Sul-Americana"
        if pos > total - 4:
            return "#DC2626", "Rebaixamento"
    else:
        if pos <= 4:
            return "#16A34A", "Acesso"
        if pos > total - 4:
            return "#DC2626", "Rebaixamento"
    return "#CBD5E1", "Meio de tabela"


def linhas_classificacao(
    divisao: str, fase_idx: int = 0, grupo: str | None = None
) -> list[dict]:
    """Linhas (com estatísticas da fase) da classificação de uma divisão."""
    piramide = get_piramide()
    if piramide is not None and divisao in piramide.divisoes:
        return piramide.tabela(divisao, fase_idx, grupo)
    league = st.session_state.get("league")
    if league is None:
        return []
    return [
        {
            "time": t,
            "pts": t.pontos,
            "j": t.jogos_campeonato,
            "v": t.vitorias,
            "e": t.empates,
            "d": t.derrotas,
            "gp": t.gols_pro,
            "gc": t.gols_contra,
            "sg": t.saldo_gols,
        }
        for t in league.classificacao
    ]


def tabela_html(
    linhas: list[dict],
    time: Time | None = None,
    divisao: str = "A",
    com_zona: bool = True,
) -> str:
    """HTML de uma tabela de classificação a partir das linhas da fase."""
    total = len(linhas)
    html = []
    for i, linha in enumerate(linhas):
        pos = i + 1
        clube: Time = linha["time"]
        zona, zona_txt = (
            zona_da_posicao(divisao, pos, total) if com_zona else ("#CBD5E1", "")
        )
        me = "me" if time is not None and clube.nome == time.nome else ""
        sg = linha["sg"]
        sg_html = (
            f'<span class="pill {"p-ok" if sg > 0 else "p-bad" if sg < 0 else "p-info"}">'
            f"{sg:+d}</span>"
        )
        html.append(
            f"<tr class='{me}' title='{zona_txt}'>"
            f"<td class='num'><b>{pos}º</b></td>"
            f"<td class='num'><span class='zona' style='background:{zona}'></span></td>"
            f"<td>{escudo_img(clube.sigla, clube.escudo_emoji)} {clube.nome}</td>"
            f"<td class='num'><b>{linha['pts']}</b></td>"
            f"<td class='num'>{linha['j']}</td>"
            f"<td class='num'>{linha['v']}</td>"
            f"<td class='num'>{linha['e']}</td>"
            f"<td class='num'>{linha['d']}</td>"
            f"<td class='num'>{linha['gp']}</td>"
            f"<td class='num'>{linha['gc']}</td>"
            f"<td class='num'>{sg_html}</td>"
            f"<td class='num'>{badge_overall(clube.overall_time)}</td>"
            "</tr>"
        )
    return (
        "<table class='tbl'><thead><tr>"
        "<th class='num'>#</th><th class='num'>Zona</th><th>Time</th>"
        "<th class='num'>Pts</th><th class='num'>J</th><th class='num'>V</th>"
        "<th class='num'>E</th><th class='num'>D</th><th class='num'>GP</th>"
        "<th class='num'>GC</th><th class='num'>SG</th><th class='num'>OVR</th>"
        "</tr></thead><tbody>" + "".join(html) + "</tbody></table>"
    )


def tabela_classificacao(
    divisao: str, time: Time | None = None, com_zona: bool = True
) -> str:
    """HTML da classificação da primeira fase de uma divisão."""
    return tabela_html(
        linhas_classificacao(divisao), time=time, divisao=divisao, com_zona=com_zona
    )


def legenda_zonas(divisao: str) -> str:
    """Legenda das faixas da tabela de uma divisão."""
    if divisao == "A":
        itens = [
            ("#16A34A", "Libertadores (1º–4º)"),
            ("#F5B301", "Sul-Americana (5º–6º)"),
            ("#DC2626", "Rebaixamento (últimos 4)"),
        ]
    elif divisao == "D":
        itens = [("#16A34A", "Acesso à Série C (1º–4º)")]
    else:
        itens = [
            ("#16A34A", "Acesso à divisão de cima (1º–4º)"),
            ("#DC2626", "Rebaixamento (últimos 4)"),
        ]
    spans = " · ".join(
        f'<span class="zona" style="background:{cor}"></span> {txt}'
        for cor, txt in itens
    )
    return f'<div class="legenda" style="margin-top:.8rem">{spans}</div>'


def _html_tabela(linhas: list[dict]) -> str:
    """Monta a tabela HTML de classificação (linhas já ordenadas)."""
    corpo = []
    for i, l in enumerate(linhas, 1):
        t = l["time"]
        sg = l["sg"]
        classe_sg = "p-ok" if sg > 0 else "p-bad" if sg < 0 else "p-info"
        corpo.append(
            f"<tr><td class='num'>{i}º</td>"
            f"<td>{escudo_img(t.sigla, t.escudo_emoji)} {t.nome}</td>"
            f"<td class='num'><b>{l['pts']}</b></td>"
            f"<td class='num'>{l['j']}</td>"
            f"<td class='num'>{l['v']}</td>"
            f"<td class='num'>{l['e']}</td>"
            f"<td class='num'>{l['d']}</td>"
            f"<td class='num'>{l['gp']}</td>"
            f"<td class='num'>{l['gc']}</td>"
            f"<td class='num'><span class='pill {classe_sg}'>{sg:+d}</span></td></tr>"
        )
    return (
        "<table class='tbl'><thead><tr><th class='num'>#</th><th>Time</th>"
        "<th class='num'>Pts</th><th class='num'>J</th><th class='num'>V</th>"
        "<th class='num'>E</th><th class='num'>D</th><th class='num'>GP</th>"
        "<th class='num'>GC</th><th class='num'>SG</th></tr></thead><tbody>"
        + "".join(corpo)
        + "</tbody></table>"
    )


def _sigla(divisao: str, nome: str) -> str:
    piramide = get_piramide()
    if piramide is not None and divisao in piramide.divisoes:
        for time in piramide.league(divisao).times:
            if time.nome == nome:
                return time.sigla
    return nome[:3].upper()


def _rodada_global(divisao: str, fase: FaseDivisao, rodada_da_fase: int) -> int:
    """Converte a rodada dentro da fase para a rodada global da temporada."""
    piramide = get_piramide()
    if piramide is None or divisao not in piramide.divisoes:
        return rodada_da_fase
    temporada = piramide.league(divisao)
    base = 0
    for outra in temporada.fases:
        if outra is fase:
            return base + rodada_da_fase
        base += outra.total_rodadas
    return base + rodada_da_fase


def _fases_da_divisao(divisao: str) -> list[tuple[str, FaseDivisao]]:
    """(nome, fase) das fases já criadas na temporada de uma divisão."""
    piramide = get_piramide()
    if piramide is None or divisao not in piramide.divisoes:
        return []
    temporada = piramide.league(divisao)
    return [(f.nome, f) for f in temporada.fases]


def _resultado_mata(divisao: str, fase: FaseDivisao) -> str:
    """Resumo em HTML dos confrontos de uma fase eliminatória."""
    piramide = get_piramide()
    linhas = []
    for casa, fora in getattr(fase, "pares", []):
        gols_casa = gols_fora = 0
        for i, (c, f) in enumerate([(casa, fora), (fora, casa)][: fase.total_rodadas]):
            partida = (
                piramide.partida(divisao, _rodada_global(divisao, fase, i + 1), c, f)
                if piramide
                else None
            )
            if partida is None:
                continue
            if partida.time_casa == casa:
                gols_casa += partida.gols_casa
                gols_fora += partida.gols_fora
            else:
                gols_casa += partida.gols_fora
                gols_fora += partida.gols_casa
        vencedores = {t.nome for t in fase.vencedores}
        cls_c = "v" if casa in vencedores else ("d" if vencedores else "")
        cls_f = "v" if fora in vencedores else ("d" if vencedores else "")
        linhas.append(
            f'<div class="res"><span class="tag {cls_c}">{_sigla(divisao, casa)}</span>'
            f"<span>{casa}</span>"
            f"<span style='margin-left:auto'><b>{gols_casa} x {gols_fora}</b></span>"
            f"<span>{fora}</span>"
            f'<span class="tag {cls_f}">{_sigla(divisao, fora)}</span></div>'
        )
    return "".join(linhas)


def _rotulo_competicao(chave: str) -> str:
    """Nome amigável de uma competição da rodada."""
    if chave in NOMES_DIVISAO:
        return NOMES_DIVISAO[chave]
    if chave == "COPA":
        return "Copa do Brasil"
    if chave == "SUPERCOPA":
        return "Supercopa do Brasil"
    piramide = get_piramide()
    if piramide is not None:
        torneio = piramide.torneio(chave)
        if torneio is not None:
            return torneio.nome
    return chave
