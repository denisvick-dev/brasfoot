"""
Classificação, calendário e resultados de todas as competições.
"""

import streamlit as st

from game.banco_dados import (
    NOMES_DIVISAO,
)
from game.copa import REGULAMENTO as REGULAMENTO_COPA, FaseCopa
from game.escudos import imagem as escudo_img
from game.modelos import Partida, Time
from game.piramide import data_da_rodada as data_semana
from game.regional import REGULAMENTO as REGULAMENTO_REGIONAL, TorneioRegional
from ui.apoio import (
    _fases_da_divisao,
    _resultado_mata,
    badge_overall,
    classificacao_de,
    confrontos_da_rodada,
    copa_da_rodada,
    copa_rodadas_com_jogos,
    cor_posicao,
    data_da_rodada,
    data_global,
    divisao_do_jogador,
    divisoes_da_temporada,
    get_copa,
    get_meu_time,
    get_piramide,
    get_regionais,
    hero,
    jogos_do_time,
    legenda_zonas,
    linhas_classificacao,
    rodada_de,
    secao,
    sigla_de,
    tabela_classificacao,
    tabela_html,
    temporada_atual,
    total_rodadas_de,
)
from ui.jogar import _linha_do_tempo


def _copa_fase_html(fase: FaseCopa) -> str:
    """HTML dos confrontos de uma fase da Copa do Brasil (agregado dos 2 jogos)."""
    copa = get_copa()
    time = get_meu_time()
    linhas = []
    for forte, fraco in fase.pares:
        gols_forte = gols_fraco = 0
        for i, rodada in enumerate(fase.rodadas):
            casa, fora = (fraco, forte) if i == 0 else (forte, fraco)
            partida = copa.partida(rodada, casa, fora) if copa is not None else None
            if partida is None:
                continue
            if partida.time_casa == forte:
                gols_forte += partida.gols_casa
                gols_fraco += partida.gols_fora
            else:
                gols_forte += partida.gols_fora
                gols_fraco += partida.gols_casa
        vencedores = {t.nome for t in fase.vencedores}
        cls_f = "v" if forte in vencedores else ("d" if vencedores else "")
        cls_x = "v" if fraco in vencedores else ("d" if vencedores else "")
        meu = time is not None and time.nome in (forte, fraco)
        estilo = "border-color:var(--brand);background:#F2FBF5" if meu else ""
        linhas.append(
            f'<div class="res" style="{estilo}">'
            f'<span class="tag {cls_f}">{sigla_de(forte)}</span>'
            f"<span>{forte}</span>"
            f"<span style='margin-left:auto'><b>{gols_forte} x {gols_fraco}</b></span>"
            f"<span>{fraco}</span>"
            f'<span class="tag {cls_x}">{sigla_de(fraco)}</span></div>'
        )
    return "".join(linhas)


def _aba_copa_classificacao():
    """Conteúdo da aba da Copa do Brasil nas classificações."""
    copa = get_copa()
    if copa is None:
        st.info("A Copa do Brasil não foi montada nesta temporada (poucos clubes).")
        return

    fase = copa.fases[-1] if copa.fases else None
    situacao = (
        f"campeão: {copa.campeao.nome}"
        if copa.campeao is not None
        else (f"fase atual: {fase.nome}" if fase is not None else "sem jogos")
    )
    st.markdown(
        f'<div class="club-meta">🏆 Copa do Brasil · {len(copa.times)} clubes · '
        f"mata-mata em ida e volta · {situacao}</div>",
        unsafe_allow_html=True,
    )

    if copa.campeao is not None:
        st.success(f"🏆 Campeão: **{copa.campeao.nome}**")

    for fase_copa in reversed(copa.fases):
        estado = "encerrada" if fase_copa.concluida else "em disputa"
        secao(
            fase_copa.nome,
            f"{len(fase_copa.pares)} confrontos · {estado}",
        )
        st.markdown(_copa_fase_html(fase_copa), unsafe_allow_html=True)

    with st.expander("📖 Regulamento da Copa do Brasil"):
        st.markdown("".join(f"- {regra}\n" for regra in REGULAMENTO_COPA))


