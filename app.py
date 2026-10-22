"""
⚽ BRASFOOT STREAMLIT
Jogo de gerenciamento de futebol brasileiro.

Tipografia
----------
Plus Jakarta Sans → títulos, placares e números de destaque
Manrope           → interface, textos e botões
Inter             → tabelas e dados (com tabular-nums para alinhar)
"""

import datetime as dt

import streamlit as st

from game.banco_dados import (
    DIVISOES,
    NOMES_DIVISAO,
    clubes_por_divisao,
    criar_times,
)
from game.competicoes import (
    DISTRIBUICOES,
    FORMATOS,
    Campeonato,
    campeonatos_salvos,
    excluir_campeonato,
    limites,
)
from game.copa import REGULAMENTO as REGULAMENTO_COPA
from game.copa import FaseCopa
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
from game.divisao import Fase as FaseDivisao
from game.escudos import imagem as escudo_img
from game.liga import League
from game.mercado import Market
from game.modelos import Jogador, Noticia, Partida, Time
from game.piramide import Piramide
from game.piramide import data_da_rodada as data_semana
from game.regional import REGULAMENTO as REGULAMENTO_REGIONAL
from game.regional import TorneioRegional

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
.club-crest .escudo-crest{
    width:100%; height:100%; object-fit:contain; padding:2px;
    filter:drop-shadow(0 1px 2px rgba(0,0,0,.28));
}
img.escudo{
    width:1.15em; height:1.15em; object-fit:contain;
    vertical-align:-.22em; margin-right:.26em;
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

/* ============================================================
   Refinamentos de acabamento / responsivo
   ============================================================ */
:focus-visible{
    outline:2px solid var(--brand); outline-offset:2px; border-radius:8px;
}

/* barras de rolagem discretas (tabelas largas, abas, listas) */
*{ scrollbar-width:thin; scrollbar-color:#CFD9D3 transparent; }
*::-webkit-scrollbar{ width:8px; height:8px; }
*::-webkit-scrollbar-thumb{ background:#D5DED8; border-radius:999px; }
*::-webkit-scrollbar-thumb:hover{ background:#B8C6BC; }

/* tabelas de classificação: rolagem horizontal em telas estreitas */
[data-testid="stMarkdownContainer"]:has(> table.tbl){
    overflow-x:auto;
    border:1px solid var(--line);
    border-radius:12px;
    box-shadow:var(--shadow-sm);
    background:var(--surface);
}
[data-testid="stMarkdownContainer"]:has(table.tbl) > table.tbl{ min-width:540px; }
.tbl tbody tr:last-child td{ border-bottom:none; }

/* títulos de seção com respiro e filete */
.sec-title{
    padding-bottom:.5rem;
    border-bottom:1px solid var(--line-2);
    margin-bottom:.85rem;
}
.sec-title .kicker{ margin-right:.15rem; }

/* linhas de resultado com microinteração */
.res{
    transition:border-color .15s ease, box-shadow .18s ease;
}
.res:hover{
    border-color:#CFE9DA;
    box-shadow:0 10px 20px -18px rgba(16,24,40,.65);
}
.res .tag{ min-width:1.5rem; text-align:center; }

/* cartões de clube */
.club-card .body{ padding-bottom:.9rem; }

/* card do clube: escudo ao lado do nome */
.club-card .club-top{
    display:flex; align-items:center; gap:.75rem;
    margin:.1rem 0 .7rem 0;
}
.club-card .club-top .club-name{ margin:0; }
.club-card .club-crest{ width:50px; height:50px; flex:0 0 auto; }


@media (max-width:900px){
    .block-container{ padding-left:1rem !important; padding-right:1rem !important; }
    .hero{ padding:1.5rem 1.2rem; border-radius:18px; }
    .hero h1{ font-size:1.85rem !important; }
    .sec-title{ font-size:1.02rem; }
    .stat .val{ font-size:1.55rem; }
    .stTabs [data-baseweb="tab-list"]{ overflow-x:auto; flex-wrap:nowrap; }
    .stTabs [data-baseweb="tab"]{ padding:.45rem .85rem; font-size:.82rem; white-space:nowrap; }
}

@media (prefers-reduced-motion:reduce){
    *{ transition:none !important; animation:none !important; }
}
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
# Temporada completa (todas as divisões)
# ============================================================
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
    partidas = {p.time_casa + "|" + p.time_fora: p for p in league.resultados.get(rodada, [])}
    return [
        (casa, fora, partidas.get(f"{casa}|{fora}"))
        for casa, fora in (league.calendario[rodada - 1] if rodada <= len(league.calendario) else [])
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
    temporada = piramide.temporada if piramide else (league.temporada if league else 2026)
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


def linhas_classificacao(divisao: str, fase_idx: int = 0, grupo: str | None = None) -> list[dict]:
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
        f'<span class="zona" style="background:{cor}"></span> {txt}' for cor, txt in itens
    )
    return f'<div class="legenda" style="margin-top:.8rem">{spans}</div>'


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

    # banco completo (156 clubes): as quatro divisões jogam ao mesmo tempo
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
    clubes_divisao = [t for t in banco if t.divisao == divisao]
    with col_info:
        st.caption(
            f"**{NOMES_DIVISAO.get(divisao, divisao)}** — {len(clubes_divisao)} clubes. "
            "As quatro divisões jogam juntas: você disputa a sua e acompanha "
            "as demais em Calendário e Classificações."
        )

    secao("Escolha seu time para começar a temporada", NOMES_DIVISAO.get(divisao, divisao))

    custom = [
        t
        for t in st.session_state.get("clubes_custom", [])
        if t.nome not in {x.nome for x in banco}
    ]
    times = list(clubes_divisao)
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
                        <div class="club-top">
                            <div class="club-crest"
                                 style="--c1:{time.cor_primaria};--c2:{time.cor_secundaria}">
                                {escudo_img(time.sigla, time.escudo_emoji, "escudo-crest")}
                            </div>
                            <div>
                                <div class="club-name">{time.nome}</div>
                                <div class="club-meta">📍 {time.cidade}/{time.estado}</div>
                            </div>
                        </div>
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
                    # a temporada inteira entra no jogo: banco + clubes criados
                    elenco = banco + custom
                    st.session_state.times = elenco
                    st.session_state.meu_time = time.nome
                    try:
                        piramide = Piramide(elenco)
                    except ValueError as erro:
                        st.error(f"❌ {erro}")
                        st.stop()
                    st.session_state.piramide = piramide
                    st.session_state.league = piramide.league_de(time.nome) or League(
                        elenco
                    )
                    st.session_state.market = Market(elenco)
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

    pos_sidebar = posicao_na_tabela(league, time.nome)
    posicao_html = f' <span class="pill p-ok">{pos_sidebar}º lugar</span>' if pos_sidebar else ""

    with st.sidebar:
        st.markdown(
            f"""
        <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.4rem;">
            <div class="club-crest" style="--c1:{time.cor_primaria};--c2:{time.cor_secundaria}">
                {escudo_img(time.sigla, time.escudo_emoji, "escudo-crest")}
            </div>
            <div>
                <div style="font-family:var(--font-display);font-weight:800;font-size:1.15rem;line-height:1.1">
                    {time.nome}
                </div>
                <div class="club-meta">Temporada {league.temporada} · {time.cidade}/{time.estado}</div>
                <div style="margin-top:.3rem">
                    <span class="pill p-info">Série {divisao_do_jogador()}</span>{posicao_html}
                </div>
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
            "classificacao": "🏆 Classificações",
            "calendario": "📅 Calendário",
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
        <h1 style="font-size:1.8rem">🏠 {escudo_img(time.sigla, time.escudo_emoji)} {time.nome}</h1>
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

    piramide_painel = get_piramide()
    if piramide_painel is not None:
        proximo = piramide_painel.proximo_jogo(time.nome)
        if proximo is not None:
            competicao, rodada_prox, casa_prox, fora_prox = proximo
            adversario_prox = fora_prox if casa_prox == time.nome else casa_prox
            st.caption(
                f"🎯 **{competicao}** — "
                f"{'🏠 em casa' if casa_prox == time.nome else '✈️ fora de casa'} "
                f"contra **{adversario_prox}** (rodada {rodada_prox} de "
                f"{piramide_painel.total_rodadas_global})"
            )

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
                f"<td>{escudo_img(t.sigla, t.escudo_emoji)} {t.sigla}</td>"
                f"<td class='num'><b>{t.pontos}</b></td>"
                f"<td class='num'>{t.vitorias}V {t.empates}E {t.derrotas}D</td></tr>"
            )
        if pos > 8:
            linhas.append(
                f"<tr class='me'><td class='num'>{pos}º</td><td></td>"
                f"<td>{escudo_img(time.sigla, time.escudo_emoji)} {time.sigla}</td>"
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
        <h1 style="font-size:1.8rem">👥 Elenco · {escudo_img(time.sigla, time.escudo_emoji)} {time.nome}</h1>
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
        <h1 style="font-size:1.8rem">📋 Tática · {escudo_img(time.sigla, time.escudo_emoji)} {time.nome}</h1>
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


def _card_resultado(partida: Partida, time: Time, rotulo: str) -> None:
    """Cartão de resultado de um jogo do clube do jogador."""
    meus = (
        partida.gols_casa if partida.time_casa == time.nome else partida.gols_fora
    )
    deles = (
        partida.gols_fora if partida.time_casa == time.nome else partida.gols_casa
    )
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
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        simular = st.button(
            "⚽ SIMULAR RODADA", type="primary", use_container_width=True
        )
    if simular:
        with st.spinner("⚽ Simulando a rodada..."):
            if piramide is not None:
                jogos = piramide.simular_rodada(time.nome)
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
            else:
                jogos_div = league.simular_rodada(time.nome)
                minha_divisao = divisao_do_jogador()
                st.session_state.ultimo_resultado = jogos_div
                st.session_state.rodadas_simuladas = {
                    minha_divisao: league.rodada_atual
                }
                st.session_state.ultima_rodada = [
                    (NOMES_DIVISAO.get(minha_divisao, "Campeonato"), partida)
                    for partida in jogos_div
                    if time.nome in (partida.time_casa, partida.time_fora)
                ]
        st.rerun()

    meus_jogos = st.session_state.get("ultima_rodada") or []
    if meus_jogos:
        secao("Seus jogos da rodada", f"Rodada {rodada_global - 1}")
        for rotulo, partida in meus_jogos:
            _card_resultado(partida, time, rotulo)

    outros = [
        partida
        for partida in (st.session_state.get("ultimo_resultado") or [])
        if time.nome not in (partida.time_casa, partida.time_fora)
    ]
    if outros:
        secao("Outros resultados", NOMES_DIVISAO.get(divisao_do_jogador(), "Divisão"))
        for partida in outros:
            st.markdown(
                f'<div class="res">⚽ <span>{escudo_img(sigla_de(partida.time_casa))} '
                f"<b>{partida.time_casa}</b></span>"
                f"<span class='res-score'>{partida.gols_casa} x {partida.gols_fora}</span>"
                f'<span style="margin-left:auto"><b>{partida.time_fora}</b> '
                f"{escudo_img(sigla_de(partida.time_fora))}</span></div>",
                unsafe_allow_html=True,
            )

    outras = [d for d in divisoes_da_temporada() if d != divisao_do_jogador()]
    pendentes = [d for d in outras if rodada_de(d) > 0]
    if pendentes:
        resumo_divisoes = " · ".join(
            f"**{NOMES_DIVISAO.get(d, d)}** rodada {rodada_de(d)}/{total_rodadas_de(d)}"
            for d in pendentes
        )
        st.caption(f"🌎 Também na temporada: {resumo_divisoes}")


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

    st.markdown(
        '<div class="tl">' + "".join(itens) + "</div>", unsafe_allow_html=True
    )


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
    for regra in (piramide.regulamento(minha) if piramide is not None else []):
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
            st.success(
                f"🏆 Campeão da Copa do Brasil: **{copa.campeao.nome}**"
            )
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


# ============================================================
# CLASSIFICAÇÃO
# ============================================================
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
        st.info(
            "A Copa do Brasil não foi montada nesta temporada (poucos clubes)."
        )
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
        (jogo.time_casa, jogo.time_fora)
        for jogo in jogos
        if fase.nome != "Final"
    ]
    if fase.nome == "Final" and not pares and len(torneio.fases) >= 2:
        finalistas = torneio.fases[-2].vencedores
        if len(finalistas) == 2:
            pares = [(finalistas[0].nome, finalistas[1].nome)]
    for casa, fora in pares:
        gols_casa = gols_fora = 0
        partidas = [
            jogo
            for jogo in jogos
            if {jogo.time_casa, jogo.time_fora} == {casa, fora}
        ]
        for jogo in partidas:
            if jogo.time_casa == casa:
                gols_casa += jogo.gols_casa
                gols_fora += jogo.gols_fora
            else:
                gols_casa += jogo.gols_fora
                gols_fora += jogo.gols_casa
        prossegue = bool(vencedores) and (
            (casa in vencedores) or (fora in vencedores)
        )
        cls_c = (
            "v"
            if casa in vencedores
            else ("d" if prossegue or fase.concluida else "")
        )
        cls_f = (
            "v"
            if fora in vencedores
            else ("d" if prossegue or fase.concluida else "")
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
        format_func=lambda k: next(
            (t.nome for t in torneios if t.chave == k), str(k)
        ),
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
        format_func=lambda k: next(
            (t.nome for t in torneios if t.chave == k), str(k)
        ),
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
        piramide_atual.rodada_global if piramide_atual is not None else league.rodada_atual
    )

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">🏆 Classificações</h1>
        <p>Temporada {league.temporada} · {len(divisoes)} divisões ·
        rodada geral {rodada_geral}</p>
    </div>
    """,
        unsafe_allow_html=True,
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
                st.markdown(
                    tabela_classificacao(divisao, time), unsafe_allow_html=True
                )
                st.markdown(legenda_zonas(divisao), unsafe_allow_html=True)
                continue

            for i, (nome_fase, fase) in enumerate(fases):
                if fase.tipo == "mata":
                    secao(nome_fase, f"{len(fase.pares)} confrontos")
                    st.markdown(
                        _resultado_mata(divisao, fase), unsafe_allow_html=True
                    )
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
                            temporada.tabela(fase) if temporada else linhas_classificacao(divisao),
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
                piramide_atual.regulamento(divisao) if piramide_atual is not None else []
            )
            if regras:
                with st.expander("📖 Regulamento da divisão"):
                    st.markdown(
                        "".join(f"- {regra}\n" for regra in regras)
                    )

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
                            {escudo_img(clube.sigla, clube.escudo_emoji, "escudo-crest")}
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
                times_por_grupo = g2.number_input(
                    "Times por grupo", 2, 48, 5, step=1
                )
                n_grupos = 4
            classificados = g1.number_input(
                "Classificados por grupo", 1, 8, 2, step=1
            )
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


# ============================================================
# CALENDÁRIO
# ============================================================
def tela_calendario():
    time = get_meu_time()
    divisoes = divisoes_da_temporada()
    minha = divisao_do_jogador()
    piramide = get_piramide()

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">📅 Calendário</h1>
        <p>Temporada {piramide.temporada if piramide else st.session_state.league.temporada} ·
        uma rodada por semana · todas as divisões</p>
    </div>
    """,
        unsafe_allow_html=True,
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
                extra = (
                    f"👥 {partida.publico:,}"
                    if partida.publico
                    else ""
                )
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
                st.success(
                    f"🏆 Campeão da Copa do Brasil: **{copa.campeao.nome}**"
                )

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
            if (
                piramide_atual.supercopa is not None
                and time.nome
                in (
                    piramide_atual.supercopa.time_casa,
                    piramide_atual.supercopa.time_fora,
                )
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
            rodada_global = rodada + (
                deslocamento if competicao == "divisao" else 0
            )
            data = (
                data_da_rodada(minha, rodada)
                if competicao == "divisao"
                else data_global(rodada)
            )
            em_casa = casa == time.nome
            adversario = fora if em_casa else casa
            if partida is None:
                tag, cls, placar = "–", "e", "<span style='color:var(--ink-3)'>a jogar</span>"
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


# ============================================================
# RESULTADOS
# ============================================================
def tela_resultados():
    time = get_meu_time()
    divisoes = divisoes_da_temporada()

    st.markdown(
        f"""
    <div class="hero" style="padding:1.4rem 1.6rem">
        <h1 style="font-size:1.8rem">📊 Resultados por Rodada</h1>
        <p>Placares de todas as divisões na temporada {st.session_state.league.temporada}</p>
    </div>
    """,
        unsafe_allow_html=True,
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
                <div class="res" style="{ 'border-color:var(--brand);background:#F2FBF5' if destaque else '' }">
                    <span style="{ 'font-weight:800' if destaque else '' }">⚽ {casa}
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
                    <div class="res" style="{ 'border-color:var(--brand);background:#F2FBF5' if destaque else '' }">
                        <span style="{ 'font-weight:800' if destaque else '' }">🏆 {partida.time_casa}
                        <b>{partida.gols_casa} x {partida.gols_fora}</b> {partida.time_fora}</span>
                        <span style="margin-left:auto;color:var(--ink-3);font-size:.78rem">
                            {partida.grupo or 'jogo único'}
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
                piramide_reg.torneio(chave_reg)
                if piramide_reg is not None
                else None
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
                        <div class="res" style="{ 'border-color:var(--brand);background:#F2FBF5' if destaque else '' }">
                            <span style="{ 'font-weight:800' if destaque else '' }">🌎 {partida.time_casa}
                            <b>{partida.gols_casa} x {partida.gols_fora}</b> {partida.time_fora}</span>
                            <span style="margin-left:auto;color:var(--ink-3);font-size:.78rem">
                                {partida.grupo or partida.fase}
                            </span>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )


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
        elif pagina == "calendario":
            tela_calendario()
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
