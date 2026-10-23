"""
Criador de clubes, jogadores e competições personalizadas.
"""

import streamlit as st

from game.banco_dados import (
    DIVISOES,
    NOMES_DIVISAO,
    clubes_por_divisao,
)
from game.competicoes import (
    DISTRIBUICOES,
    FORMATOS,
    Campeonato,
    campeonatos_salvos,
    excluir_campeonato,
    limites,
)
from game.criador import (
    PERFIS,
    POSICOES,
    clube_salvo,
    clubes_salvos,
    criar_clube,
    criar_jogador,
    excluir_clube,
    excluir_jogador,
    gerar_jogador_aleatorio,
    jogador_salvo,
    jogadores_salvos,
    pool_de_times,
    resolver_times,
    salvar_clube,
    salvar_jogador,
)
from game.escudos import imagem as escudo_img
from game.modelos import Time
from ui.apoio import formatar_dinheiro, get_meu_time, get_piramide, secao


def tela_criador():
    st.markdown(
        """
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">🛠️ Criador</h1>
        <p>Monte seus próprios clubes, jogadores e campeonatos — tudo salvo em JSON.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab_clube, tab_jog, tab_camp, tab_dados = st.tabs(
        ["🏟️ Clube", "👤 Jogador", "🏆 Campeonato", "📁 Meus dados"]
    )

    # ---------------- CLUBE ----------------
    with tab_clube:
        with st.form("form_clube"):
            c1, c2, c3 = st.columns([3, 1, 1])
            nome = c1.text_input("Nome*", placeholder="Aurora Futebol Clube")
            sigla = c2.text_input("Sigla*", placeholder="AUR", max_chars=4)
            escudo = c3.text_input("Escudo", value="⚽")

            c4, c5, c6 = st.columns([3, 1, 1])
            cidade = c4.text_input("Cidade", placeholder="Curitiba")
            estado = c5.text_input("UF", placeholder="PR", max_chars=2)
            fundacao = c6.number_input("Fundação", 1850, 2026, 2000)

            c7, c8 = st.columns(2)
            cor1 = c7.color_picker("Cor primária", "#16A34A")
            cor2 = c8.color_picker("Cor secundária", "#FFFFFF")

            c9, c10 = st.columns(2)
            estadio = c9.text_input("Estádio", placeholder="Arena Aurora")
            capacidade = c10.number_input(
                "Capacidade", 1_000, 120_000, 30_000, step=1_000
            )

            faixa = st.slider("Força do elenco (mínimo → máximo)", 30, 95, (50, 72))

            c11, c12, c13 = st.columns(3)
            financas = c11.number_input(
                "Finanças (R$)", 0, 500_000_000, 10_000_000, step=1_000_000
            )
            torcida = c12.slider("Torcida", 1, 100, 40)
            reputacao = c13.slider("Reputação", 1, 100, 50)

            c14, c15, c16 = st.columns(3)
            tamanho = c14.slider("Jogadores no elenco", 11, 30, 22)
            divisao = c15.selectbox(
                "Divisão", list(DIVISOES), format_func=lambda d: NOMES_DIVISAO[d]
            )
            formacao = c16.selectbox(
                "Formação", ["4-4-2", "4-3-3", "3-5-2", "4-5-1", "5-3-2"]
            )

            enviar = st.form_submit_button(
                "🏗️ Criar clube", type="primary", use_container_width=True
            )

        if enviar:
            try:
                st.session_state.clube_novo = criar_clube(
                    nome=nome,
                    sigla=sigla,
                    cidade=cidade,
                    estado=estado,
                    escudo_emoji=escudo,
                    cor_primaria=cor1,
                    cor_secundaria=cor2,
                    forca_min=faixa[0],
                    forca_max=faixa[1],
                    financas=financas,
                    torcida=torcida,
                    reputacao=reputacao,
                    estadio=estadio,
                    capacidade=capacidade,
                    fundacao=fundacao,
                    divisao=divisao,
                    tamanho_elenco=tamanho,
                    formacao=formacao,
                )
            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:  # noqa: BLE001
                st.error(f"❌ Não foi possível criar o clube: {e}")

        clube = st.session_state.get("clube_novo")
        if clube:
            secao("Clube criado", "Prévia")
            col_prev, col_acoes = st.columns([2, 1])
            with col_prev:
                st.markdown(
                    f"""
                <div class="club-card">
                    <div class="stripe" style="--c1:{clube.cor_primaria}"></div>
                    <div class="body">
                        <div class="club-crest" style="--c1:{clube.cor_primaria};--c2:{clube.cor_secundaria}">
                            {escudo_img(clube.sigla, clube.escudo_emoji, "escudo-crest")}
                        </div>
                        <div class="club-name">{clube.nome} ({clube.sigla})</div>
                        <div class="club-meta">📍 {clube.cidade}/{clube.estado or "—"} ·
                            fundado em {clube.fundacao}</div>
                        <div class="kv"><span>Estádio</span><b>{clube.estadio}</b></div>
                        <div class="kv"><span>Capacidade</span><b>{clube.capacidade:,}</b></div>
                        <div class="kv"><span>Divisão</span><b>{clube.divisao}</b></div>
                        <div class="kv"><span>Overall</span><b>⭐ {clube.overall_time}</b></div>
                        <div class="kv"><span>Elenco</span><b>{len(clube.jogadores)} jogadores</b></div>
                        <div class="kv"><span>Caixa</span><b>{formatar_dinheiro(clube.financas)}</b></div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            with col_acoes:
                st.metric("⭐ Overall", clube.overall_time)
                st.metric("⚔️ Ataque", clube.forca_ataque)
                st.metric("🛡️ Defesa", clube.forca_defesa)
                if st.button(
                    "💾 Salvar clube", use_container_width=True, type="primary"
                ):
                    slug = salvar_clube(clube)
                    st.success(f"✅ {clube.nome} salvo como `{slug}`")
                if st.button("🎮 Usar no próximo jogo", use_container_width=True):
                    st.session_state.setdefault("clubes_custom", [])
                    if clube.nome not in [
                        t.nome for t in st.session_state.clubes_custom
                    ]:
                        st.session_state.clubes_custom.append(clube)
                        st.success(f"✅ {clube.nome} entra no próximo jogo!")
                    else:
                        st.info("Esse clube já está na lista.")
                if st.button("🗑️ Descartar", use_container_width=True):
                    st.session_state.pop("clube_novo", None)
                    st.rerun()

    # ---------------- JOGADOR ----------------
    with tab_jog:
        with st.form("form_jogador"):
            c1, c2, c3 = st.columns([3, 1, 1])
            nome_j = c1.text_input(
                "Nome", value="", placeholder="Deixe vazio para sortear"
            )
            posicao = c2.selectbox("Posição", POSICOES)
            idade = c3.number_input("Idade", 16, 45, 24)

            st.markdown(
                '<div class="club-meta">Atributos (1 a 99)</div>',
                unsafe_allow_html=True,
            )
            a1, a2 = st.columns(2)
            hab = a1.slider("🎯 Habilidade", 1, 99, 60)
            vel = a2.slider("⚡ Velocidade", 1, 99, 60)
            a3, a4 = st.columns(2)
            fin = a3.slider("🥅 Finalização", 1, 99, 60)
            pas = a4.slider("🎯 Passe", 1, 99, 60)
            a5, a6 = st.columns(2)
            defe = a5.slider("🛡️ Defesa", 1, 99, 60)
            fis = a6.slider("💪 Físico", 1, 99, 60)

            col_perfil, col_btn = st.columns([3, 1])
            with col_perfil:
                perfil = st.selectbox(
                    "Preencher com um perfil pronto (use o botão ao lado)",
                    list(PERFIS),
                )
            sortear = col_btn.form_submit_button("🎲 Sortear")

            enviar_j = st.form_submit_button(
                "👤 Criar jogador", type="primary", use_container_width=True
            )

        if sortear:
            st.session_state.jogador_novo = gerar_jogador_aleatorio(posicao, perfil)

        if enviar_j:
            try:
                st.session_state.jogador_novo = criar_jogador(
                    nome_j or "", posicao, idade, hab, vel, fin, pas, defe, fis
                )
            except ValueError as e:
                st.error(f"❌ {e}")

        jog = st.session_state.get("jogador_novo")
        if jog:
            secao("Jogador criado", "Prévia")
            c_esq, c_dir = st.columns([2, 1])
            with c_esq:
                st.markdown(
                    f"""
                <div class="stat" style="--accent:var(--brand)">
                    <div class="lbl">{jog.posicao_emoji} {jog.posicao} · {jog.idade} anos</div>
                    <div class="val">{jog.nome}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
                cols = st.columns(6)
                for col, (rotulo, valor) in zip(
                    cols,
                    [
                        ("Habilidade", jog.habilidade),
                        ("Velocidade", jog.velocidade),
                        ("Finalização", jog.finalizacao),
                        ("Passe", jog.passe),
                        ("Defesa", jog.defesa),
                        ("Físico", jog.fisico),
                    ],
                    strict=False,
                ):
                    col.metric(rotulo, valor)
            with c_dir:
                st.metric("⭐ Overall", jog.overall)
                st.metric("💵 Salário", formatar_dinheiro(jog.salario))
                st.metric("💎 Valor", formatar_dinheiro(jog.valor_mercado))
                if st.button(
                    "💾 Salvar jogador", use_container_width=True, type="primary"
                ):
                    slug = salvar_jogador(jog)
                    st.success(f"✅ {jog.nome} salvo como `{slug}`")
                meu_time = get_meu_time()
                if meu_time and st.button(
                    f"➕ Adicionar ao {meu_time.sigla}", use_container_width=True
                ):
                    if len(meu_time.jogadores) >= 30:
                        st.error("❌ Elenco lotado (máximo 30)!")
                    else:
                        meu_time.jogadores.append(jog)
                        meu_time.auto_escalar()
                        st.success(f"✅ {jog.nome} entrou no {meu_time.nome}!")
                        st.session_state.pop("jogador_novo", None)
                        st.rerun()

    # ---------------- CAMPEONATO ----------------
    with tab_camp:
        banco, custom = pool_de_times()
        opcoes = custom + banco

        nome_c = st.text_input("Nome do campeonato*", placeholder="Copa Aurora 2026")
        formato = st.radio(
            "Formato",
            list(FORMATOS),
            format_func=lambda k: FORMATOS[k],
            horizontal=True,
        )

        st.markdown(
            '<div class="club-meta">Seleção rápida:</div>', unsafe_allow_html=True
        )
        por_divisao = {d: [c.nome for c in clubes_por_divisao(d)] for d in DIVISOES}
        atalhos = st.columns(4)
        if atalhos[0].button(f"Série A ({len(por_divisao['A'])})"):
            st.session_state.sel_times = por_divisao["A"]
        if atalhos[1].button(f"Série B ({len(por_divisao['B'])})"):
            st.session_state.sel_times = por_divisao["B"]
        if atalhos[2].button(f"Série C ({len(por_divisao['C'])})"):
            st.session_state.sel_times = por_divisao["C"]
        if atalhos[3].button(f"Série D ({len(por_divisao['D'])})"):
            st.session_state.sel_times = por_divisao["D"]

        atalhos2 = st.columns(3)
        if atalhos2[0].button(f"Todo o banco ({len(banco)})"):
            st.session_state.sel_times = list(banco)
        if atalhos2[1].button("Meus clubes"):
            st.session_state.sel_times = list(custom)
        if atalhos2[2].button("Limpar"):
            st.session_state.sel_times = []

        # a seleção vive na sessão (os atalhos acima escrevem nela)
        if "sel_times" not in st.session_state:
            st.session_state.sel_times = list(custom[:1]) + banco[:7]
        st.session_state.sel_times = [
            n for n in st.session_state.sel_times if n in opcoes
        ]

        selecao = st.multiselect("Times participantes*", opcoes, key="sel_times")
        n_times = len(selecao)
        lim = limites(max(n_times, 2))

        # ---------------- regras gerais ----------------
        secao("Regras gerais", "Opções")
        r1, r2, r3 = st.columns(3)
        with r1:
            ida_e_volta = st.checkbox(
                "Ida e volta na fase de grupos",
                value=True,
                help="Desmarcado, cada time enfrenta o outro uma única vez.",
            )
        with r2:
            distribuicao = st.selectbox(
                "Distribuição dos times",
                list(DISTRIBUICOES),
                format_func=lambda k: DISTRIBUICOES[k],
                help="Por força, os melhores viram cabeças de chave e ficam "
                "separados (potes).",
            )
        with r3:
            temporada_c = st.number_input("Temporada", 2020, 2100, 2026)

        s1, s2 = st.columns([1, 2])
        with s1:
            usar_semente = st.checkbox(
                "Sorteio reproduzível",
                value=False,
                help="Com a mesma semente, o sorteio sai sempre igual.",
            )
        with s2:
            semente = st.number_input(
                "Semente",
                1,
                9999,
                42,
                disabled=not usar_semente,
            )

        # ---- competições prontas ----
        secao("Competições prontas", "Atalho")
        col_p1, col_p2 = st.columns([1, 3])
        with col_p1:
            criar_copa = st.button(
                "🏆 Copa do Brasil", type="primary", use_container_width=True
            )
        with col_p2:
            st.caption(
                "Competição avulsa, com 128 clubes em mata-mata de ida e volta. "
                "A Copa do Brasil da carreira já vem no calendário da temporada."
            )
        if criar_copa:
            _criar_copa_do_brasil(
                banco, custom, int(temporada_c), usar_semente, int(semente)
            )
            if st.session_state.get("erro_copa"):
                st.error(f"❌ Copa do Brasil: {st.session_state.pop('erro_copa')}")
            else:
                st.session_state.pagina = "competicao"
                st.rerun()

        # ---------------- regras por formato ----------------
        promovidos = rebaixados = 0
        n_grupos, times_por_grupo = 4, 0
        classificados = 2
        ida_e_volta_mata = True
        final_unica = True
        terceiro_lugar = False

        if formato == "pontos_corridos":
            secao("Pontos corridos", "Opções")
            c1, c2 = st.columns(2)
            promovidos = c1.number_input("Promovidos", 0, 20, 4, step=1)
            rebaixados = c2.number_input("Rebaixados", 0, 20, 4, step=1)
            st.caption(
                "Tabela única: todos contra todos. Ao final, os primeiros sobem "
                "e os últimos caem."
            )
            if promovidos + rebaixados > lim["promovidos"] * 2:
                st.warning(
                    f"⚠️ Promovidos + rebaixados passa de {lim['promovidos'] * 2} "
                    "para esse número de times."
                )
        elif formato == "copa":
            secao("Mata-mata", "Opções")
            c1, c2, c3 = st.columns(3)
            ida_e_volta_mata = c1.checkbox(
                "Ida e volta nas fases", value=True, key="copa_ida_volta"
            )
            final_unica = c2.checkbox(
                "Final em jogo único", value=True, key="copa_final_unica"
            )
            terceiro_lugar = c3.checkbox(
                "Disputa de 3º lugar", value=False, key="copa_terceiro"
            )
            st.caption(
                "Chave eliminatória. Times que sobram na conta (ex.: 13) "
                "recebem folga (BYE) — com cabeças de chave, a folga fica com "
                "os melhores."
            )
        else:
            secao("Fase de grupos", "Opções")
            modo = st.radio(
                "Montar os grupos por",
                ["Número de grupos", "Times por grupo"],
                horizontal=True,
                key="modo_grupos",
            )
            g1, g2 = st.columns(2)
            if modo == "Número de grupos":
                n_grupos = g1.number_input("Número de grupos", 2, 12, 4, step=1)
            else:
                times_por_grupo = g2.number_input("Times por grupo", 2, 48, 5, step=1)
                n_grupos = 4
            classificados = g1.number_input("Classificados por grupo", 1, 8, 2, step=1)
            st.caption(
                f"Com {n_times} times cabem até {lim['grupos']} grupos "
                f"e até {lim['classificados_por_grupo']} classificados por grupo."
            )

            secao("Mata-mata", "Opções")
            m1, m2, m3 = st.columns(3)
            ida_e_volta_mata = m1.checkbox(
                "Ida e volta nas fases", value=True, key="grupos_ida_volta"
            )
            final_unica = m2.checkbox(
                "Final em jogo único", value=True, key="grupos_final_unica"
            )
            terceiro_lugar = m3.checkbox(
                "Disputa de 3º lugar", value=False, key="grupos_terceiro"
            )

        # ---------------- prévia ----------------
        previa = _previa_campeonato(
            formato=formato,
            n_times=n_times,
            n_grupos=int(n_grupos),
            times_por_grupo=int(times_por_grupo),
            classificados=int(classificados),
            ida_e_volta=ida_e_volta,
            ida_e_volta_mata=ida_e_volta_mata,
            final_unica=final_unica,
            terceiro_lugar=terceiro_lugar,
            distribuicao=distribuicao,
        )
        st.markdown(
            f'<div class="res" style="background:var(--surface-2)">📐 '
            f"<b>Prévia:</b> {previa}</div>",
            unsafe_allow_html=True,
        )

        if st.button("🏆 Criar campeonato", type="primary", use_container_width=True):
            if n_times < 2:
                st.error("❌ Selecione ao menos 2 times.")
            elif formato == "grupos_mata" and n_times < 4:
                st.error("❌ Grupos + eliminatórias precisa de ao menos 4 times.")
            else:
                with st.spinner("Montando o campeonato..."):
                    try:
                        times = resolver_times(selecao)
                        camp = Campeonato(
                            nome=nome_c or "Meu Campeonato",
                            times=times,
                            formato=formato,
                            temporada=int(temporada_c),
                            ida_e_volta=ida_e_volta,
                            ida_e_volta_mata=ida_e_volta_mata,
                            n_grupos=int(n_grupos),
                            times_por_grupo=int(times_por_grupo) or None,
                            classificados_por_grupo=int(classificados),
                            distribuicao=distribuicao,
                            terceiro_lugar=terceiro_lugar,
                            promovidos=int(promovidos),
                            rebaixados=int(rebaixados),
                            final_unica=final_unica,
                            semente=int(semente) if usar_semente else None,
                        )
                        camp.salvar()
                        st.session_state.competicao = camp
                        st.success(f"✅ {camp.nome} criado e salvo!")
                        st.session_state.pagina = "competicao"
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {e}")
                    except Exception as e:  # noqa: BLE001
                        st.error(f"❌ Não foi possível criar: {e}")

        if not st.session_state.get("competicao"):
            st.caption(
                f"Times disponíveis: {len(banco)} do banco + {len(custom)} criados por você."
            )

    # ---------------- MEUS DADOS ----------------
    with tab_dados:
        secao("Clubes salvos", f"{len(clubes_salvos())} no arquivo")
        registros = clubes_salvos()
        if not registros:
            st.caption("Nenhum clube salvo ainda.")
        for reg in registros:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**🏟️ {reg['nome']}**  \n`{reg['slug']}`")
                c2.caption(f"atualizado em {reg.get('atualizado_em', '—')[:10]}")
                if c3.button("Usar", key=f"usar_clube_{reg['slug']}"):
                    time = clube_salvo(reg["slug"])
                    if time:
                        st.session_state.setdefault("clubes_custom", [])
                        if time.nome not in [
                            t.nome for t in st.session_state.clubes_custom
                        ]:
                            st.session_state.clubes_custom.append(time)
                            st.success(f"✅ {time.nome} entra no próximo jogo!")
                        else:
                            st.info("Esse clube já está na lista.")
                if c3.button("🗑️", key=f"del_clube_{reg['slug']}"):
                    excluir_clube(reg["slug"])
                    st.rerun()

        secao("Jogadores salvos", f"{len(jogadores_salvos())} no arquivo")
        registros_j = jogadores_salvos()
        if not registros_j:
            st.caption("Nenhum jogador salvo ainda.")
        for reg in registros_j:
            with st.container(border=True):
                j = jogador_salvo(reg["slug"])
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(
                    f"**👤 {reg['nome']}** {j.posicao_emoji if j else ''} "
                    f"{f'· {j.overall} OVR' if j else ''}"
                )
                c2.markdown(
                    f"<span class='club-meta'>{reg['slug']}</span>",
                    unsafe_allow_html=True,
                )
                meu_time = get_meu_time()
                if (
                    j is not None
                    and meu_time
                    and c3.button("Contratar", key=f"usar_jog_{reg['slug']}")
                ):
                    if len(meu_time.jogadores) >= 30:
                        st.error("❌ Elenco lotado!")
                    else:
                        meu_time.jogadores.append(j)
                        meu_time.auto_escalar()
                        st.success(f"✅ {j.nome} contratado!")
                        st.rerun()
                if c3.button("🗑️", key=f"del_jog_{reg['slug']}"):
                    excluir_jogador(reg["slug"])
                    st.rerun()

        secao("Campeonatos salvos", f"{len(campeonatos_salvos())} no arquivo")
        registros_c = campeonatos_salvos()
        if not registros_c:
            st.caption("Nenhum campeonato salvo ainda.")
        for reg in registros_c:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                dados = reg["dados"]
                c1.markdown(
                    f"**🏆 {reg['nome']}**  \n"
                    f"<span class='club-meta'>{FORMATOS.get(dados['formato'], dados['formato'])} · "
                    f"{len(dados['times'])} times · {len(dados['resultados'])} jogos</span>",
                    unsafe_allow_html=True,
                )
                c2.markdown(
                    f"<span class='club-meta'>{reg.get('atualizado_em', '—')[:10]}</span>",
                    unsafe_allow_html=True,
                )
                if c3.button("Abrir", key=f"abrir_camp_{reg['slug']}"):
                    with st.spinner("Carregando..."):
                        try:
                            nomes = dados["times"]
                            times = resolver_times(nomes)
                            indice = {t.nome: t for t in times}
                            camp = Campeonato.de_dict(
                                dados, lambda n, i=indice: i.get(n)
                            )
                            st.session_state.competicao = camp
                            st.session_state.pagina = "competicao"
                            st.rerun()
                        except Exception as e:  # noqa: BLE001
                            st.error(f"❌ Não foi possível abrir: {e}")
                if c3.button("🗑️", key=f"del_camp_{reg['slug']}"):
                    excluir_campeonato(reg["slug"])
                    st.rerun()


def _clubes_da_copa_do_brasil(
    banco: list[str], custom: list[str], total: int = 128
) -> list[Time]:
    """128 clubes para a Copa do Brasil: todas as divisões, por reputação."""
    piramide = get_piramide()
    times = list(piramide.times) if piramide is not None else []
    if not times:
        times = list(st.session_state.get("times") or [])
    if not times:
        times = resolver_times((custom + banco)[:total])
    ordenados = sorted(times, key=lambda t: (-t.reputacao, -t.torcida, t.nome))
    return ordenados[:total]


def _criar_copa_do_brasil(
    banco: list[str],
    custom: list[str],
    temporada: int,
    usar_semente: bool,
    semente: int,
) -> None:
    """Monta a Copa do Brasil (128 clubes, mata-mata em ida e volta)."""
    selecionados = _clubes_da_copa_do_brasil(banco, custom)
    if len(selecionados) < 4:
        st.session_state["erro_copa"] = "não há clubes suficientes para o mata-mata"
        return
    try:
        camp = Campeonato(
            nome="Copa do Brasil",
            times=resolver_times([t.nome for t in selecionados]),
            formato="copa",
            temporada=temporada,
            ida_e_volta=True,
            ida_e_volta_mata=True,
            final_unica=False,
            distribuicao="forca",
            semente=semente if usar_semente else None,
        )
        camp.salvar()
    except Exception as erro:  # noqa: BLE001
        st.session_state["erro_copa"] = str(erro)
        return
    st.session_state.competicao = camp


def _previa_campeonato(
    *,
    formato: str,
    n_times: int,
    n_grupos: int,
    times_por_grupo: int,
    classificados: int,
    ida_e_volta: bool,
    ida_e_volta_mata: bool,
    final_unica: bool,
    terceiro_lugar: bool,
    distribuicao: str,
) -> str:
    """Resumo em texto do formato escolhido, antes de criar o campeonato."""
    if n_times < 2:
        return "escolha ao menos 2 times para ver o formato."
    turnos = 2 if ida_e_volta else 1
    sorteio = "cabeças de chave" if distribuicao == "forca" else "sorteio"

    if formato == "pontos_corridos":
        rodadas = (n_times - 1) * turnos
        jogos = n_times * (n_times - 1) // 2 * turnos
        return (
            f"{n_times} times · {rodadas} rodadas · {jogos} jogos · "
            f"{'turno e returno' if ida_e_volta else 'turno único'}"
        )

    if formato == "copa":
        chave = 1
        while chave < n_times:
            chave *= 2
        byes = chave - n_times
        fases = chave.bit_length() - 1
        extra = " · disputa de 3º lugar" if terceiro_lugar else ""
        return (
            f"chave de {chave} ({byes} folga{'s' if byes != 1 else ''}) · "
            f"{fases} fase{'s' if fases != 1 else ''} · {n_times - 1} jogos{extra} · "
            f"fases em {'ida e volta' if ida_e_volta_mata else 'jogo único'}"
            f"{' (final única)' if final_unica else ''} · {sorteio}"
        )

    # grupos + eliminatórias
    grupos = -(-n_times // max(2, times_por_grupo)) if times_por_grupo else n_grupos
    grupos = max(2, min(grupos, n_times // 2, 12))
    base, resto = divmod(n_times, grupos)
    if base < 2:
        return "poucos times para essa quantidade de grupos."
    classificados_grupo = max(1, min(classificados, base))
    total_classificados = grupos * classificados_grupo
    chave = 1
    while chave < total_classificados:
        chave *= 2

    tamanhos = [base + 1] * resto + [base] * (grupos - resto)
    jogos_grupos = sum(t * (t - 1) // 2 * turnos for t in tamanhos)
    return (
        f"{grupos} grupos ({tamanhos[0]}"
        f"{f'–{tamanhos[-1]}' if tamanhos[0] != tamanhos[-1] else ''} times) · "
        f"classificam {classificados_grupo} por grupo ({total_classificados} no mata-mata) · "
        f"{jogos_grupos} jogos na fase de grupos + {total_classificados - 1} no mata-mata"
        f"{' (mais a disputa de 3º lugar)' if terceiro_lugar else ''} · "
        f"grupos em {'ida e volta' if ida_e_volta else 'turno único'} · "
        f"{sorteio}"
    )