def _regional_meta(torneio: TorneioRegional) -> str:
    """Linha de contexto de um torneio regional."""
    if torneio.campeao is not None:
        situacao = f"campeão: {torneio.campeao.nome}"
    else:
        situacao = f"{torneio.fase_atual.nome} · {torneio.regiao.resumo}"
    return (
        f'<div class="club-meta">🏆 {torneio.nome} · {len(torneio.times)} clubes · '
        f"{situacao}</div>"
    )


def _regional_tabelas(torneio: TorneioRegional, time: Time | None) -> None:
    """As tabelas dos grupos do torneio."""
    grupos = sorted(torneio.grupos)
    colunas = st.columns(min(3, len(grupos)))
    for i, letra in enumerate(grupos):
        with colunas[i % len(colunas)]:
            st.markdown(
                f"<div class='sec-title' style='font-size:.95rem'>Grupo {letra}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                tabela_html(torneio.tabela(letra), time=time, com_zona=False),
                unsafe_allow_html=True,
            )


def _regional_mata_html(torneio: TorneioRegional, fase) -> str:
    """HTML dos confrontos eliminatórios de um torneio regional."""
    time = get_meu_time()
    vencedores = {t.nome for t in fase.vencedores}
    linhas = []
    jogos = fase.jogos
    pares = fase.pares or [
        (jogo.time_casa, jogo.time_fora) for jogo in jogos if fase.nome != "Final"
    ]
    if fase.nome == "Final" and not pares and len(torneio.fases) >= 2:
        finalistas = torneio.fases[-2].vencedores
        if len(finalistas) == 2:
            pares = [(finalistas[0].nome, finalistas[1].nome)]
    for casa, fora in pares:
        gols_casa = gols_fora = 0
        partidas = [
            jogo for jogo in jogos if {jogo.time_casa, jogo.time_fora} == {casa, fora}
        ]
        for jogo in partidas:
            if jogo.time_casa == casa:
                gols_casa += jogo.gols_casa
                gols_fora += jogo.gols_fora
            else:
                gols_casa += jogo.gols_fora
                gols_fora += jogo.gols_casa
        prossegue = bool(vencedores) and ((casa in vencedores) or (fora in vencedores))
        cls_c = (
            "v" if casa in vencedores else ("d" if prossegue or fase.concluida else "")
        )
        cls_f = (
            "v" if fora in vencedores else ("d" if prossegue or fase.concluida else "")
        )
        meu = time is not None and time.nome in (casa, fora)
        estilo = "border-color:var(--brand);background:#F2FBF5" if meu else ""
        placar = (
            f"<b>{gols_casa} x {gols_fora}</b>"
            if partidas
            else "<span style='color:var(--ink-3)'>a jogar</span>"
        )
        linhas.append(
            f'<div class="res" style="{estilo}">'
            f'<span class="tag {cls_c}">{sigla_de(casa)}</span>'
            f"<span>{escudo_img(sigla_de(casa))} {casa}</span>"
            f"<span style='margin-left:auto'>{placar}</span>"
            f"<span>{fora} {escudo_img(sigla_de(fora))}</span>"
            f'<span class="tag {cls_f}">{sigla_de(fora)}</span></div>'
        )
    return "".join(linhas)


def _aba_regionais_classificacao() -> None:
    """Aba dos torneios regionais nas classificações."""
    piramide = get_piramide()
    if piramide is None or not piramide.regionais:
        st.info(
            "Os torneios regionais não foram montados nesta temporada "
            "(são necessários 8 clubes da região)."
        )
        return
    time = get_meu_time()
    torneios = piramide.regionais
    chave = st.selectbox(
        "Torneio",
        [t.chave for t in torneios],
        format_func=lambda k: next((t.nome for t in torneios if t.chave == k), str(k)),
        key="regional_classificacao",
    )
    torneio = piramide.torneio(chave)
    if torneio is None:
        return
    st.markdown(_regional_meta(torneio), unsafe_allow_html=True)
    _regional_tabelas(torneio, time)
    for fase in torneio.fases:
        if fase.tipo != "mata":
            continue
        estado = "encerrada" if fase.concluida else "em disputa"
        secao(fase.nome, f"{len(fase.pares) or len(fase.jogos)} confrontos · {estado}")
        st.markdown(_regional_mata_html(torneio, fase), unsafe_allow_html=True)
    if torneio.campeao is not None:
        st.success(f"🏆 Campeão: **{torneio.campeao.nome}**")
    with st.expander("📖 Regulamento do torneio"):
        st.markdown("".join(f"- {regra}\n" for regra in REGULAMENTO_REGIONAL))


