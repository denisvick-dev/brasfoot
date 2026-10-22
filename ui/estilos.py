"""
CSS e tema do app (identidade visual do Brasfoot).
"""

import streamlit as st


def configurar_pagina() -> None:
    """Configuração da página do Streamlit (precisa ser o primeiro comando st)."""
    st.set_page_config(
        page_title="⚽ Brasfoot Streamlit",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )


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


