"""
⚽ BRASFOOT STREAMLIT
Jogo de gerenciamento de futebol brasileiro.

Tipografia
----------
Plus Jakarta Sans → títulos, placares e números de destaque
Manrope           → interface, textos e botões
Inter             → tabelas e dados (com tabular-nums para alinhar)
"""

import streamlit as st

from game.banco_dados import (
    DIVISOES,
    NOMES_DIVISAO,
    clubes_por_divisao,
    criar_times,
)
from game.competicoes import (
    FORMATOS,
    Campeonato,
    campeonatos_salvos,
    excluir_campeonato,
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
from game.liga import League
from game.mercado import Market
from game.modelos import Jogador, Noticia, Time

# ============================================================
# Configuração da página
# ============================================================
st.set_page_config(
    page_title="⚽ Brasfoot Streamlit",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS customizado
# ============================================================
def carregar_estilos():
    st.markdown(
        """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">

<style>
:root{
    --ink:#0E1A14;
    --ink-2:#5A6B61;
    --ink-3:#8A9A90;
    --line:#E4EAE6;
    --line-2:#EEF3F0;
    --surface:#FFFFFF;
    --surface-2:#F7FAF8;
    --brand:#16A34A;
    --brand-700:#15803D;
    --brand-900:#065F46;
    --gold:#F5B301;
    --blue:#2563EB;
    --red:#DC2626;
    --amber:#D97706;
    --radius:14px;
    --shadow-sm:0 1px 2px rgba(16,24,40,.06);
    --shadow:0 1px 3px rgba(16,24,40,.08), 0 12px 28px -18px rgba(16,24,40,.35);
    --font-display:'Plus Jakarta Sans','Manrope',system-ui,sans-serif;
    --font-ui:'Manrope','Inter',system-ui,-apple-system,sans-serif;
    --font-data:'Inter','Manrope',system-ui,sans-serif;
}

/* ---------- base ---------- */
html, body, [class*="css"], .stApp, .stMarkdown, p, span, div, label{
    font-family: var(--font-ui) !important;
    color: var(--ink);
    -webkit-font-smoothing: antialiased;
}

/* ---------- ícones (Material Symbols) ----------
   A regra global acima vale para todo <span> e, com !important, vencia a
   fonte dos ícones nativos do Streamlit — o nome da ligadura aparecia como
   texto (ex.: "keyboard_double_arrow_left" no botão de recolher a sidebar).
   Esta regra tem especificidade maior e devolve a fonte de ícones. */
span[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"],
.material-symbols-rounded,
.material-symbols-outlined{
    font-family: "Material Symbols Rounded" !important;
    font-weight: 400 !important;
    font-style: normal !important;
    font-feature-settings: "liga" !important;
    -webkit-font-feature-settings: "liga" !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
}

/* emojis usados como ícone continuam na fonte de emoji do sistema */
span[data-testid="stIconEmoji"],
[data-testid="stIconEmoji"]{
    font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji",
        var(--font-ui) !important;
}

.stApp{
    background:
        radial-gradient(1200px 600px at 12% -8%, #E9F7EE 0%, rgba(233,247,238,0) 60%),
        radial-gradient(900px 500px at 100% 0%, #EEF4FF 0%, rgba(238,244,255,0) 55%),
        #FCFDFC;
}
.block-container{ max-width:1400px; padding-top:1.8rem; padding-bottom:3rem; }
h1,h2,h3,h4{ font-family: var(--font-display) !important; letter-spacing:-.02em; }

/* ---------- header / footer ---------- */
[data-testid="stHeader"]{
    background:rgba(252,253,252,.82);
    backdrop-filter:blur(10px);
    border-bottom:1px solid var(--line);
}
footer{ visibility:hidden; }

/* ---------- botões ---------- */
.stButton > button{
    border-radius:999px !important;
    font-family:var(--font-ui) !important;
    font-weight:700 !important;
    letter-spacing:.01em;
    border:1px solid var(--line) !important;
    background:var(--surface) !important;
    color:var(--ink) !important;
    box-shadow:var(--shadow-sm);
    transition:transform .12s ease, box-shadow .18s ease, border-color .18s ease, color .18s ease;
    padding:.5rem 1rem;
}
.stButton > button:hover{
    transform:translateY(-1px);
    border-color:var(--brand) !important;
    color:var(--brand-900) !important;
    box-shadow:0 10px 22px -14px rgba(22,163,74,.85);
}
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"]{
    background:linear-gradient(135deg,#16A34A 0%,#065F46 100%) !important;
    color:#fff !important;
    border:none !important;
}
.stButton > button:disabled{ opacity:.45; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#FFFFFF 0%,#F4F9F6 100%);
    border-right:1px solid var(--line);
}
[data-testid="stSidebar"] .stButton > button{
    justify-content:flex-start !important;
    border-radius:10px !important;
    font-weight:600 !important;
    padding:.45rem .8rem;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]{
    box-shadow:0 8px 20px -12px rgba(6,95,70,.9);

}
[data-testid="stSidebar"] hr{ border-color:var(--line); }

/* ---------- containers / cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"]{
    border-radius:var(--radius) !important;
    border:1px solid var(--line) !important;
    background:var(--surface);
    box-shadow:var(--shadow-sm);
    transition:transform .14s ease, box-shadow .2s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover{
    transform:translateY(-2px);
    box-shadow:var(--shadow);
}

/* ---------- métricas ---------- */
[data-testid="stMetric"]{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:var(--radius);
    padding:.85rem 1rem;
    box-shadow:var(--shadow-sm);
}
[data-testid="stMetricLabel"]{
    font-family:var(--font-ui) !important;
    font-size:.72rem !important;
    text-transform:uppercase;
    letter-spacing:.08em;
    color:var(--ink-3) !important;
    font-weight:700 !important;
}
[data-testid="stMetricValue"]{
    font-family:var(--font-data) !important;
    font-variant-numeric:tabular-nums;
    font-size:1.55rem !important;
    font-weight:700 !important;
}

/* ---------- abas ---------- */
.stTabs [data-baseweb="tab-list"]{
    gap:6px;
    background:var(--surface-2);
    padding:6px;
    border-radius:999px;
    border:1px solid var(--line);
}
.stTabs [data-baseweb="tab"]{
    border-radius:999px !important;
    padding:.5rem 1.15rem;
    font-family:var(--font-ui) !important;
    font-weight:700;
    font-size:.9rem;
    color:var(--ink-2);
}
.stTabs [aria-selected="true"]{
    background:linear-gradient(135deg,#16A34A,#065F46) !important;
    color:#fff !important;
}

/* ---------- alertas ---------- */
.stAlert, [data-testid="stNotification"]{
    border-radius:12px !important;
    border:1px solid var(--line) !important;
}

/* ---------- expansor ---------- */
[data-testid="stExpander"]{
    border-radius:12px !important;
    border:1px solid var(--line) !important;
    background:var(--surface);
}

/* ============================================================
   Componentes do jogo
   ============================================================ */
.hero{
    background:linear-gradient(120deg,#065F46 0%,#16A34A 55%,#4ADE80 100%);
    border-radius:22px;
    padding:2.2rem 2rem;
    color:#fff;
    box-shadow:0 24px 50px -30px rgba(6,95,70,.9);
    position:relative;
    overflow:hidden;
    margin-bottom:1.5rem;
}
.hero::after{
    content:"";
    position:absolute; right:-80px; top:-80px;
    width:320px; height:320px; border-radius:50%;
    background:radial-gradient(circle,rgba(255,255,255,.22),rgba(255,255,255,0) 70%);
}
.hero h1{
    font-family:var(--font-display) !important;
    font-weight:800; font-size:2.6rem; margin:0; color:#fff;
    letter-spacing:-.03em;
}
.hero p{ margin:.35rem 0 0 0; color:rgba(255,255,255,.9); font-size:1.02rem; }

.sec-title{
    font-family:var(--font-display) !important;
    font-size:1.15rem; font-weight:800; color:var(--ink);
    margin:1.4rem 0 .7rem 0; display:flex; align-items:center; gap:.5rem;
}
.sec-title .kicker{
    font-size:.68rem; letter-spacing:.12em; text-transform:uppercase;
    color:var(--brand-700); background:#E8F7EE; border-radius:999px;
    padding:.2rem .55rem; font-weight:800;
}

/* cards de estatística */
.stat{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:var(--radius);
    padding:1rem 1.1rem;
    box-shadow:var(--shadow-sm);
    position:relative; overflow:hidden;
}
.stat::before{
    content:""; position:absolute; left:0; top:0; bottom:0; width:4px;
    background:var(--accent,var(--brand));
}
.stat .lbl{
    font-size:.7rem; text-transform:uppercase; letter-spacing:.09em;
    color:var(--ink-3); font-weight:800;
}
.stat .val{
    font-family:var(--font-data) !important; font-variant-numeric:tabular-nums;
    font-size:1.9rem; font-weight:700; letter-spacing:-.02em; margin-top:.15rem;
}

/* card de time (seleção inicial) */
.club-card{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:var(--radius);
    overflow:hidden;
    box-shadow:var(--shadow-sm);
    transition:transform .14s ease, box-shadow .2s ease;
    height:100%;
}
.club-card:hover{ transform:translateY(-3px); box-shadow:var(--shadow); }
.club-card .stripe{ height:6px; background:var(--c1); }
.club-card .body{ padding:.85rem 1rem 0 1rem; }
.club-crest{
    width:46px; height:46px; border-radius:12px; display:flex;
    align-items:center; justify-content:center; font-size:1.35rem;
    background:linear-gradient(135deg,var(--c1),var(--c2));
    box-shadow:inset 0 0 0 1px rgba(0,0,0,.06);
}
.club-name{
    font-family:var(--font-display); font-weight:800; font-size:1.05rem;
    letter-spacing:-.01em; margin:.55rem 0 .1rem 0;
}
.club-meta{ color:var(--ink-3); font-size:.82rem; }
.kv{ display:flex; justify-content:space-between; font-size:.85rem; padding:.18rem 0; }
.kv b{ font-family:var(--font-data) !important; font-variant-numeric:tabular-nums; }

/* tabelas */
.tbl{ width:100%; border-collapse:separate; border-spacing:0; font-family:var(--font-data); }
.tbl th{
    font-family:var(--font-ui) !important; font-size:.68rem; text-transform:uppercase;
    letter-spacing:.08em; color:var(--ink-3); font-weight:800;
    text-align:left; padding:.6rem .7rem; background:var(--surface-2);
    border-bottom:1px solid var(--line); white-space:nowrap;
}
.tbl th:first-child{ border-top-left-radius:10px; }
.tbl th:last-child{ border-top-right-radius:10px; }
.tbl td{
    font-family:var(--font-data) !important;
    padding:.58rem .7rem; border-bottom:1px solid var(--line-2);
    font-variant-numeric:tabular-nums; font-size:.92rem; background:var(--surface);
}
.tbl tbody tr:hover td{ background:#F2FBF5; }
.tbl tr.me td{ background:#EAF7EF; font-weight:700; }
.tbl tr.me td:first-child{ box-shadow:inset 3px 0 0 var(--brand); }
.tbl td.num, .tbl th.num{ text-align:center; }

.zona{ width:8px; height:8px; border-radius:50%; display:inline-block; }
.badge{
    display:inline-block; min-width:30px; text-align:center;
    padding:.12rem .38rem; border-radius:7px; font-weight:700;
    font-family:var(--font-data) !important; font-variant-numeric:tabular-nums; font-size:.82rem;
}
.b-80{ background:#DCFCE7; color:#065F46; }
.b-70{ background:#D1FAE5; color:#047857; }
.b-60{ background:#FEF3C7; color:#92400E; }
.b-50{ background:#F1F5F9; color:#475569; }
.pill{
    display:inline-block; padding:.12rem .5rem; border-radius:999px;
    font-size:.72rem; font-weight:800; letter-spacing:.02em;
}
.p-ok{ background:#DCFCE7; color:#065F46; }
.p-warn{ background:#FEF3C7; color:#92400E; }
.p-bad{ background:#FEE2E2; color:#991B1B; }
.p-info{ background:#E0E7FF; color:#3730A3; }

.energy{ height:7px; border-radius:99px; background:#EEF2F0; overflow:hidden; }
.energy > i{ display:block; height:100%; border-radius:99px; }

/* campo tático */
.pitch{
    position:relative;
    background:repeating-linear-gradient(180deg,#1E7A46 0 46px,#1A6C3E 46px 92px);
    border:3px solid rgba(255,255,255,.85);
    border-radius:16px; padding:20px 16px;
    box-shadow:inset 0 0 70px rgba(0,0,0,.28), var(--shadow);
    overflow:hidden;
}
.pitch::before{
    content:""; position:absolute; left:0; right:0; top:50%; height:2px;
    background:rgba(255,255,255,.45);
}
.pitch::after{
    content:""; position:absolute; left:50%; top:50%; width:96px; height:96px;
    transform:translate(-50%,-50%); border:2px solid rgba(255,255,255,.45);
    border-radius:50%;
}
.pitch-row{ position:relative; z-index:2; display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin:7px 0; }
.chip{
    position:relative; z-index:2;
    display:flex; align-items:center; gap:.45rem;
    background:rgba(255,255,255,.96); color:#0E1A14;
    border-radius:999px; padding:.32rem .7rem;
    font-family:var(--font-ui); font-weight:700; font-size:.82rem;
    box-shadow:0 4px 10px -6px rgba(0,0,0,.6);
}
.chip .ovr{
    font-family:var(--font-data) !important; font-variant-numeric:tabular-nums;
    background:#0E1A14; color:#fff; border-radius:6px; padding:0 .3rem; font-size:.75rem;
}
.chip .en{ font-size:.7rem; color:#5A6B61; }

/* placar */
.score{
    border-radius:20px; padding:1.6rem; color:#fff; text-align:center;
    background:var(--sc,#0E1A14);
    box-shadow:0 22px 44px -28px rgba(0,0,0,.85);
}
.score .teams{
    font-family:var(--font-display) !important; font-weight:800; font-size:1.5rem;
    display:flex; align-items:center; justify-content:center; gap:1rem; flex-wrap:wrap;
}
.score .goals{
    font-family:var(--font-data) !important; font-variant-numeric:tabular-nums;
    font-size:3rem; font-weight:800; letter-spacing:.02em;
}
.score .tag{ font-size:.9rem; opacity:.95; font-weight:700; letter-spacing:.04em; }
.score .pub{ font-size:.78rem; opacity:.8; }

/* linha do tempo de eventos */
.tl{ position:relative; margin-left:10px; padding-left:18px; border-left:2px solid var(--line); }
.tl .ev{ position:relative; padding:.35rem 0; font-size:.9rem; }
.tl .ev::before{
    content:""; position:absolute; left:-25px; top:.75rem;
    width:10px; height:10px; border-radius:50%;
    background:var(--dot,#CBD5E1); box-shadow:0 0 0 3px #fff;
}
.tl .ev.gol::before{ background:var(--brand); }
.tl .ev.amarelo::before{ background:var(--gold); }
.tl .ev.vermelho::before{ background:var(--red); }
.tl .ev.defesa::before{ background:var(--blue); }

/* lista de resultados */
.res{
    display:flex; align-items:center; gap:.6rem;
    border:1px solid var(--line); border-radius:12px;
    padding:.55rem .8rem; margin:.35rem 0; background:var(--surface);
    font-family:var(--font-data) !important; font-variant-numeric:tabular-nums;
}
.res .tag{
    font-family:var(--font-ui); font-weight:800; font-size:.75rem;
    padding:.1rem .45rem; border-radius:7px;
}
.v{ background:#DCFCE7; color:#065F46; }
.e{ background:#FEF3C7; color:#92400E; }
.d{ background:#FEE2E2; color:#991B1B; }

.legenda{ color:var(--ink-3); font-size:.8rem; }
hr{ border-color:var(--line); }
</style>
""",
        unsafe_allow_html=True,
    )


carregar_estilos()


# ============================================================
# Inicializar estado do jogo
# ============================================================
def init_game():
    """Inicializa um novo jogo."""
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
    if "times" not in st.session_state:
        st.session_state.times = None
    if "league" not in st.session_state:
        st.session_state.league = None
    if "market" not in st.session_state:
        st.session_state.market = None
    if "meu_time" not in st.session_state:
        st.session_state.meu_time = None
    if "ultimo_resultado" not in st.session_state:
        st.session_state.ultimo_resultado = None
    if "pagina" not in st.session_state:
        st.session_state.pagina = "inicio"


init_game()


# ============================================================
# Funções auxiliares
# ============================================================
def get_meu_time() -> Time | None:
    """Retorna o time do jogador."""
    if not st.session_state.times:
        return None
    for t in st.session_state.times:
        if t.nome == st.session_state.meu_time:
            return t
    return None


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
    st.markdown(
        f'<div class="sec-title">{k}{titulo}</div>', unsafe_allow_html=True
    )


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


# ============================================================
# TELA INICIAL - Seleção de time
# ============================================================
def tela_inicial():
    st.markdown(
        """
    <div class="hero">
        <h1>⚽ BRASFOOT</h1>
        <p>Gerenciador de futebol brasileiro — escolha seu clube, monte a equipe
        e busque o título do Brasileirão.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # banco completo (156 clubes) — a divisão escolhida vira o campeonato
    if st.session_state.times is None:
        st.session_state.times = criar_times(None)

    banco = list(st.session_state.times)

    col_div, col_info = st.columns([1, 3])
    with col_div:
        divisao = (
            st.selectbox(
                "Divisão",
                list(DIVISOES),
                index=0,
                format_func=lambda d: NOMES_DIVISAO.get(d, str(d)),
                key="divisao_inicial",
            )
            or "A"
        )
    times = [t for t in banco if t.divisao == divisao]
    with col_info:
        st.caption(
            f"**{NOMES_DIVISAO.get(divisao, divisao)}** — {len(times)} clubes. "
            f"O campeonato é disputado só entre os clubes da divisão escolhida."
        )

    secao("Escolha seu time para começar a temporada", NOMES_DIVISAO.get(divisao, divisao))

    custom = [
        t
        for t in st.session_state.get("clubes_custom", [])
        if t.nome not in {x.nome for x in times}
    ]
    if custom:
        incluir = st.toggle(
            f"Incluir meus clubes criados ({len(custom)})", value=True
        )
        if incluir:
            times += custom

    cols_per_row = 4
    for i in range(0, len(times), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(times):
                continue
            time = times[idx]
            with col:
                st.markdown(
                    f"""
                <div class="club-card">
                    <div class="stripe" style="--c1:{time.cor_primaria}"></div>
                    <div class="body">
                        <div class="club-crest"
                             style="--c1:{time.cor_primaria};--c2:{time.cor_secundaria}">
                            {time.escudo_emoji}
                        </div>
                        <div class="club-name">{time.nome}</div>
                        <div class="club-meta">📍 {time.cidade}/{time.estado}</div>
                        <div class="kv"><span>Força</span><b>⭐ {time.overall_time}</b></div>
                        <div class="kv"><span>Caixa</span><b>{formatar_dinheiro(time.financas)}</b></div>
                        <div class="kv"><span>Elenco</span><b>{len(time.jogadores)} jogadores</b></div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    f"Escolher {time.sigla}",
                    key=f"btn_{time.sigla}_{idx}",
                    use_container_width=True,
                    type="primary",
                ):
                    # a lista pode incluir clubes criados pelo jogador
                    st.session_state.times = times
                    st.session_state.meu_time = time.nome
                    st.session_state.league = League(times)
                    st.session_state.market = Market(times)
                    st.session_state.game_started = True
                    st.session_state.pagina = "painel"
                    st.rerun()
                st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)


# ============================================================
# SIDEBAR - Navegação
# ============================================================
def sidebar():
    time = get_meu_time()
    if time is None:
        return

    league = st.session_state.league

    with st.sidebar:
        st.markdown(
            f"""
        <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.4rem;">
            <div class="club-crest" style="--c1:{time.cor_primaria};--c2:{time.cor_secundaria}">
                {time.escudo_emoji}
            </div>
            <div>
                <div style="font-family:var(--font-display);font-weight:800;font-size:1.15rem;line-height:1.1">
                    {time.nome}
                </div>
                <div class="club-meta">Temporada {league.temporada} · {time.cidade}/{time.estado}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.progress(
            min(1.0, league.rodada_atual / max(1, league.total_rodadas)),
            text=f"Rodada {league.rodada_atual}/{league.total_rodadas}",
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Caixa", formatar_dinheiro(time.financas))
        with col2:
            st.metric("⭐ Overall", time.overall_time)

        col3, col4 = st.columns(2)
        with col3:
            st.metric(
                "📊 Posição", f"{posicao_na_tabela(league, time.nome)}º"
            )
        with col4:
            st.metric("🎭 Moral", f"{time.moral_time}%")

        prox = league.proximo_adversario(time.nome)
        st.markdown(
            f"""
        <div style="border:1px dashed var(--line);border-radius:12px;padding:.6rem .8rem;
                    background:var(--surface-2)">
            <div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;
                        color:var(--ink-3);font-weight:800">Próximo jogo</div>
            <div style="font-weight:700;margin-top:.15rem">📅 {prox}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        paginas = {
            "painel": "🏠 Painel",
            "elenco": "👥 Elenco",
            "tatica": "📋 Tática",
            "jogar": "⚽ Jogar Rodada",
            "classificacao": "🏆 Classificação",
            "mercado": "🏪 Mercado",
            "resultados": "📊 Resultados",
            "noticias": "📰 Notícias",
            "criador": "🛠️ Criador",
        }

        if st.session_state.get("competicao") is not None:
            paginas["competicao"] = "🏆 Competição"

        for key, label in paginas.items():
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if st.session_state.pagina == key else "secondary",
            ):
                st.session_state.pagina = key
                st.rerun()

        st.markdown("---")

        if st.button("🔄 Novo Jogo", use_container_width=True):
            # preserva o que foi criado no Criador (clubes e competição em curso)
            preservar = {
                k: st.session_state[k]
                for k in ("clubes_custom", "competicao")
                if k in st.session_state
            }
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.update(preservar)
            st.rerun()


# ============================================================
# PAINEL PRINCIPAL
# ============================================================
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
        <h1 style="font-size:1.8rem">🏠 {time.escudo_emoji} {time.nome}</h1>
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
                f"<td>{t.escudo_emoji} {t.sigla}</td>"
                f"<td class='num'><b>{t.pontos}</b></td>"
                f"<td class='num'>{t.vitorias}V {t.empates}E {t.derrotas}D</td></tr>"
            )
        if pos > 8:
            linhas.append(
                f"<tr class='me'><td class='num'>{pos}º</td><td></td>"
                f"<td>{time.escudo_emoji} {time.sigla}</td>"
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
            st.info(f"**{noticia.titulo}** (Rodada {noticia.rodada})\n\n{noticia.texto}")


# ============================================================
# ELENCO
# ============================================================
def tela_elenco():
    time = get_meu_time()
    if time is None:
        st.error("Não foi possível encontrar o time selecionado.")
        return

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">👥 Elenco · {time.escudo_emoji} {time.nome}</h1>
        <p>{len(time.jogadores)} jogadores · overall {time.overall_time} ·
        valor de elenco {formatar_dinheiro(time.valor_elenco)}</p>
    </div>
    """,
        unsafe_allow_html=True,
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


# ============================================================
# TÁTICA
# ============================================================
def tela_tatica():
    time = get_meu_time()
    if time is None:
        st.warning("Nenhum time selecionado.")
        return

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">📋 Tática · {time.escudo_emoji} {time.nome}</h1>
        <p>Formação {time.formacao} · estilo {_nome_estilo(time.tatica_ofensiva)}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        secao("Formação", "Esquema")
        formacoes = ["4-4-2", "4-3-3", "3-5-2", "4-5-1", "5-3-2"]
        formacao = st.selectbox(
            "Escolha a formação",
            formacoes,
            index=formacoes.index(time.formacao)
            if time.formacao in formacoes
            else 0,
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


# ============================================================
# JOGAR RODADA
# ============================================================
def tela_jogar():
    time = get_meu_time()
    league = st.session_state.league

    if time is None:
        st.error("Nenhum time selecionado. Selecione um time para continuar.")
        return

    if league.campeonato_encerrado or league.rodada_atual >= len(league.calendario):
        _tela_fim_temporada(time, league)
        return

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">⚽ Rodada {league.rodada_atual + 1} de {league.total_rodadas}</h1>
        <p>{time.escudo_emoji} {time.nome} · {league.proximo_adversario(time.nome)}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if len(time.titulares) != 11:
        st.warning(
            f"⚠️ Você tem {len(time.titulares)} titulares! Precisa de 11. "
            f"Vá em 📋 Tática para ajustar."
        )

    # Encontrar adversário
    adversario = None
    em_casa = False
    for casa, fora in league.calendario[league.rodada_atual]:
        if casa == time.nome:
            adversario = league._get_time_por_nome(fora)
            em_casa = True
            break
        elif fora == time.nome:
            adversario = league._get_time_por_nome(casa)
            em_casa = False
            break

    if adversario:
        secao("Pré-jogo", "Confronto")
        col1, col2, col3 = st.columns([2, 1, 2])

        with col1:
            st.markdown(_cartao_time(time, "🏠 Casa" if em_casa else "✈️ Fora"),
                        unsafe_allow_html=True)
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
            st.markdown(_cartao_time(adversario, "✈️ Fora" if em_casa else "🏠 Casa"),
                        unsafe_allow_html=True)

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("⚽ SIMULAR RODADA!", type="primary", use_container_width=True):
            with st.spinner("⚽ Simulando jogos..."):
                resultados = league.simular_rodada(time.nome)
                st.session_state.ultimo_resultado = resultados
                st.rerun()

    if st.session_state.ultimo_resultado and league.rodada_atual > 0:
        meu_jogo = league.jogo_do_jogador(time.nome, league.rodada_atual)
        if meu_jogo:
            secao(f"Resultado · Rodada {league.rodada_atual}", "Seu jogo")

            if time.nome == meu_jogo.time_casa:
                meus_gols = meu_jogo.gols_casa
                gols_adv = meu_jogo.gols_fora
            else:
                meus_gols = meu_jogo.gols_fora
                gols_adv = meu_jogo.gols_casa

            if meus_gols > gols_adv:
                cor, txt = "linear-gradient(135deg,#16A34A,#065F46)", "VITÓRIA"
            elif meus_gols < gols_adv:
                cor, txt = "linear-gradient(135deg,#DC2626,#7F1D1D)", "DERROTA"
            else:
                cor, txt = "linear-gradient(135deg,#D97706,#92400E)", "EMPATE"

            st.markdown(
                f"""
            <div class="score" style="--sc:{cor}">
                <div class="teams">{meu_jogo.time_casa}
                    <span class="goals">{meu_jogo.gols_casa} x {meu_jogo.gols_fora}</span>
                    {meu_jogo.time_fora}</div>
                <div class="tag" style="margin-top:.4rem">{txt}</div>
                <div class="pub">Público: {meu_jogo.publico:,}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if meu_jogo.eventos:
                secao("Eventos da Partida", "Narração")
                _linha_do_tempo(meu_jogo.eventos)

        secao("Outros Resultados", "Rodada")
        for partida in st.session_state.ultimo_resultado:
            if time.nome not in (partida.time_casa, partida.time_fora):
                st.markdown(
                    f'<div class="res">⚽ <b>{partida.time_casa}</b> '
                    f"{partida.gols_casa} x {partida.gols_fora} "
                    f"<b>{partida.time_fora}</b></div>",
                    unsafe_allow_html=True,
                )


def _cartao_time(time: Time, local: str) -> str:
    return f"""
    <div class="stat" style="--accent:{time.cor_primaria}">
        <div style="display:flex;align-items:center;gap:.6rem">
            <div class="club-crest" style="--c1:{time.cor_primaria};--c2:{time.cor_secundaria}">
                {time.escudo_emoji}
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

    st.markdown(
        '<div class="tl">' + "".join(itens) + "</div>", unsafe_allow_html=True
    )


def _tela_fim_temporada(time: Time, league: League):
    campeao = league.classificacao[0]
    pos = posicao_na_tabela(league, time.nome)
    n = len(league.classificacao)

    st.markdown(
        f"""
    <div class="hero" style="background:linear-gradient(120deg,#92400E 0%,#F5B301 55%,#FDE68A 100%);
                             color:#1F1300">
        <h1 style="color:#1F1300">🏆 CAMPEONATO ENCERRADO</h1>
        <p style="color:rgba(31,19,0,.85)">
            Campeão: <b>{campeao.escudo_emoji} {campeao.nome}</b> com {campeao.pontos} pontos<br>
            Sua posição: <b>{pos}º</b> com {time.pontos} pontos
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if pos == 1:
        st.balloons()
        st.success("🎉🏆 PARABÉNS! VOCÊ É O CAMPEÃO BRASILEIRO! 🏆🎉")
    elif pos <= 4:
        st.success(f"✅ Classificado para a Libertadores! ({pos}º lugar)")
    elif pos <= 6:
        st.info(f"Classificado para a Sul-Americana ({pos}º lugar)")
    elif pos >= n - 3:
        st.error(f"😢 Rebaixado! ({pos}º lugar)")

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


# ============================================================
# CLASSIFICAÇÃO
# ============================================================
def tela_classificacao():
    league = st.session_state.league
    time = get_meu_time()

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">🏆 Classificação</h1>
        <p>{NOMES_DIVISAO.get(time.divisao, "Brasileirão") if time else "Brasileirão"} ·
        Temporada {league.temporada} · Rodada {league.rodada_atual}/{league.total_rodadas}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["📊 Tabela", "⚽ Artilharia"])

    with tab1:
        classif = league.classificacao
        n = len(classif)
        linhas = []
        for i, t in enumerate(classif):
            pos = i + 1
            if pos <= 4:
                zona, zona_txt = "#16A34A", "Libertadores"
            elif pos <= 6:
                zona, zona_txt = "#F5B301", "Sul-Americana"
            elif pos >= n - 3:
                zona, zona_txt = "#DC2626", "Rebaixamento"
            else:
                zona, zona_txt = "#CBD5E1", "Meio de tabela"

            me = "me" if time is not None and t.nome == time.nome else ""
            sg = t.saldo_gols
            sg_html = (
                f'<span class="pill {"p-ok" if sg > 0 else "p-bad" if sg < 0 else "p-info"}">'
                f'{sg:+d}</span>'
            )
            linhas.append(
                f"<tr class='{me}' title='{zona_txt}'>"
                f"<td class='num'><b>{pos}º</b></td>"
                f"<td class='num'><span class='zona' style='background:{zona}'></span></td>"
                f"<td>{t.escudo_emoji} {t.nome}</td>"
                f"<td class='num'><b>{t.pontos}</b></td>"
                f"<td class='num'>{t.jogos_campeonato}</td>"
                f"<td class='num'>{t.vitorias}</td>"
                f"<td class='num'>{t.empates}</td>"
                f"<td class='num'>{t.derrotas}</td>"
                f"<td class='num'>{t.gols_pro}</td>"
                f"<td class='num'>{t.gols_contra}</td>"
                f"<td class='num'>{sg_html}</td>"
                f"<td class='num'>{badge_overall(t.overall_time)}</td>"
                "</tr>"
            )

        st.markdown(
            "<table class='tbl'><thead><tr>"
            "<th class='num'>#</th><th class='num'>Zona</th><th>Time</th>"
            "<th class='num'>Pts</th><th class='num'>J</th><th class='num'>V</th>"
            "<th class='num'>E</th><th class='num'>D</th><th class='num'>GP</th>"
            "<th class='num'>GC</th><th class='num'>SG</th><th class='num'>OVR</th>"
            "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="legenda" style="margin-top:.8rem">
            <span class="zona" style="background:#16A34A"></span> Libertadores (1º–4º) ·
            <span class="zona" style="background:#F5B301"></span> Sul-Americana (5º–6º) ·
            <span class="zona" style="background:#DC2626"></span> Rebaixamento (últimos 4)
        </div>
        """,
            unsafe_allow_html=True,
        )

    with tab2:
        secao("Artilheiros", "Top 20")
        artilheiros = league.artilharia(20)

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


# ============================================================
# MERCADO DE TRANSFERÊNCIAS
# ============================================================
def tela_mercado():
    time = get_meu_time()
    if time is None:
        st.warning("Selecione um time antes de acessar o mercado de transferências.")
        return

    market = st.session_state.market

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">🏪 Mercado de Transferências</h1>
        <p>Orçamento disponível: <b>{formatar_dinheiro(time.financas)}</b> ·
        elenco: {len(time.jogadores)}/30 jogadores</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["🛒 Comprar", "💸 Vender", "📊 Jogadores Livres"])

    with tab1:
        secao("Jogadores Disponíveis", "Ofertas")
        col_a, col_b, col_c = st.columns([2, 2, 1])
        with col_a:
            filtro_pos = st.selectbox(
                "Posição",
                ["Todas", "GOL", "ZAG", "LAT", "VOL", "MEI", "ATA"],
                key="filtro_compra",
            )
        with col_b:
            filtro_max = st.number_input(
                "Preço máximo (R$)",
                min_value=0,
                value=max(0, time.financas),
                step=500_000,
                key="preco_max",
            )
        with col_c:
            st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
            if st.button("🔄 Atualizar Mercado"):
                market.atualizar_mercado()
                st.rerun()

        ofertas = market.ofertas_disponiveis
        if filtro_pos != "Todas":
            ofertas = [(j, t, p) for j, t, p in ofertas if j.posicao == filtro_pos]
        ofertas = [(j, t, p) for j, t, p in ofertas if p <= filtro_max]
        ofertas = [(j, t, p) for j, t, p in ofertas if t.nome != time.nome]
        ofertas.sort(key=lambda x: x[0].overall, reverse=True)

        if ofertas:
            for j, t_vendedor, preco in ofertas[:20]:
                with st.container(border=True):
                    cols = st.columns([2.2, 0.7, 0.7, 1, 1, 1])
                    cols[0].markdown(
                        f"**{cor_posicao(j.posicao)} {j.nome}** "
                        f"<span style='color:var(--ink-3)'>· {t_vendedor.sigla}</span>",
                        unsafe_allow_html=True,
                    )
                    cols[1].markdown(badge_overall(j.overall), unsafe_allow_html=True)
                    cols[2].markdown(f"🎂 {j.idade}")
                    cols[3].markdown(f"💰 **{formatar_dinheiro(preco)}**")
                    cols[4].markdown(
                        f"<span style='color:var(--ink-3)'>💵 {formatar_dinheiro(j.salario)}/mês</span>",
                        unsafe_allow_html=True,
                    )
                    with cols[5]:
                        if st.button("Comprar", key=f"buy_{j.id}", type="primary",
                                     use_container_width=True):
                            sucesso, msg = market.comprar_jogador(
                                j, t_vendedor, time, preco
                            )
                            if sucesso:
                                st.session_state.league.noticias.append(
                                    Noticia(
                                        titulo=f"📋 {time.nome} contrata {j.nome}!",
                                        texto=f"{j.nome} chega do {t_vendedor.nome} "
                                              f"por {formatar_dinheiro(preco)}",
                                        rodada=st.session_state.league.rodada_atual,
                                        tipo="transferencia",
                                    )
                                )
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("Nenhum jogador disponível com os filtros selecionados.")

    with tab2:
        secao("Vender Jogadores", f"{len(time.jogadores)} no elenco")
        for j in sorted(time.jogadores, key=lambda x: x.overall, reverse=True):
            with st.container(border=True):
                cols = st.columns([2.2, 0.7, 0.7, 1, 1, 1])
                cols[0].markdown(
                    f"**{cor_posicao(j.posicao)} {j.nome}**"
                    f"{' ⭐' if j.titular else ''}",
                    unsafe_allow_html=True,
                )
                cols[1].markdown(badge_overall(j.overall), unsafe_allow_html=True)
                cols[2].markdown(f"🎂 {j.idade}")
                cols[3].markdown(f"💎 {formatar_dinheiro(j.valor_mercado)}")
                cols[4].markdown(
                    f"<span style='color:var(--ink-3)'>💵 {formatar_dinheiro(j.salario)}/mês</span>",
                    unsafe_allow_html=True,
                )
                with cols[5]:
                    if st.button("Vender", key=f"sell_{j.id}",
                                 use_container_width=True):
                        sucesso, msg = market.vender_jogador(j, time)
                        if sucesso:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    with tab3:
        secao("Jogadores Livres", "Sem contrato")
        st.caption(
            "Custo de contratação: 6 meses de salário adiantados."
        )
        if st.button("🔍 Buscar Jogadores Livres", type="primary"):
            livres = [market.gerar_jogador_livre() for _ in range(8)]
            st.session_state["jogadores_livres"] = livres

        if st.session_state.get("jogadores_livres"):
            for j in st.session_state["jogadores_livres"]:
                with st.container(border=True):
                    cols = st.columns([2.2, 0.7, 0.7, 1, 1, 1])
                    cols[0].markdown(f"**{cor_posicao(j.posicao)} {j.nome}**",
                                     unsafe_allow_html=True)
                    cols[1].markdown(badge_overall(j.overall), unsafe_allow_html=True)
                    cols[2].markdown(f"🎂 {j.idade}")
                    cols[3].markdown(f"💵 {formatar_dinheiro(j.salario)}/mês")
                    cols[4].markdown(
                        f"💎 {formatar_dinheiro(j.valor_mercado)}"
                    )
                    with cols[5]:
                        custo = j.salario * 6
                        if st.button(
                            f"Contratar {formatar_dinheiro(custo)}",
                            key=f"free_{j.id}",
                            type="primary",
                            use_container_width=True,
                        ):
                            if len(time.jogadores) >= 30:
                                st.error("❌ Elenco lotado!")
                            elif time.financas < custo:
                                st.error("❌ Dinheiro insuficiente!")
                            else:
                                time.financas -= custo
                                time.jogadores.append(j)
                                time.auto_escalar()
                                st.session_state["jogadores_livres"].remove(j)
                                st.success(f"✅ {j.nome} contratado!")
                                st.rerun()


# ============================================================
# CRIADOR — clubes, jogadores e campeonatos
# ============================================================
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
            capacidade = c10.number_input("Capacidade", 1_000, 120_000, 30_000, step=1_000)

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
                            {clube.escudo_emoji}
                        </div>
                        <div class="club-name">{clube.nome} ({clube.sigla})</div>
                        <div class="club-meta">📍 {clube.cidade}/{clube.estado or '—'} ·
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
                if st.button("💾 Salvar clube", use_container_width=True, type="primary"):
                    slug = salvar_clube(clube)
                    st.success(f"✅ {clube.nome} salvo como `{slug}`")
                if st.button(
                    "🎮 Usar no próximo jogo", use_container_width=True
                ):
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
            nome_j = c1.text_input("Nome", value="", placeholder="Deixe vazio para sortear")
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
        por_divisao = {
            d: [c.nome for c in clubes_por_divisao(d)] for d in DIVISOES
        }
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

        col_o1, col_o2, col_o3 = st.columns(3)
        ida_e_volta = col_o1.checkbox("Ida e volta", value=True)
        if formato == "pontos_corridos":
            promovidos = col_o2.number_input("Promovidos", 0, 10, 3)
            rebaixados = col_o3.number_input("Rebaixados", 0, 10, 3)
            n_grupos, classificados, final_unica = 4, 2, True
        elif formato == "copa":
            final_unica = col_o2.checkbox("Final em jogo único", value=True)
            n_grupos, classificados, promovidos, rebaixados = 4, 2, 0, 0
        else:
            n_grupos = col_o2.number_input("Número de grupos", 2, 8, 4)
            classificados = col_o3.number_input("Classificados por grupo", 1, 4, 2)
            final_unica = col_o1.checkbox("Final em jogo único", value=True)
            promovidos, rebaixados = 0, 0

        if st.button("🏆 Criar campeonato", type="primary", use_container_width=True):
            if len(selecao) < 2:
                st.error("❌ Selecione ao menos 2 times.")
            elif formato == "grupos_mata" and len(selecao) < 4:
                st.error("❌ Grupos + eliminatórias precisa de ao menos 4 times.")
            else:
                with st.spinner("Montando o campeonato..."):
                    try:
                        times = resolver_times(selecao)
                        camp = Campeonato(
                            nome=nome_c or "Meu Campeonato",
                            times=times,
                            formato=formato,
                            ida_e_volta=ida_e_volta,
                            n_grupos=int(n_grupos),
                            classificados_por_grupo=int(classificados),
                            promovidos=int(promovidos),
                            rebaixados=int(rebaixados),
                            final_unica=bool(final_unica),
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
                if j is not None and meu_time and c3.button(
                    "Contratar", key=f"usar_jog_{reg['slug']}"
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


# ============================================================
# COMPETIÇÃO PERSONALIZADA
# ============================================================
def _html_tabela(linhas: list[dict]) -> str:
    """Monta a tabela HTML de classificação (linhas já ordenadas)."""
    corpo = []
    for i, l in enumerate(linhas, 1):
        t = l["time"]
        sg = l["sg"]
        classe_sg = "p-ok" if sg > 0 else "p-bad" if sg < 0 else "p-info"
        corpo.append(
            f"<tr><td class='num'>{i}º</td>"
            f"<td>{t.escudo_emoji} {t.nome}</td>"
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
                <h1 style="color:#1F1300;font-size:1.6rem">🏆 {campeao.escudo_emoji} {campeao.nome} CAMPEÃO</h1>
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
                    f'<div class="res">🎟️ <b>{b.escudo_emoji} {b.nome}</b> '
                    f'<span class="tag e" style="margin-left:auto">Folga (BYE)</span></div>',
                    unsafe_allow_html=True,
                )
                continue
            if b is None:
                st.markdown(
                    f'<div class="res">🎟️ <b>{a.escudo_emoji} {a.nome}</b> '
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
                <span><b>{a.escudo_emoji} {a.nome}</b></span>
                <span style="font-size:1.25rem"><b>{gols_a} x {gols_b}</b></span>
                <span><b>{b.escudo_emoji} {b.nome}</b></span>
                <span class="tag {cls_b}">{b.sigla}</span>
                <span style="margin-left:auto" class="club-meta">{jogos_txt or 'aguardando'}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )
        st.caption("Ida e volta" if fase.ida_e_volta else "Jogo único")

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


# ============================================================
# RESULTADOS
# ============================================================
def tela_resultados():
    league = st.session_state.league
    time = get_meu_time()

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">📊 Resultados por Rodada</h1>
        <p>{len(league.resultados)} rodadas disputadas na temporada {league.temporada}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if league.rodada_atual == 0:
        st.info("Nenhuma rodada disputada ainda.")
        return

    rodada_sel = st.selectbox(
        "Selecione a rodada",
        range(1, league.rodada_atual + 1),
        index=league.rodada_atual - 1,
    )

    if rodada_sel in league.resultados:
        secao(f"Rodada {rodada_sel}", "Jogos")
        for partida in league.resultados[rodada_sel]:
            destaque = time is not None and time.nome in (
                partida.time_casa,
                partida.time_fora,
            )
            st.markdown(
                f"""
            <div class="res" style="{'border-color:var(--brand);background:#F2FBF5' if destaque else ''}">
                <span style="{'font-weight:800' if destaque else ''}">⚽ {partida.time_casa}
                <b>{partida.gols_casa} x {partida.gols_fora}</b> {partida.time_fora}</span>
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


# ============================================================
# NOTÍCIAS
# ============================================================
def tela_noticias():
    league = st.session_state.league

    st.markdown(
        """
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">📰 Notícias</h1>
        <p>Tudo o que acontece no Brasileirão</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if not league.noticias:
        st.info("Nenhuma notícia no momento. Jogue algumas rodadas!")
        return

    tipo_emoji = {
        "geral": "📰",
        "transferencia": "📋",
        "resultado": "⚽",
        "lesao": "🏥",
    }

    for noticia in reversed(league.noticias):
        emoji = tipo_emoji.get(noticia.tipo, "📰")
        with st.container(border=True):
            st.markdown(
                f"""
            <div style="display:flex;gap:.7rem;align-items:flex-start">
                <div style="font-size:1.4rem">{emoji}</div>
                <div>
                    <div style="font-family:var(--font-display);font-weight:800;font-size:1.02rem">
                        {noticia.titulo}
                    </div>
                    <div style="color:var(--ink-2);margin-top:.15rem">{noticia.texto}</div>
                    <div class="club-meta" style="margin-top:.3rem">Rodada {noticia.rodada}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


# ============================================================
# ROTEAMENTO PRINCIPAL
# ============================================================
def main():
    if not st.session_state.game_started:
        tela_inicial()
    else:
        sidebar()
        pagina = st.session_state.pagina
        if pagina == "elenco":
            tela_elenco()
        elif pagina == "tatica":
            tela_tatica()
        elif pagina == "jogar":
            tela_jogar()
        elif pagina == "classificacao":
            tela_classificacao()
        elif pagina == "mercado":
            tela_mercado()
        elif pagina == "resultados":
            tela_resultados()
        elif pagina == "noticias":
            tela_noticias()
        elif pagina == "criador":
            tela_criador()
        elif pagina == "competicao":
            tela_competicao()
        else:
            tela_painel()


if __name__ == "__main__":
    main()