def _aba_regionais_calendario() -> None:
    """Aba dos torneios regionais no calendário."""
    piramide = get_piramide()
    if piramide is None or not piramide.regionais:
        st.info("Os torneios regionais não foram montados nesta temporada.")
        return
    time = get_meu_time()
    torneios = piramide.regionais
    chave = st.selectbox(
        "Torneio",
        [t.chave for t in torneios],
        format_func=lambda k: next((t.nome for t in torneios if t.chave == k), str(k)),
        key="regional_calendario",
    )
    torneio = piramide.torneio(chave)
    if torneio is None:
        return
    st.markdown(_regional_meta(torneio), unsafe_allow_html=True)
    ano = piramide.temporada
    rodada = st.selectbox(
        "Rodada da temporada",
        torneio.datas,
        index=min(torneio._jogo_atual, len(torneio.datas) - 1),
        format_func=lambda r, _ano=ano: f"Rodada {r} · {data_semana(r, _ano):%d/%m/%Y}",
        key="regional_calendario_rodada",
    )
    confrontos = torneio.confrontos_da_rodada(rodada)
    if not confrontos:
        st.info("Nenhum jogo nesta rodada.")
    for casa, fora, partida in confrontos:
        destaque = time is not None and time.nome in (casa, fora)
        estilo = "border-color:var(--brand);background:#F2FBF5" if destaque else ""
        if partida is not None:
            placar = f"<b>{partida.gols_casa} x {partida.gols_fora}</b>"
            extra = partida.fase
        else:
            placar = "<span style='color:var(--ink-3)'>x</span>"
            extra = "a jogar"
        st.markdown(
            f"""
        <div class="res" style="{estilo}">
            <span>🏆 {escudo_img(sigla_de(casa))} {casa} {placar} {fora} {escudo_img(sigla_de(fora))}</span>
            <span style="margin-left:auto;color:var(--ink-3);font-size:.78rem">{extra}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )


def tela_classificacao():
    time = get_meu_time()
    league = st.session_state.league
    divisoes = divisoes_da_temporada()
    piramide_atual = get_piramide()
    rodada_geral = (
        piramide_atual.rodada_global
        if piramide_atual is not None
        else league.rodada_atual
    )

    hero(
        "Classificações",
        f"Temporada {league.temporada} · {len(divisoes)} divisões · "
        f"rodada geral {rodada_geral}",
        kicker="🏆 Tabelas",
        emoji="",
        chips=(
            f"{len(divisoes)} divisões",
            f"rodada {rodada_geral}",
            "Copa do Brasil" if get_copa() is not None else "sem copa",
        ),
    )

    rotulos = [f"🏆 {NOMES_DIVISAO.get(d, d)}" for d in divisoes]
    tem_copa = get_copa() is not None
    tem_regionais = bool(get_regionais())
    extras = []
    if tem_copa:
        extras.append("🏆 Copa do Brasil")
    if tem_regionais:
        extras.append("🌎 Regionais")
    abas = st.tabs([*rotulos, *extras, "⚽ Artilharia"])

    for aba, divisao in zip(abas, divisoes, strict=False):
        with aba:
            temporada = (
                piramide_atual.league(divisao)
                if piramide_atual is not None and divisao in piramide_atual.divisoes
                else None
            )
            situacao = (
                f"rodada {rodada_de(divisao)}/{total_rodadas_de(divisao)}"
                if rodada_de(divisao) < total_rodadas_de(divisao)
                else "encerrada"
            )
            st.markdown(
                f'<div class="club-meta">🏁 {NOMES_DIVISAO.get(divisao, divisao)} · '
                f"{len(classificacao_de(divisao))} clubes · {situacao}"
                + (
                    f" · fase atual: {temporada.fase_atual.nome}"
                    if temporada is not None
                    else ""
                )
                + "</div>",
                unsafe_allow_html=True,
            )

            fases = _fases_da_divisao(divisao)
            if not fases:
                # modo antigo (sem pirâmide): tabela única
                st.markdown(tabela_classificacao(divisao, time), unsafe_allow_html=True)
                st.markdown(legenda_zonas(divisao), unsafe_allow_html=True)
                continue

            for i, (nome_fase, fase) in enumerate(fases):
                if fase.tipo == "mata":
                    secao(nome_fase, f"{len(fase.pares)} confrontos")
                    st.markdown(_resultado_mata(divisao, fase), unsafe_allow_html=True)
                    continue

                if fase.tipo == "pontos":
                    titulo = "1ª fase · turno único"
                else:
                    titulo = nome_fase
                secao(titulo, f"rodada {fase.rodada_atual}/{fase.total_rodadas}")
                grupos = sorted(fase.grupos) if len(fase.grupos) > 1 else ["Geral"]
                if len(grupos) == 1:
                    st.markdown(
                        tabela_html(
                            temporada.tabela(fase)
                            if temporada
                            else linhas_classificacao(divisao),
                            time=time,
                            divisao=divisao,
                        ),
                        unsafe_allow_html=True,
                    )
                else:
                    colunas = st.columns(min(4, len(grupos)))
                    for j, letra in enumerate(grupos):
                        with colunas[j % len(colunas)]:
                            st.markdown(
                                f"<div class='sec-title' style='font-size:.95rem'>"
                                f"Grupo {letra}</div>",
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                tabela_html(
                                    temporada.tabela(fase, letra) if temporada else [],
                                    time=time,
                                    divisao=divisao,
                                    com_zona=len(grupos) <= 4,
                                ),
                                unsafe_allow_html=True,
                            )
                if i == 0:
                    st.markdown(legenda_zonas(divisao), unsafe_allow_html=True)

            # regulamento da divisão
            regras = (
                piramide_atual.regulamento(divisao)
                if piramide_atual is not None
                else []
            )
            if regras:
                with st.expander("📖 Regulamento da divisão"):
                    st.markdown("".join(f"- {regra}\n" for regra in regras))

    indice_extra = len(divisoes)
    if tem_copa:
        with abas[indice_extra]:
            _aba_copa_classificacao()
        indice_extra += 1
    if tem_regionais:
        with abas[indice_extra]:
            _aba_regionais_classificacao()

    with abas[-1]:
        divisao_art = st.selectbox(
            "Divisão",
            divisoes,
            index=divisoes.index(divisao_do_jogador())
            if divisao_do_jogador() in divisoes
            else 0,
            format_func=lambda d: NOMES_DIVISAO.get(d, str(d)),
            key="artilharia_divisao",
        )
        secao("Artilheiros", f"{NOMES_DIVISAO.get(divisao_art, divisao_art)} · Top 20")
        piramide = get_piramide()
        liga_art = piramide.league(divisao_art) if piramide else league
        artilheiros = liga_art.artilharia(20)

        if artilheiros:
            linhas = []
            for i, (j, sigla) in enumerate(artilheiros):
                medal = {0: "🥇", 1: "🥈", 2: "🥉"}.get(i, f"{i + 1}º")
                me = "me" if time is not None and time.sigla == sigla else ""
                linhas.append(
                    f"<tr class='{me}'>"
                    f"<td class='num'>{medal}</td>"
                    f"<td><b>{j.nome}</b> "
                    f"<span style='color:var(--ink-3)'>{cor_posicao(j.posicao)} {j.posicao}</span></td>"
                    f"<td class='num'>{sigla}</td>"
                    f"<td class='num'>⚽ <b>{j.gols}</b></td>"
                    f"<td class='num'>🅰️ {j.assistencias}</td>"
                    f"<td class='num'>📋 {j.jogos}</td>"
                    f"<td class='num'>{badge_overall(j.overall)}</td>"
                    "</tr>"
                )
            st.markdown(
                "<table class='tbl'><thead><tr>"
                "<th class='num'>#</th><th>Jogador</th><th class='num'>Time</th>"
                "<th class='num'>Gols</th><th class='num'>Assist</th>"
                "<th class='num'>Jogos</th><th class='num'>OVR</th>"
                "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table>",
                unsafe_allow_html=True,
            )
        else:
            st.info("Nenhum gol marcado ainda.")


def tela_calendario():
    time = get_meu_time()
    divisoes = divisoes_da_temporada()
    minha = divisao_do_jogador()
    piramide = get_piramide()

    hero(
        "Calendário",
        f"Temporada {piramide.temporada if piramide else st.session_state.league.temporada}"
        " · uma rodada por semana · todas as divisões",
        kicker="📅 Temporada",
    )

    copa = get_copa()
    regionais = get_regionais()
    rotulos_cal = ["📅 Rodadas por divisão"]
    if copa is not None:
        rotulos_cal.append("🏆 Copa do Brasil")
    if regionais:
        rotulos_cal.append("🌎 Regionais")
    rotulos_cal.append("🗓️ Meus jogos")
    abas_cal = st.tabs(rotulos_cal)

    aba_rodadas = abas_cal[0]
    indice_cal = 1
    aba_copa = None
    if copa is not None:
        aba_copa = abas_cal[indice_cal]
        indice_cal += 1
    aba_regionais = None
    if regionais:
        aba_regionais = abas_cal[indice_cal]
        indice_cal += 1
    aba_meus = abas_cal[indice_cal]

    with aba_rodadas:
        col_div, col_rod = st.columns([1, 2])
        with col_div:
            divisao = st.selectbox(
                "Divisão",
                divisoes,
                index=divisoes.index(minha) if minha in divisoes else 0,
                format_func=lambda d: NOMES_DIVISAO.get(d, str(d)),
                key="calendario_divisao",
            )
        total = total_rodadas_de(divisao)
        atual = rodada_de(divisao)

        if total == 0:
            st.info("Essa divisão não tem calendário nesta temporada.")
            return

        ano = temporada_atual()
        desloc = piramide.rodadas_regionais if piramide is not None else 0

        def _rotulo_rodada_divisao(r: int, _ano: int = ano, _off: int = desloc) -> str:
            data_rotulo = data_semana(r + _off, _ano)
            return (
                f"Rodada {r} · {data_rotulo:%d/%m/%Y}"
                f"{' · disputada' if r <= atual else ''}"
            )

        with col_rod:
            rodada = st.selectbox(
                "Rodada",
                list(range(1, total + 1)),
                index=min(max(atual - 1, 0), total - 1),
                format_func=_rotulo_rodada_divisao,
                key="calendario_rodada",
            )

        data = data_da_rodada(divisao, rodada)
        st.markdown(
            f'<div class="club-meta">📅 {data:%d/%m/%Y} · '
            f"{NOMES_DIVISAO.get(divisao, divisao)} · rodada {atual}/{total} disputada</div>",
            unsafe_allow_html=True,
        )

        confrontos = confrontos_da_rodada(divisao, rodada)
        if not confrontos:
            st.info("Nenhum jogo nesta rodada.")
        for casa, fora, partida in confrontos:
            destaque = time is not None and time.nome in (casa, fora)
            estilo = "border-color:var(--brand);background:#F2FBF5" if destaque else ""
            if partida is not None:
                placar = f"<b>{partida.gols_casa} x {partida.gols_fora}</b>"
                extra = f"👥 {partida.publico:,}" if partida.publico else ""
            else:
                placar = "<span style='color:var(--ink-3)'>x</span>"
                extra = "a jogar"
            st.markdown(
                f"""
            <div class="res" style="{estilo}">
                <span>⚽ {casa} {placar} {fora}</span>
                <span style="margin-left:auto;color:var(--ink-3);font-size:.78rem">{extra}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

    if aba_copa is not None and copa is not None:
        with aba_copa:
            rodadas_copa = copa_rodadas_com_jogos()
            if not rodadas_copa:
                st.info(
                    "A Copa do Brasil ainda não tem jogos marcados nesta temporada."
                )
            else:
                rodada_copa = st.selectbox(
                    "Rodada da temporada",
                    rodadas_copa,
                    index=len(rodadas_copa) - 1,
                    format_func=lambda r, _ano=ano: (
                        f"Rodada {r} · {data_semana(r, _ano):%d/%m/%Y}"
                    ),
                    key="calendario_copa_rodada",
                )
                confrontos_copa = copa_da_rodada(rodada_copa)
                jogados = sum(1 for _, _, partida in confrontos_copa if partida)
                st.markdown(
                    f'<div class="club-meta">🏆 Copa do Brasil · {len(confrontos_copa)} '
                    f"jogos nesta rodada · {jogados} já disputados · "
                    f"{len(copa.times)} clubes</div>",
                    unsafe_allow_html=True,
                )
                for casa, fora, partida in confrontos_copa:
                    destaque = time is not None and time.nome in (casa, fora)
                    estilo = (
                        "border-color:var(--brand);background:#F2FBF5"
                        if destaque
                        else ""
                    )
                    if partida is not None:
                        placar = f"<b>{partida.gols_casa} x {partida.gols_fora}</b>"
                        extra = (
                            f"{partida.fase} · {partida.grupo}"
                            if partida.fase
                            else "encerrado"
                        )
                    else:
                        placar = "<span style='color:var(--ink-3)'>x</span>"
                        extra = "a jogar"
                    st.markdown(
                        f"""
                    <div class="res" style="{estilo}">
                        <span>🏆 {casa} {placar} {fora}</span>
                        <span style="margin-left:auto;color:var(--ink-3);font-size:.78rem">{extra}</span>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

            secao("Fases da copa", "Chave")
            for fase in copa.fases:
                estado = "encerrada" if fase.concluida else "em disputa"
                st.markdown(
                    f'<div class="res"><span>🏆 <b>{fase.nome}</b></span>'
                    f'<span style="margin-left:auto;color:var(--ink-3);font-size:.78rem">'
                    f"{len(fase.pares)} confrontos · ida e volta · {estado}</span></div>",
                    unsafe_allow_html=True,
                )
            if copa.campeao is not None:
                st.success(f"🏆 Campeão da Copa do Brasil: **{copa.campeao.nome}**")

    if aba_regionais is not None:
        with aba_regionais:
            _aba_regionais_calendario()

    with aba_meus:
        if time is None:
            st.info("Selecione um time para ver o seu calendário.")
            return
        jogos: list[tuple[int, str, str, Partida | None, str]] = [
            (rodada, casa, fora, partida, "divisao")
            for rodada, casa, fora, partida in jogos_do_time(time.nome, minha)
        ]
        piramide_atual = get_piramide()
        if piramide_atual is not None:
            if piramide_atual.copa is not None:
                jogos += [
                    (rodada, casa, fora, partida, "copa")
                    for rodada, casa, fora, partida in piramide_atual.copa_jogos_do_time(
                        time.nome
                    )
                ]
            jogos += [
                (rodada, casa, fora, partida, "regional")
                for _, rodada, casa, fora, partida in (
                    piramide_atual.regional_jogos_do_time(time.nome)
                )
            ]
            if piramide_atual.supercopa is not None and time.nome in (
                piramide_atual.supercopa.time_casa,
                piramide_atual.supercopa.time_fora,
            ):
                jogos.append(
                    (
                        piramide_atual.total_rodadas_global,
                        piramide_atual.supercopa.time_casa,
                        piramide_atual.supercopa.time_fora,
                        piramide_atual.supercopa,
                        "supercopa",
                    )
                )
        deslocamento = piramide_atual.rodadas_regionais if piramide_atual else 0

        def _ordem(jogo: tuple[int, str, str, Partida | None, str]) -> int:
            """Rodada global do jogo (as divisões começam após os regionais)."""
            return jogo[0] + (deslocamento if jogo[4] == "divisao" else 0)

        jogos.sort(key=_ordem)
        if not jogos:
            st.info("Sem jogos no calendário.")
            return

        vitorias = empates = derrotas = 0
        linhas = []
        for rodada, casa, fora, partida, competicao in jogos:
            rodada_global = rodada + (deslocamento if competicao == "divisao" else 0)
            data = (
                data_da_rodada(minha, rodada)
                if competicao == "divisao"
                else data_global(rodada)
            )
            em_casa = casa == time.nome
            adversario = fora if em_casa else casa
            if partida is None:
                tag, cls, placar = (
                    "–",
                    "e",
                    "<span style='color:var(--ink-3)'>a jogar</span>",
                )
            else:
                meus = partida.gols_casa if em_casa else partida.gols_fora
                deles = partida.gols_fora if em_casa else partida.gols_casa
                placar = f"<b>{meus} x {deles}</b>"
                if meus > deles:
                    tag, cls = "V", "v"
                    vitorias += 1
                elif meus < deles:
                    tag, cls = "D", "d"
                    derrotas += 1
                else:
                    tag, cls = "E", "e"
                    empates += 1
            icone = {
                "copa": "🏆",
                "regional": "🌎",
                "supercopa": "🥇",
            }.get(competicao, "⚽")
            linhas.append(
                f"<div class='res'>"
                f"<span class='tag {cls}'>{tag}</span>"
                f"<span style='color:var(--ink-3);font-size:.8rem'>Rod. {rodada_global}</span>"
                f"<span style='color:var(--ink-3);font-size:.8rem'>{data:%d/%m}</span>"
                f"<span>{icone} {'🏠' if em_casa else '✈️'} {adversario}</span>"
                f"<span style='margin-left:auto'>{placar}</span>"
                f"</div>"
            )

        secao(
            "Meus jogos",
            f"{len(jogos)} jogos (divisão + copa) · {vitorias}V {empates}E {derrotas}D",
        )
        st.markdown("".join(linhas), unsafe_allow_html=True)


def tela_resultados():
    time = get_meu_time()
    divisoes = divisoes_da_temporada()

    hero(
        "Resultados por Rodada",
        f"Placares de todas as divisões na temporada "
        f"{st.session_state.league.temporada}",
        kicker="📊 Rodada a rodada",
    )

    rotulos = [f"📊 {NOMES_DIVISAO.get(d, d)}" for d in divisoes]
    tem_copa = get_copa() is not None
    tem_regionais = bool(get_regionais())
    extras = []
    if tem_copa:
        extras.append("🏆 Copa do Brasil")
    if tem_regionais:
        extras.append("🌎 Regionais")
    abas = st.tabs([*rotulos, *extras])
    for aba, divisao in zip(abas, divisoes, strict=False):
        with aba:
            atual = rodada_de(divisao)
            if atual == 0:
                st.info(
                    f"Nenhuma rodada disputada ainda na "
                    f"{NOMES_DIVISAO.get(divisao, divisao)}."
                )
                continue
            rodada_sel = st.selectbox(
                "Selecione a rodada",
                list(range(1, atual + 1)),
                index=atual - 1,
                key=f"resultados_rodada_{divisao}",
                format_func=lambda r: f"Rodada {r}",
            )
            secao(f"Rodada {rodada_sel}", NOMES_DIVISAO.get(divisao, divisao))
            for casa, fora, partida in confrontos_da_rodada(divisao, rodada_sel):
                if partida is None:
                    continue
                destaque = time is not None and time.nome in (casa, fora)
                st.markdown(
                    f"""
                <div class="res" style="{"border-color:var(--brand);background:#F2FBF5" if destaque else ""}">
                    <span style="{"font-weight:800" if destaque else ""}">⚽ {casa}
                    <b>{partida.gols_casa} x {partida.gols_fora}</b> {fora}</span>
                    <span style="margin-left:auto;color:var(--ink-3);font-size:.78rem">
                        👥 {partida.publico:,}
                    </span>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                if destaque and partida.eventos:
                    with st.expander("📋 Ver eventos da partida"):
                        _linha_do_tempo(partida.eventos)

    indice_extra = len(divisoes)
    if tem_copa:
        copa = get_copa()
        with abas[indice_extra]:
            rodadas_copa = (
                [r for r in sorted(copa.resultados) if copa.resultados[r]]
                if copa is not None
                else []
            )
            if not rodadas_copa:
                st.info("Nenhum jogo da Copa do Brasil disputado ainda.")
            else:
                rodada_copa = st.selectbox(
                    "Selecione a rodada",
                    rodadas_copa,
                    index=len(rodadas_copa) - 1,
                    key="resultados_rodada_copa",
                    format_func=lambda r: f"Rodada {r}",
                )
                partidas_copa = (
                    copa.resultados.get(rodada_copa, []) if copa is not None else []
                )
                fase_nome = partidas_copa[0].fase if partidas_copa else ""
                secao(f"Rodada {rodada_copa}", f"🏆 Copa do Brasil · {fase_nome}")
                for partida in partidas_copa:
                    destaque = time is not None and time.nome in (
                        partida.time_casa,
                        partida.time_fora,
                    )
                    st.markdown(
                        f"""
                    <div class="res" style="{"border-color:var(--brand);background:#F2FBF5" if destaque else ""}">
                        <span style="{"font-weight:800" if destaque else ""}">🏆 {partida.time_casa}
                        <b>{partida.gols_casa} x {partida.gols_fora}</b> {partida.time_fora}</span>
                        <span style="margin-left:auto;color:var(--ink-3);font-size:.78rem">
                            {partida.grupo or "jogo único"}
                        </span>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                    if destaque and partida.eventos:
                        with st.expander("📋 Ver eventos da partida"):
                            _linha_do_tempo(partida.eventos)
        indice_extra += 1

    if tem_regionais:
        piramide_reg = get_piramide()
        torneios = get_regionais()
        with abas[indice_extra]:
            chave_reg = st.selectbox(
                "Torneio",
                [t.chave for t in torneios],
                format_func=lambda k: next(
                    (t.nome for t in torneios if t.chave == k), str(k)
                ),
                key="resultados_regional",
            )
            torneio = (
                piramide_reg.torneio(chave_reg) if piramide_reg is not None else None
            )
            if torneio is None:
                st.info("Torneio indisponível nesta temporada.")
            else:
                rodadas_reg = [
                    r for r in sorted(torneio.resultados) if torneio.resultados[r]
                ]
                if not rodadas_reg:
                    st.info(f"{torneio.nome}: nenhum jogo disputado ainda.")
                else:
                    rodada_reg = st.selectbox(
                        "Selecione a rodada",
                        rodadas_reg,
                        index=len(rodadas_reg) - 1,
                        key="resultados_regional_rodada",
                        format_func=lambda r: f"Rodada {r}",
                    )
                    partidas_reg = torneio.resultados.get(rodada_reg, [])
                    fase_reg = partidas_reg[0].fase if partidas_reg else ""
                    secao(f"Rodada {rodada_reg}", f"{torneio.nome} · {fase_reg}")
                    for partida in partidas_reg:
                        destaque = time is not None and time.nome in (
                            partida.time_casa,
                            partida.time_fora,
                        )
                        st.markdown(
                            f"""
                        <div class="res" style="{"border-color:var(--brand);background:#F2FBF5" if destaque else ""}">
                            <span style="{"font-weight:800" if destaque else ""}">🌎 {partida.time_casa}
                            <b>{partida.gols_casa} x {partida.gols_fora}</b> {partida.time_fora}</span>
                            <span style="margin-left:auto;color:var(--ink-3);font-size:.78rem">
                                {partida.grupo or partida.fase}
                            </span>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
