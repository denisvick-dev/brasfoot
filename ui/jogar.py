"""
Tela de partida: pré-jogo, jogo ao vivo e fim de temporada.
"""

import random
import time as _time

import streamlit as st

from game.banco_dados import (
    NOMES_DIVISAO,
)
from game.campeonato import League
from game.escudos import imagem as escudo_img
from game.modelos import Partida, Time
from ui.ao_vivo import (
    VELOCIDADE_PADRAO,
    VELOCIDADES,
    html_ao_vivo,
    minuto_final,
    passos,
    relogio,
)
from ui.apoio import (
    _rotulo_competicao,
    divisao_do_jogador,
    divisoes_da_temporada,
    get_copa,
    get_meu_time,
    get_piramide,
    posicao_na_tabela,
    rodada_de,
    secao,
    sigla_de,
    tabela_classificacao,
    time_por_nome,
    total_rodadas_de,
)


def tela_jogar():
    time = get_meu_time()
    league = st.session_state.league

    if time is None:
        st.error("Nenhum time selecionado. Selecione um time para continuar.")
        return

    piramide = get_piramide()
    proximo: tuple[str, int, str, str] | None = None
    if piramide is not None:
        proximo = piramide.proximo_jogo(time.nome)
        rodada_global = piramide.rodada_global + 1
        total_global = piramide.total_rodadas_global
        divisao_encerrada = league.campeonato_encerrado or (
            league.rodada_atual >= len(league.calendario)
        )
        if proximo is None and divisao_encerrada:
            _tela_fim_temporada(time, league)
            return
    else:
        if league.campeonato_encerrado or league.rodada_atual >= len(league.calendario):
            _tela_fim_temporada(time, league)
            return
        rodada_global = league.rodada_atual + 1
        total_global = league.total_rodadas
        for casa, fora in league.calendario[league.rodada_atual]:
            if time.nome in (casa, fora):
                proximo = (
                    NOMES_DIVISAO.get(time.divisao, "Campeonato"),
                    league.rodada_atual + 1,
                    casa,
                    fora,
                )
                break

    adversario = None
    em_casa = False
    competicao = ""
    if proximo is not None:
        competicao, _, casa, fora = proximo
        adversario = time_por_nome(fora if casa == time.nome else casa)
        em_casa = casa == time.nome

    sub = (
        f"{competicao} · {'em casa contra' if em_casa else 'fora de casa contra'} "
        f"{adversario.nome}"
        if adversario is not None
        else "Sem jogo nesta rodada — folga"
    )
    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <div class="hero-kicker">Temporada {league.temporada} · rodada {rodada_global} de {total_global}</div>
        <h1 style="font-size:1.9rem">{escudo_img(time.sigla, time.escudo_emoji)} {time.nome}</h1>
        <p>{sub}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if len(time.titulares) != 11:
        st.warning(
            f"⚠️ Você tem {len(time.titulares)} titulares! Precisa de 11. "
            f"Vá em 📋 Tática para ajustar."
        )

    if adversario is not None:
        secao("Pré-jogo", competicao)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown(
                _cartao_time(time, "🏠 Casa" if em_casa else "✈️ Fora"),
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                """
            <div style="display:flex;align-items:center;justify-content:center;
                        height:100%;min-height:140px">
                <div style="font-family:var(--font-display);font-weight:800;
                            font-size:1.4rem;color:var(--ink-3)">VS</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                _cartao_time(adversario, "✈️ Fora" if em_casa else "🏠 Casa"),
                unsafe_allow_html=True,
            )
    else:
        st.info(
            "🌴 Sem jogo nesta rodada. Você pode adiantar a rodada — as outras "
            "competições continuam rolando."
        )

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    col_vel, col_btn = st.columns([1.3, 1])
    with col_vel:
        velocidade = st.radio(
            "⏱️ Relógio da rodada",
            list(VELOCIDADES),
            index=list(VELOCIDADES).index(VELOCIDADE_PADRAO),
            horizontal=True,
            key="velocidade_rodada",
            help="Quanto tempo o relógio leva para ir de 0' a 90'. "
            "Cada simulação sorteia resultados novos.",
        )
    with col_btn:
        st.markdown("<div style='height:1.55rem'></div>", unsafe_allow_html=True)
        simular = st.button(
            "⚽ SIMULAR RODADA", type="primary", use_container_width=True
        )
    if simular:
        # Cada rodada é um sorteio novo: o número fica na tela e, se precisar,
        # reproduz exatamente esta rodada (foi a semente usada pelo motor).
        sorteio = random.getrandbits(24)
        random.seed(sorteio)
        st.session_state.sorteio_rodada = sorteio

        barra = st.progress(0.0, text="⚽ Preparando a rodada...")

        def _progresso(fracao: float, rotulo: str) -> None:
            barra.progress(min(1.0, fracao), text=f"⚽ Simulando {rotulo}...")

        if piramide is not None:
            jogos = piramide.simular_rodada(time.nome, progresso=_progresso)
            minha_divisao = divisao_do_jogador()
            st.session_state.ultimo_resultado = jogos.get(minha_divisao, [])
            st.session_state.rodadas_simuladas = {
                d: rodada_de(d) for d in jogos if d in piramide.divisoes
            }
            st.session_state.ultima_rodada = [
                (_rotulo_competicao(chave), partida)
                for chave, partidas in jogos.items()
                for partida in partidas
                if time.nome in (partida.time_casa, partida.time_fora)
            ]
            st.session_state.resultados_copa = jogos.get("COPA", [])
            st.session_state.placares_rodada = {
                _rotulo_competicao(chave): partidas
                for chave, partidas in jogos.items()
                if partidas
            }
        else:
            jogos_div = league.simular_rodada(time.nome, progresso=_progresso)
            minha_divisao = divisao_do_jogador()
            st.session_state.ultimo_resultado = jogos_div
            st.session_state.rodadas_simuladas = {minha_divisao: league.rodada_atual}
            st.session_state.ultima_rodada = [
                (NOMES_DIVISAO.get(minha_divisao, "Campeonato"), partida)
                for partida in jogos_div
                if time.nome in (partida.time_casa, partida.time_fora)
            ]
            st.session_state.placares_rodada = {
                NOMES_DIVISAO.get(minha_divisao, "Campeonato"): jogos_div
            }

        st.session_state.placares_rodada_numero = rodada_global
        barra.empty()
        # A rodada já está calculada; agora o relógio passa de 0' a 90' mostrando
        # os gols acontecendo (ou seja: "tempo rodando com barra de progresso").
        _rodar_relogio(
            st.session_state.placares_rodada or {},
            time,
            rodada_global,
            velocidade,
        )
        st.rerun()

    meus_jogos = st.session_state.get("ultima_rodada") or []
    if meus_jogos:
        secao("Seus jogos da rodada", f"Rodada {rodada_global - 1}")
        for rotulo, partida in meus_jogos:
            _card_resultado(partida, time, rotulo)

    placares = st.session_state.get("placares_rodada") or {}
    numero = st.session_state.get("placares_rodada_numero")
    if placares:
        total_jogos = sum(len(partidas) for partidas in placares.values())
        secao(
            "Placares da rodada",
            f"Rodada {numero} · {total_jogos} jogos"
            if numero
            else f"{total_jogos} jogos",
        )
        st.markdown(_html_placares(placares), unsafe_allow_html=True)
        sorteio = st.session_state.get("sorteio_rodada")
        if sorteio:
            st.caption(
                f"🎲 Sorteio #{sorteio:06x} — cada simulação sorteia resultados "
                "novos; o número identifica este sorteio."
            )

    outras = [d for d in divisoes_da_temporada() if d != divisao_do_jogador()]
    pendentes = [d for d in outras if rodada_de(d) > 0]
    if pendentes:
        resumo_divisoes = " · ".join(
            f"**{NOMES_DIVISAO.get(d, d)}** rodada {rodada_de(d)}/{total_rodadas_de(d)}"
            for d in pendentes
        )
        st.caption(f"🌎 Também na temporada: {resumo_divisoes}")


def _placar_linha(partida: Partida) -> str:
    """Uma linha de placar: mandante, gols e visitante, com escudos."""
    casa = escudo_img(sigla_de(partida.time_casa))
    fora = escudo_img(sigla_de(partida.time_fora))
    return (
        "<div class='placar-linha'>"
        f"<span class='pc-time'>{casa} {partida.time_casa}</span>"
        f"<span class='pc-score'>{partida.gols_casa}<i>x</i>{partida.gols_fora}</span>"
        f"<span class='pc-time right'>{partida.time_fora} {fora}</span>"
        "</div>"
    )


def _html_placares(placares: dict[str, list[Partida]]) -> str:
    """Quadro com todos os placares da rodada, separados por competição."""
    blocos = []
    for rotulo, partidas in placares.items():
        if not partidas:
            continue
        linhas = "".join(_placar_linha(partida) for partida in partidas)
        blocos.append(
            f"<div class='placar-bloco'><h4>{rotulo}"
            f"<span>{len(partidas)} jogos</span></h4>{linhas}</div>"
        )
    if not blocos:
        return ""
    return f"<div class='placares'>{''.join(blocos)}</div>"


def _card_resultado(partida: Partida, time: Time, rotulo: str) -> None:
    """Cartão de resultado de um jogo do clube do jogador."""
    meus = partida.gols_casa if partida.time_casa == time.nome else partida.gols_fora
    deles = partida.gols_fora if partida.time_casa == time.nome else partida.gols_casa
    cor = (
        "linear-gradient(135deg,#16A34A,#065F46)"
        if meus > deles
        else "linear-gradient(135deg,#DC2626,#7F1D1D)"
        if meus < deles
        else "linear-gradient(135deg,#D97706,#92400E)"
    )
    st.markdown(
        f"""
    <div class="score" style="--sc:{cor}">
        <div class="score-comp">{rotulo}{f" · {partida.fase}" if partida.fase else ""}</div>
        <div class="teams">{escudo_img(sigla_de(partida.time_casa))} {partida.time_casa}
            <span class="goals">{partida.gols_casa} x {partida.gols_fora}</span>
            {partida.time_fora} {escudo_img(sigla_de(partida.time_fora))}</div>
        <div class="pub">Público: {partida.publico:,}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if partida.eventos:
        with st.expander("⚽ Eventos da partida"):
            _linha_do_tempo(partida.eventos)


def _cartao_time(time: Time, local: str) -> str:
    return f"""
    <div class="stat" style="--accent:{time.cor_primaria}">
        <div style="display:flex;align-items:center;gap:.6rem">
            <div class="club-crest" style="--c1:{time.cor_primaria};--c2:{time.cor_secundaria}">
                {escudo_img(time.sigla, time.escudo_emoji, "escudo-crest")}
            </div>
            <div>
                <div style="font-family:var(--font-display);font-weight:800;font-size:1.05rem">
                    {time.nome}
                </div>
                <div class="club-meta">{local}</div>
            </div>
        </div>
        <div style="margin-top:.7rem">
            <div class="kv"><span>Overall</span><b>⭐ {time.overall_time}</b></div>
            <div class="kv"><span>Ataque</span><b>⚔️ {time.forca_ataque}</b></div>
            <div class="kv"><span>Defesa</span><b>🛡️ {time.forca_defesa}</b></div>
            <div class="kv"><span>Moral</span><b>🎭 {time.moral_time}%</b></div>
        </div>
    </div>
    """


def _linha_do_tempo(eventos: list[str]):
    itens = []
    for ev in eventos:
        if "GOOOL" in ev:
            classe = "gol"
        elif "vermelho" in ev.lower():
            classe = "vermelho"
        elif "amarelo" in ev.lower():
            classe = "amarelo"
        elif "defesa" in ev.lower():
            classe = "defesa"
        else:
            classe = ""
        itens.append(f'<div class="ev {classe}">{ev}</div>')

    st.markdown('<div class="tl">' + "".join(itens) + "</div>", unsafe_allow_html=True)


def _tela_fim_temporada(time: Time, league: League):
    piramide = get_piramide()
    minha = divisao_do_jogador()
    campeao = (
        piramide.league(minha).campeao
        if piramide is not None
        else league.classificacao[0]
    )
    campeao = campeao or league.classificacao[0]
    pos = posicao_na_tabela(league, time.nome)
    outras_pendentes = (
        [d for d in piramide.ordem if not piramide.encerrada_em(d)]
        if piramide is not None
        else []
    )
    copa = get_copa()
    copa_pendente = copa is not None and not copa.encerrada
    supercopa_pendente = (
        piramide is not None
        and piramide.fases_finais_encerradas
        and piramide.supercopa is None
    )

    st.markdown(
        f"""
    <div class="hero" style="background:linear-gradient(120deg,#92400E 0%,#F5B301 55%,#FDE68A 100%);
                             color:#1F1300">
        <h1 style="color:#1F1300">🏆 {NOMES_DIVISAO.get(minha, "CAMPEONATO")} ENCERRADA</h1>
        <p style="color:rgba(31,19,0,.85)">
            Campeão: <b>{escudo_img(campeao.sigla, campeao.escudo_emoji)} {campeao.nome}</b> com {campeao.pontos} pontos<br>
            Sua posição: <b>{pos}º</b> com {time.pontos} pontos
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if piramide is not None and campeao is not None and campeao.nome == time.nome:
        st.balloons()
        st.success("🎉🏆 PARABÉNS! VOCÊ É O CAMPEÃO! 🏆🎉")
    else:
        temporada_div = piramide.league(minha) if piramide is not None else None
        if temporada_div is not None and any(
            t.nome == time.nome for t in temporada_div.promovidos
        ):
            st.success(f"✅ Acesso garantido! ({pos}º na 1ª fase)")
        elif temporada_div is not None and any(
            t.nome == time.nome for t in temporada_div.rebaixados
        ):
            st.error(f"😢 Rebaixado! ({pos}º na 1ª fase)")
        elif pos <= 6 and minha == "A":
            st.info(f"Classificado para a Sul-Americana ({pos}º lugar)")
        elif pos == 1 and temporada_div is not None:
            st.success(f"✅ Melhor campanha da 1ª fase! ({pos}º lugar)")

    secao("Regulamento", NOMES_DIVISAO.get(minha, minha))
    for regra in piramide.regulamento(minha) if piramide is not None else []:
        st.markdown(f"- {regra}")

    secao("Classificação final", NOMES_DIVISAO.get(minha, minha))
    st.markdown(tabela_classificacao(minha, time), unsafe_allow_html=True)

    if piramide is None:
        if st.button("🔄 Nova Temporada", type="primary"):
            league.temporada += 1
            league.rodada_atual = 0
            league.campeonato_encerrado = False
            league.resultados = {}
            league.noticias = []
            league._gerar_calendario()
            st.session_state.ultimo_resultado = None
            for t in league.times:
                t.resetar_campeonato()
                t.auto_escalar()
            st.session_state.market.atualizar_mercado()
            st.rerun()
        return

    # ---- outras divisões (e a copa) ainda em andamento
    if outras_pendentes or copa_pendente or supercopa_pendente:
        nomes = ", ".join(NOMES_DIVISAO.get(d, d) for d in outras_pendentes)
        if copa_pendente:
            nomes = f"{nomes}, Copa do Brasil" if nomes else "Copa do Brasil"
        if supercopa_pendente:
            nomes = f"{nomes}, Supercopa do Brasil" if nomes else "Supercopa do Brasil"
        st.info(
            f"⏳ {nomes} ainda em andamento. Feche a temporada para ver o "
            "resumo completo."
        )
        if st.button("⏭️ Simular o restante da temporada", type="primary"):
            with st.spinner("Simulando o restante da temporada..."):
                piramide.simular_restante()
            st.rerun()

    # ---- resumo da temporada inteira
    secao("Temporada completa", f"{len(piramide.ordem)} divisões")
    colunas = st.columns(min(4, len(piramide.ordem)))
    for i, divisao in enumerate(piramide.ordem):
        temporada_div = piramide.league(divisao)
        tabela = temporada_div.tabela(temporada_div.fases[0])
        if not tabela:
            continue
        with colunas[i % len(colunas)]:
            encerrada = piramide.encerrada_em(divisao)
            destaque = (
                temporada_div.campeao if encerrada else tabela[0]["time"]
            ) or tabela[0]["time"]
            st.markdown(
                f'<div class="stat" style="--accent:#F5B301">'
                f'<div class="lbl">{NOMES_DIVISAO.get(divisao, divisao)}</div>'
                f'<div class="val" style="font-size:1.05rem;font-family:var(--font-ui)!important">'
                f"{escudo_img(destaque.sigla, destaque.escudo_emoji)} {destaque.nome}</div>"
                f'<div class="club-meta">{"campeão" if encerrada else "líder"} · '
                f"{tabela[0]['pts']} pts · rodada {piramide.rodada(divisao)}/"
                f"{piramide.total_rodadas(divisao)}</div></div>",
                unsafe_allow_html=True,
            )

    regionais = piramide.regionais
    if regionais:
        secao("Torneios regionais", "Início da temporada")
        colunas_reg = st.columns(min(3, len(regionais)))
        for i, torneio in enumerate(regionais):
            with colunas_reg[i % len(colunas_reg)]:
                campeao_reg = (
                    torneio.campeao.nome if torneio.campeao is not None else "—"
                )
                st.markdown(
                    f'<div class="stat" style="--accent:#0EA5E9">'
                    f'<div class="lbl">{torneio.nome}</div>'
                    f'<div class="val" style="font-size:1rem;'
                    f'font-family:var(--font-ui)!important">{campeao_reg}</div>'
                    f'<div class="club-meta">campeão</div></div>',
                    unsafe_allow_html=True,
                )

    if copa is not None:
        secao("Copa do Brasil", "Mata-mata em ida e volta")
        if copa.campeao is not None:
            st.success(f"🏆 Campeão da Copa do Brasil: **{copa.campeao.nome}**")
        else:
            fase = copa.fases[-1] if copa.fases else None
            st.info(
                f"⏳ Em andamento · {fase.nome if fase is not None else 'sem jogos'}"
            )

    if piramide.supercopa is not None:
        jogo_super = piramide.supercopa
        secao("Supercopa do Brasil", "Campeão brasileiro x campeão da copa")
        st.markdown(
            f"""
        <div class="score" style="--sc:linear-gradient(135deg,#0F172A,#334155)">
            <div class="score-comp">Jogo único</div>
            <div class="teams">{escudo_img(sigla_de(jogo_super.time_casa))} {jogo_super.time_casa}
                <span class="goals">{jogo_super.gols_casa} x {jogo_super.gols_fora}</span>
                {jogo_super.time_fora} {escudo_img(sigla_de(jogo_super.time_fora))}</div>
            <div class="pub">Público: {jogo_super.publico:,}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    elif piramide.fases_finais_encerradas:
        st.info("⏳ Supercopa do Brasil a ser disputada — simule a próxima rodada.")

    if piramide.encerrada:
        movimentos = piramide.acesso_descenso()
        secao("Acesso e descenso", "Prévia da próxima temporada")
        for divisao in piramide.ordem:
            mov = movimentos.get(divisao, {})
            sobe = ", ".join(t.nome for t in mov.get("promovidos", [])) or "—"
            cai = ", ".join(t.nome for t in mov.get("rebaixados", [])) or "—"
            st.markdown(
                f'<div class="res" style="flex-wrap:wrap">'
                f"<b>{NOMES_DIVISAO.get(divisao, divisao)}</b>"
                f'<span style="margin-left:auto">⬆️ {sobe}</span>'
                f'<span style="color:var(--ink-3)">⬇️ {cai}</span></div>',
                unsafe_allow_html=True,
            )

        if st.button("🔄 Nova Temporada", type="primary"):
            with st.spinner("Aplicando acesso e descenso..."):
                piramide.nova_temporada()
                st.session_state.league = piramide.league_de(time.nome) or league
                if st.session_state.market is not None:
                    st.session_state.market.atualizar_mercado()
            st.session_state.ultimo_resultado = None
            st.session_state.pagina = "painel"
            st.rerun()
    else:
        st.caption(
            "Assim que todas as divisões terminarem, o acesso e o descenso "
            "são aplicados e você pode começar a temporada seguinte."
        )


def _rodar_relogio(
    placares: dict[str, list[Partida]],
    time: Time,
    rodada: int,
    velocidade: str,
) -> None:
    """Passa o relógio de 0' ao último minuto, com barra de progresso.

    Os jogos já foram simulados (é instantâneo); aqui só *revelamos* o placar de
    cada partida conforme o minuto, do jeito que o Brasfoot faz na tela de jogo.
    """
    segundos = VELOCIDADES.get(velocidade, VELOCIDADES[VELOCIDADE_PADRAO])
    final = minuto_final(placares)
    if not placares or segundos <= 0 or final <= 0:
        return

    marcos = passos(final)
    atraso = segundos / max(1, len(marcos))
    sorteio = st.session_state.get("sorteio_rodada")

    barra = st.progress(0.0, text=f"⏱️ {relogio(0)} · rodada {rodada}")
    painel = st.empty()
    for minuto in marcos:
        barra.progress(
            min(1.0, minuto / final),
            text=f"⏱️ {relogio(minuto)} · rodada {rodada}",
        )
        painel.markdown(
            html_ao_vivo(
                placares,
                minuto,
                meu_time=time.nome,
                rodada=rodada,
                sorteio=sorteio,
                final=final,
            ),
            unsafe_allow_html=True,
        )
        _time.sleep(atraso)

    barra.progress(1.0, text="✅ Rodada encerrada — confira os placares abaixo")
    painel.markdown(
        html_ao_vivo(
            placares,
            final,
            meu_time=time.nome,
            rodada=rodada,
            sorteio=sorteio,
            final=final,
        ),
        unsafe_allow_html=True,
    )
