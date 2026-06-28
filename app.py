"""
Dashboard Hospitalar — Região de Lisboa
Análise Estatística Avançada · ISCTE · Data Science & Business Analytics
Ricardo Manuel Freire Santos · N.º 143318
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Configuração da página ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Hospitalar · Lisboa",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta e tema ──────────────────────────────────────────────────────────
BG       = "#0d1117"
CARD_BG  = "#141d2d"
CARD_BG2 = "#1a2640"
TEXT     = "#e8ecf4"
MUTED    = "#7a8aaa"
GRID     = "#2a3550"
BLUE     = "#5b8dd9"
CYAN     = "#22d3ee"
GREEN    = "#10b981"
AMBER    = "#f59e0b"
RED      = "#ef4444"
PURPLE   = "#a855f7"
PINK     = "#ec4899"

HOSP_COLORS = {
    "São José":       BLUE,
    "CUF":            GREEN,
    "Santa Maria":    AMBER,
    "Luz":            PURPLE,
    "Beatriz Angelo": RED,
    "Amadora Sintra": CYAN,
}

PALETTE = [BLUE, GREEN, AMBER, RED, PURPLE, CYAN, PINK, "#f97316"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor=CARD_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color=TEXT, family="sans-serif", size=12),
    margin=dict(l=16, r=16, t=80, b=16),
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickcolor=MUTED, color=TEXT, gridcolor=GRID, automargin=True),
    yaxis=dict(gridcolor=GRID, gridwidth=0.6, zeroline=False,
               showline=False, tickcolor=MUTED, color=TEXT, automargin=True),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                font=dict(color=TEXT, size=11)),
    hoverlabel=dict(bgcolor=CARD_BG2, bordercolor=GRID,
                    font=dict(color=TEXT, size=12)),
    title=dict(x=0.01, xanchor="left", y=0.97, yanchor="top",
               font=dict(size=15, color=TEXT)),
    colorway=PALETTE,
)

# CSS global
st.markdown(f"""
<style>
  html, body, [data-testid="stAppViewContainer"] {{
      background-color: {BG};
      color: {TEXT};
  }}
  [data-testid="stSidebar"] {{
      background-color: {CARD_BG};
      border-right: 1px solid {GRID};
  }}
  .metric-card {{
      background: {CARD_BG};
      border: 1px solid {GRID};
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 8px;
  }}
  .metric-label {{
      font-size: 0.72rem;
      font-weight: 600;
      color: {MUTED};
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 4px;
  }}
  .metric-value {{
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.1;
  }}
  .metric-delta {{
      font-size: 0.75rem;
      color: {MUTED};
      margin-top: 3px;
  }}
  .section-title {{
      font-size: 0.68rem;
      font-weight: 700;
      color: {MUTED};
      text-transform: uppercase;
      letter-spacing: 0.12em;
      border-top: 1px solid {GRID};
      padding-top: 8px;
      margin: 16px 0 8px 0;
  }}
  .insight-box {{
      background: {CARD_BG2};
      border-left: 3px solid {BLUE};
      border-radius: 0 8px 8px 0;
      padding: 10px 14px;
      margin: 6px 0;
      font-size: 0.85rem;
      color: {TEXT};
  }}
  .footer {{
      background: {CARD_BG};
      border-top: 1px solid {GRID};
      padding: 20px 32px;
      margin-top: 32px;
      border-radius: 12px;
      font-size: 0.78rem;
      color: {MUTED};
  }}
  .stTabs [data-baseweb="tab-list"] {{
      background: {CARD_BG};
      border-radius: 8px;
      padding: 4px;
      gap: 4px;
  }}
  .stTabs [data-baseweb="tab"] {{
      background: transparent;
      color: {MUTED};
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 500;
  }}
  .stTabs [aria-selected="true"] {{
      background: {BLUE} !important;
      color: white !important;
  }}
  div[data-testid="stExpander"] {{
      background: {CARD_BG};
      border: 1px solid {GRID};
      border-radius: 8px;
  }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────
def kpi(label, value, delta="", color=BLUE):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color}">{value}</div>
        <div class="metric-delta">{delta}</div>
    </div>""", unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)

def chart(fig, caption_text, interpretar_text, dados_text, insight_text=None):
    """Renderiza gráfico com dropdown de interpretação e insights."""
    st.plotly_chart(fig, use_container_width=True, theme=None)
    if caption_text:
        st.caption(caption_text)
    with st.expander("📖 Como interpretar este gráfico"):
        st.markdown(interpretar_text)
    if insight_text:
        with st.expander("💡 Como são gerados estes Insights"):
            st.markdown(insight_text)
    st.markdown("")

def tab_header(audiencia, decisao, janela, dados, glossario_dict=None):
    """Bloco subtil por aba: pills de contexto + expanders de dados e glossário."""
    st.markdown(f"""
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center">
        <span style="font-size:0.72rem;color:{MUTED};margin-right:4px">contexto</span>
        <span style="background:{CARD_BG};border:1px solid {GRID};border-radius:20px;
                     padding:3px 10px;font-size:0.75rem;color:{TEXT};">
            👥 {audiencia}
        </span>
        <span style="background:{CARD_BG};border:1px solid {GRID};border-radius:20px;
                     padding:3px 10px;font-size:0.75rem;color:{TEXT};">
            🎯 {decisao}
        </span>
        <span style="background:{CARD_BG};border:1px solid {GRID};border-radius:20px;
                     padding:3px 10px;font-size:0.75rem;color:{TEXT};">
            🕐 {janela}
        </span>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🗄️ De onde vêm estes dados?"):
            st.markdown(dados)
    if glossario_dict:
        with col2:
            with st.expander("📌 O que significam estes termos?"):
                for termo, definicao in glossario_dict.items():
                    st.markdown(f"**{termo}** — {definicao}")

def apply_layout(fig, title="", legend=None, margin=None):
    """Aplica PLOTLY_LAYOUT sem conflitos de chaves duplicadas."""
    excluir = set()
    if legend is not None:
        excluir.add("legend")
    if margin is not None:
        excluir.add("margin")
    base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in excluir}
    kwargs = dict(**base)
    if title:
        kwargs["title"] = dict(text=title, x=0.01, xanchor="left",
                                y=0.97, yanchor="top",
                                font=dict(size=15, color=TEXT))
    if legend is not None:
        kwargs["legend"] = legend
    if margin is not None:
        kwargs["margin"] = margin
    fig.update_layout(**kwargs)
    return fig

def glossario(termos: dict):
    with st.expander("📌 O que significam estes termos?"):
        for termo, definicao in termos.items():
            st.markdown(f"**{termo}** — {definicao}")


# ── Carregar dados ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_parquet("hospitais_data.parquet")

df_full = load_data()

FAIXA_ORDER   = ['< 50','50-60','60-70','70-80','> 80']
IMC_ORDER     = ['<18.5','18.5-22','22-25','25-28','28-32','32-36','>36']
HOSP_LIST     = sorted(df_full["Hospital"].unique())
COMORB_MAP    = {
    "Fumador":     "Fumador",
    "Diabetes":    "Diabetes",
    "Colesterol":  "Colesterol",
    "INS_Cardiaca":"Ins. Cardíaca",
    "Hepatite_C":  "Hepatite C",
}


# ══════════════════════════════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
PERFIS = {
    "clinico":  {"label": "🩺 Clínico",      "abas": [0, 1]},
    "gestao":   {"label": "📊 Gestão",        "abas": [0, 1, 2]},
    "admin":    {"label": "🔐 Administração", "abas": [0, 1, 2, 3, 4]},
}

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None

if not st.session_state.autenticado:
    st.markdown(f"""
    <div style="max-width:420px;margin:80px auto;background:{CARD_BG};
                border:1px solid {GRID};border-radius:16px;padding:40px;">
        <div style="text-align:center;font-size:2.5rem;margin-bottom:8px">🏥</div>
        <h2 style="text-align:center;color:{TEXT};margin:0 0 4px">Dashboard Hospitalar</h2>
        <p style="text-align:center;color:{MUTED};font-size:0.85rem;margin-bottom:24px">
            Região de Lisboa · Acesso Restrito</p>
    </div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        perfil_sel = st.selectbox("Perfil de acesso",
                                   options=list(PERFIS.keys()),
                                   format_func=lambda x: PERFIS[x]["label"])
        password = st.text_input("Password", type="password")
        if st.button("Entrar", use_container_width=True, type="primary"):
            pwd_correta = st.secrets.get("passwords", {}).get(perfil_sel, "")
            if password == pwd_correta:
                st.session_state.autenticado = True
                st.session_state.perfil = perfil_sel
                st.rerun()
            else:
                st.error("Password incorrecta.")
    st.stop()

perfil      = st.session_state.perfil
abas_acesso = PERFIS[perfil]["abas"]


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:12px 0 8px">
        <div style="font-size:2rem">🏥</div>
        <div style="font-weight:700;color:{TEXT};font-size:1rem">Dashboard Hospitalar</div>
        <div style="color:{MUTED};font-size:0.75rem">Região de Lisboa</div>
    </div>
    <hr style="border-color:{GRID};margin:8px 0">
    """, unsafe_allow_html=True)

    st.markdown(f'<div style="color:{MUTED};font-size:0.72rem;text-transform:uppercase;'
                f'letter-spacing:0.08em;margin-bottom:6px">Perfil activo</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div style="color:{BLUE};font-weight:600;margin-bottom:16px">'
                f'{PERFIS[perfil]["label"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Filtros</div>', unsafe_allow_html=True)

    hosp_sel = st.multiselect("Hospital", options=HOSP_LIST, default=HOSP_LIST)
    sexo_sel = st.multiselect("Sexo", options=["Masculino","Feminino"],
                               default=["Masculino","Feminino"])
    ano_min, ano_max = int(df_full["Ano"].min()), int(df_full["Ano"].max())
    ano_sel = st.slider("Ano", min_value=ano_min, max_value=ano_max,
                         value=(ano_min, ano_max))
    tipo_adm_sel = st.multiselect("Tipo de Admissão",
                                   options=["Urgente","Programada"],
                                   default=["Urgente","Programada"])

    st.markdown('<div class="section-title">Sessão</div>', unsafe_allow_html=True)
    if st.button("Terminar sessão", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.perfil = None
        st.rerun()

# Aplicar filtros
df = df_full.copy()
if hosp_sel:
    df = df[df["Hospital"].isin(hosp_sel)]
if sexo_sel:
    df = df[df["Sexo_Label"].isin(sexo_sel)]
df = df[(df["Ano"] >= ano_sel[0]) & (df["Ano"] <= ano_sel[1])]
if tipo_adm_sel:
    df = df[df["TipodeADM_Label"].isin(tipo_adm_sel)]

n_total = len(df)


# ── Header ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{CARD_BG};border:1px solid {GRID};border-radius:12px;
            padding:16px 24px;margin-bottom:20px;display:flex;
            align-items:center;justify-content:space-between;">
    <div>
        <div style="font-size:1.4rem;font-weight:800;color:{TEXT}">
            🏥 Dashboard Hospitalar · Região de Lisboa
        </div>
        <div style="color:{MUTED};font-size:0.82rem;margin-top:2px">
            Análise Estatística Avançada · ISCTE · Data Science & Business Analytics
        </div>
    </div>
    <div style="text-align:right">
        <div style="color:{BLUE};font-weight:600;font-size:0.85rem">
            n = {n_total} doentes visíveis
        </div>
        <div style="color:{MUTED};font-size:0.75rem">
            {PERFIS[perfil]["label"]} · 6 Hospitais · 2011–2025
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABAS
# ══════════════════════════════════════════════════════════════════════════════
NOMES_ABAS = [
    "📊 Visão Geral",
    "🫀 Perfil Clínico",
    "🏥 Por Hospital",
    "💉 Tratamento",
    "⚠️ Risco & Mortalidade",
]
abas_visiveis = [NOMES_ABAS[i] for i in abas_acesso]
tabs = st.tabs(abas_visiveis)
tab_map = {i: tabs[abas_acesso.index(i)] for i in abas_acesso}


# ══════════════════════════════════════════════════════════════════════════════
# ABA 0 — VISÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════
with tab_map[0]:

    tab_header(
        audiencia="Todos os perfis (Clínico, Gestão, Administração)",
        decisao="Compreender o volume, composição e distribuição da população hospitalar",
        janela="2011–2025 · Dados históricos de internamento",
        dados="Base de dados **Hospitais.xlsx** · 449 doentes · 6 hospitais da Região de Lisboa · "
              "variáveis demográficas, administrativas e clínicas após limpeza e correcção de 4 anomalias.",
        glossario_dict={
            "Admissão Urgente": "Doente internado por via de urgência, sem agendamento prévio (TipodeADM = U).",
            "PPP": "Parceria Público-Privada — hospital gerido por entidade privada com financiamento público.",
            "Faixa Etária": "Intervalo de 10 anos que agrupa doentes com idades semelhantes para análise comparativa.",
            "Internamento": "Período de permanência do doente numa unidade hospitalar, medido em dias.",
        },
    )
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi("Total Doentes", f"{n_total}", "amostra filtrada", BLUE)
    with c2:
        kpi("Idade Média", f"{df['Idade'].mean():.1f}",
            f"anos · {df['Idade'].min():.0f}–{df['Idade'].max():.0f}", AMBER)
    with c3:
        kpi("Internamento Médio", f"{df['Dias_Inter'].mean():.1f}",
            "dias · mediana " + f"{df['Dias_Inter'].median():.0f}", GREEN)
    with c4:
        urgentes = (df["TipodeADM_Label"] == "Urgente").mean() * 100
        kpi("Admissão Urgente", f"{urgentes:.1f}%",
            f"{(df['TipodeADM_Label']=='Urgente').sum()} doentes", RED)
    with c5:
        kpi("Hospitais", f"{df['Hospital'].nunique()}",
            "unidades · Região Lisboa", PURPLE)

    st.markdown('<div class="section-title">Distribuição Demográfica</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        # Faixas etárias
        fe = df.groupby("Faixa_Etaria", observed=False).size().reset_index(name="n")
        fe["Faixa_Etaria"] = pd.Categorical(fe["Faixa_Etaria"], categories=FAIXA_ORDER, ordered=True)
        fe = fe.sort_values("Faixa_Etaria")
        fig = px.bar(fe, x="Faixa_Etaria", y="n",
                     color="Faixa_Etaria",
                     color_discrete_sequence=PALETTE,
                     text="n")
        fig.update_traces(textposition="outside", textfont_color=TEXT,
                          marker_line_width=0)
        apply_layout(fig, "Distribuição por Faixa Etária",
                     margin=dict(l=16, r=16, t=80, b=16))
        fig.update_xaxes(categoryorder="array", categoryarray=FAIXA_ORDER)
        chart(fig,
              "Número de doentes por grupo etário.",
              "Cada barra representa o total de doentes numa faixa etária. "
              "Faixas mais altas indicam maior representação na amostra. "
              "Uma concentração nas faixas 70-80 e >80 é típica de populações hospitalares geriátricas.",
              "Calculado a partir da variável **Idade** da base de dados Hospitais.xlsx, "
              "agrupada em intervalos de 10 anos. Os filtros laterais aplicam-se.",
              "A faixa etária dominante reflecte o perfil geriátrico da população internada, "
              "com implicações directas na mortalidade esperada e duração do internamento.")

    with col2:
        # Sexo donut
        sexo = df["Sexo_Label"].value_counts().reset_index()
        sexo.columns = ["Sexo","n"]
        fig2 = go.Figure(go.Pie(
            labels=sexo["Sexo"], values=sexo["n"],
            hole=0.7, marker_colors=[BLUE, PINK],
            textinfo="percent", textfont_color=TEXT,
            hovertemplate="<b>%{label}</b><br>n=%{value}<br>%{percent}<extra></extra>",
        ))
        apply_layout(fig2, "Distribuição por Sexo",
                     margin=dict(l=16, r=16, t=80, b=16))
        chart(fig2,
              "Proporção masculino/feminino na amostra filtrada.",
              "O gráfico de anel mostra a divisão por sexo. "
              "O valor central corresponde ao grupo maioritário. "
              "Uma divisão equilibrada sugere ausência de viés de selecção por sexo.",
              "Variável **Sexo** da base de dados (M/F). "
              "O registo com valor 'N' foi corrigido para 'M' na fase de limpeza.",
              None)

    with col3:
        # Pub/Priv donut
        pp = df["HospPP"].value_counts().reset_index()
        pp.columns = ["Tipo","n"]
        fig3 = go.Figure(go.Pie(
            labels=pp["Tipo"], values=pp["n"],
            hole=0.7, marker_colors=[GREEN, BLUE, AMBER],
            textinfo="percent", textfont_color=TEXT,
            hovertemplate="<b>%{label}</b><br>n=%{value}<br>%{percent}<extra></extra>",
        ))
        apply_layout(fig3, "Tipo de Hospital",
                     margin=dict(l=16, r=16, t=80, b=16))
        chart(fig3,
              "Proporção de doentes em hospitais Públicos, Privados e PPP.",
              "Mostra a distribuição dos doentes pelos três tipos de gestão hospitalar. "
              "Uma maioria em hospitais privados pode reflectir a composição da rede hospitalar de Lisboa.",
              "Variável **HospPP** da base de dados (Público/Privado/PPP).",
              None)

    st.markdown('<div class="section-title">Evolução Temporal</div>',
                unsafe_allow_html=True)

    col4, col5 = st.columns([3, 2])

    with col4:
        # Internamentos por ano e sexo
        ys = df.groupby(["Ano","Sexo_Label"]).size().reset_index(name="n")
        fig4 = px.line(ys, x="Ano", y="n", color="Sexo_Label",
                       color_discrete_map={"Masculino": BLUE, "Feminino": PINK},
                       markers=True, line_shape="spline")
        fig4.update_traces(line_width=2.5, marker_size=6)
        apply_layout(fig4, "Internamentos por Ano e Sexo (2011–2025)",
                     legend=dict(orientation="h", yanchor="top", y=1.18,
                                 xanchor="left", x=-0.02,
                                 bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                 font=dict(color=TEXT, size=11)),
                     margin=dict(l=16, r=16, t=100, b=16))
        chart(fig4,
              "Evolução anual do número de internamentos, diferenciada por sexo.",
              "Cada linha representa a evolução temporal de um sexo. "
              "Picos ou quedas acentuadas podem reflectir eventos externos (ex: pandemia, políticas de saúde). "
              "A diferença entre as duas linhas indica assimetria de género nos internamentos.",
              "Variáveis **Ano** e **Sexo** da base de dados. "
              "O período cobre 2011 a 2025 com dados reais de internamento.",
              "O pico em 2011-2012 seguido de queda acentuada é consistente com o período de "
              "austeridade em Portugal. A recuperação a partir de 2023 sugere normalização.")

    with col5:
        # Doentes por hospital
        hb = df.groupby("Hospital").size().reset_index(name="n").sort_values("n", ascending=True)
        hb["cor"] = hb["Hospital"].map(HOSP_COLORS)
        fig5 = px.bar(hb, y="Hospital", x="n", orientation="h",
                      color="Hospital",
                      color_discrete_map=HOSP_COLORS,
                      text="n")
        fig5.update_traces(textposition="outside", textfont_color=TEXT,
                           marker_line_width=0)
        apply_layout(fig5, "Doentes por Hospital",
                     margin=dict(l=16, r=16, t=80, b=16))
        fig5.update_layout(showlegend=False)
        chart(fig5,
              "Volume de internamentos por unidade hospitalar.",
              "Cada barra representa o número total de doentes internados nesse hospital. "
              "Hospitais com barras mais longas têm maior volume, o que pode influenciar "
              "a representatividade das análises subsequentes.",
              "Variável **Hospital** da base de dados. "
              "Os 6 hospitais pertencem à região metropolitana de Lisboa.",
              None)

    # Mapa
    st.markdown('<div class="section-title">Distribuição Geográfica</div>',
                unsafe_allow_html=True)

    coords = {
        "São José":       (38.7060, -9.1360),
        "CUF":            (38.7260, -9.1620),
        "Santa Maria":    (38.7460, -9.1600),
        "Luz":            (38.7420, -9.1460),
        "Beatriz Angelo": (38.7970, -9.1010),
        "Amadora Sintra": (38.7510, -9.2280),
    }
    map_df = df.groupby("Hospital").agg(
        n=("ID_Doente","count"),
        mort=("MortEsperada_Pct","mean"),
        dias=("Dias_Inter","mean"),
    ).reset_index()
    map_df["lat"] = map_df["Hospital"].map(lambda h: coords.get(h,(38.72,-9.14))[0])
    map_df["lon"] = map_df["Hospital"].map(lambda h: coords.get(h,(38.72,-9.14))[1])
    map_df["cor"] = map_df["Hospital"].map(HOSP_COLORS)
    map_df["mort"] = map_df["mort"].round(1)
    map_df["dias"] = map_df["dias"].round(1)

    fig_map = px.scatter_mapbox(
        map_df, lat="lat", lon="lon",
        size="n", color="Hospital",
        color_discrete_map=HOSP_COLORS,
        hover_name="Hospital",
        hover_data={"n": True, "mort": True, "dias": True,
                    "lat": False, "lon": False},
        size_max=50,
        zoom=11, center={"lat": 38.73, "lon": -9.15},
        mapbox_style="carto-darkmatter",
        labels={"n":"Doentes","mort":"Mort. Esp. (%)","dias":"Dias Inter."},
    )
    fig_map.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font=dict(color=TEXT),
        margin=dict(l=0, r=0, t=60, b=0),
        height=420,
        title=dict(text="Distribuição Geográfica dos Hospitais — Região de Lisboa",
                   x=0.01, font=dict(size=15, color=TEXT)),
        hoverlabel=dict(bgcolor=CARD_BG2, font=dict(color=TEXT)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
    )
    chart(fig_map,
          "Tamanho da bolha proporcional ao n.º de doentes. Hover para detalhes por hospital.",
          "Cada bolha representa um hospital. O tamanho é proporcional ao volume de internamentos. "
          "Hospitais próximos podem partilhar população, o que é relevante para análise de referenciação.",
          "Coordenadas geográficas aproximadas dos hospitais da região de Lisboa. "
          "Volume de doentes calculado a partir dos filtros activos.",
          None)


# ══════════════════════════════════════════════════════════════════════════════
# ABA 1 — PERFIL CLÍNICO
# ══════════════════════════════════════════════════════════════════════════════
with tab_map[1]:

    tab_header(
        audiencia="Clínico · Gestão · Administração",
        decisao="Identificar o perfil de risco clínico da população internada e priorizar intervenções",
        janela="Momento de internamento · Dados transversais por doente",
        dados="Variáveis clínicas da base **Hospitais.xlsx**: Fumador, Diabetes, Colesterol, INS_Cardiaca, "
              "Hepatite_C, Grau_Dor, COVID_M1/M2/M3, IMC, Freq_Resp, pH, pO2_AntesTrat, Glicemia_AntesTrat.",
        glossario_dict={
            "Comorbilidade": "Condição clínica adicional presente no doente para além da patologia principal que motivou o internamento.",
            "Mortalidade Esperada": "Score contínuo [0–1] que estima a probabilidade de morte do doente. Aqui expresso em percentagem.",
            "IMC": "Índice de Massa Corporal = Peso (kg) / Altura² (m). Normal: 18.5–25; Pré-obeso: 25–30; Obeso: >30.",
            "Grau de Dor": "Escala numérica de 0 (sem dor) a 10 (dor máxima) reportada pelo doente no momento do internamento.",
            "COVID M1/M2/M3": "Estado serológico COVID em três momentos distintos de avaliação (P=Positivo, N=Negativo).",
            "Mortalidade Alta": f"Score de MortEsperada ≥ percentil 75 da amostra.",
        },
    )

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        mort_m = df["MortEsperada_Pct"].mean()
        kpi("Mort. Esperada Média", f"{mort_m:.1f}%",
            "score contínuo 0–100%", RED)
    with c2:
        pct_fum = (df["Fumador"]=="S").mean()*100
        kpi("Fumadores", f"{pct_fum:.1f}%",
            f"{(df['Fumador']=='S').sum()} doentes", AMBER)
    with c3:
        pct_diab = (df["Diabetes"]=="S").mean()*100
        kpi("Diabetes", f"{pct_diab:.1f}%",
            f"{(df['Diabetes']=='S').sum()} doentes", PURPLE)
    with c4:
        pct_ins = (df["INS_Cardiaca"]=="S").mean()*100
        kpi("Ins. Cardíaca", f"{pct_ins:.1f}%",
            f"{(df['INS_Cardiaca']=='S').sum()} doentes", BLUE)
    with c5:
        grau_dor = df["Grau_Dor"].mean()
        kpi("Grau de Dor Médio", f"{grau_dor:.1f}",
            "escala 0–10", CYAN)

    st.markdown('<div class="section-title">Comorbilidades e Parâmetros</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        # Comorbilidades
        comorb_data = []
        for col_name, label in COMORB_MAP.items():
            n_sim = (df[col_name] == "S").sum()
            comorb_data.append({"Comorbilidade": label, "n": n_sim})
        cdf = pd.DataFrame(comorb_data).sort_values("n")
        fig = px.bar(cdf, y="Comorbilidade", x="n", orientation="h",
                     color="Comorbilidade",
                     color_discrete_sequence=PALETTE,
                     text="n")
        fig.update_traces(textposition="outside", textfont_color=TEXT,
                          marker_line_width=0)
        apply_layout(fig, "Distribuição de Comorbilidades na Amostra",
                     margin=dict(l=16, r=16, t=80, b=16))
        fig.update_layout(showlegend=False)
        chart(fig,
              "Número de doentes com cada condição clínica associada (n.º absoluto).",
              "Cada barra representa o número total de doentes com essa comorbilidade. "
              "Quanto maior a barra, mais prevalente é a condição. "
              "O tabagismo como comorbilidade dominante é consistente com a literatura sobre populações hospitalizadas.",
              "Variáveis **Fumador**, **Diabetes**, **Colesterol**, **INS_Cardiaca** e **Hepatite_C** "
              "da base de dados (valores S/N). Frequência absoluta de doentes com valor 'S'.",
              "Uma prevalência de tabagismo acima de 75% é clinicamente relevante pois está "
              "associada a maior risco de complicações respiratórias e cardiovasculares.")

    with col2:
        # Grau de Dor
        dor = df["Grau_Dor"].value_counts().sort_index().reset_index()
        dor.columns = ["Grau","n"]
        dor_colors = [CYAN, BLUE, BLUE, PURPLE, PURPLE,
                      AMBER, AMBER, RED, RED, RED, RED]
        fig2 = px.bar(dor, x="Grau", y="n",
                      color="Grau",
                      color_discrete_sequence=dor_colors,
                      text="n")
        fig2.update_traces(textposition="outside", textfont_color=TEXT,
                           marker_line_width=0)
        apply_layout(fig2, "Distribuição do Grau de Dor (Escala 0–10)",
                     margin=dict(l=16, r=16, t=80, b=16))
        fig2.update_layout(showlegend=False)
        chart(fig2,
              "Frequência de doentes por nível de dor reportado (0=sem dor, 10=dor máxima).",
              "O gradiente de cor (azul→vermelho) acompanha a intensidade da dor. "
              "Uma distribuição uniforme indica ausência de concentração num nível específico, "
              "sugerindo heterogeneidade clínica na amostra.",
              "Variável **Grau_Dor** da base de dados (escala discreta 0–10).",
              None)

    st.markdown('<div class="section-title">Evolução COVID e IMC</div>',
                unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        # COVID evolução
        covid_data = []
        for momento, col_covid in [("M1","COVID_M1"),("M2","COVID_M2"),("M3","COVID_M3")]:
            for status in ["P","N"]:
                n = (df[col_covid] == status).sum()
                covid_data.append({"Momento": momento, "Status": "Positivo" if status=="P" else "Negativo", "n": n})
        cov_df = pd.DataFrame(covid_data)
        fig3 = px.bar(cov_df, x="Momento", y="n", color="Status",
                      color_discrete_map={"Positivo": RED, "Negativo": GREEN},
                      barmode="stack", text="n")
        fig3.update_traces(textposition="inside", textfont_color="white",
                           marker_line_width=0)
        apply_layout(fig3, "Evolução do Estado COVID (M1 → M2 → M3)",
                     legend=dict(orientation="h", yanchor="top", y=1.18,
                                 xanchor="left", x=-0.02,
                                 bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                 font=dict(color=TEXT, size=11)),
                     margin=dict(l=16, r=16, t=100, b=16))
        chart(fig3,
              "Proporção de doentes COVID positivo (P) e negativo (N) em cada momento de observação.",
              "Barras empilhadas mostram a composição de cada momento. "
              "Um aumento dos positivos ao longo dos momentos indica progressão da infeção na amostra. "
              "M1=primeiro momento, M2=segundo, M3=terceiro momento de avaliação.",
              "Variáveis **COVID_M1**, **COVID_M2** e **COVID_M3** da base de dados (P=positivo, N=negativo).",
              "A progressão crescente de positivos ao longo dos três momentos é consistente "
              "com a natureza evolutiva da infeção por COVID-19 em contexto hospitalar.")

    with col4:
        # IMC por Fumador
        imc_df = df[df["IMC_Categoria"] != "nan"].copy()
        imc_df["IMC_Categoria"] = pd.Categorical(imc_df["IMC_Categoria"],
                                                   categories=IMC_ORDER, ordered=True)
        imc_g = imc_df.groupby(["IMC_Categoria","Fumador_Label"],
                                observed=True).size().reset_index(name="n")
        fig4 = px.bar(imc_g, x="IMC_Categoria", y="n", color="Fumador_Label",
                      color_discrete_map={"Fumador": RED, "Não Fumador": BLUE},
                      barmode="stack", text="n")
        fig4.update_traces(textposition="inside", textfont_color="white",
                           marker_line_width=0)
        apply_layout(fig4, "Distribuição do IMC por Hábito Tabágico",
                     legend=dict(orientation="h", yanchor="top", y=1.18,
                                 xanchor="left", x=-0.02,
                                 bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                 font=dict(color=TEXT, size=11)),
                     margin=dict(l=16, r=16, t=100, b=16))
        fig4.update_xaxes(categoryorder="array", categoryarray=IMC_ORDER)
        chart(fig4,
              "Distribuição do IMC por categoria, diferenciada por hábito tabágico.",
              "Cada barra representa uma categoria de IMC. A cor diferencia fumadores de não fumadores. "
              "Se os fumadores dominam todas as categorias é porque representam 77% da amostra.",
              "Variáveis **IMC** (agrupado em 7 categorias) e **Fumador** (S/N) da base de dados.",
              None)

    # Parallel Categories
    st.markdown('<div class="section-title">Relações entre Variáveis Qualitativas</div>',
                unsafe_allow_html=True)
    par_df = df[["Fumador_Label","Diabetes","Colesterol","MortAlta"]].copy()
    par_df["Mortalidade"] = par_df["MortAlta"].map({1:"Alta","0":"Baixa",0:"Baixa"})
    par_df["Colesterol_L"] = par_df["Colesterol"].map({"S":"Com Colesterol","N":"Sem Colesterol"})
    par_df["Diabetes_L"] = par_df["Diabetes"].map({"S":"Com Diabetes","N":"Sem Diabetes"})
    fig_par = px.parallel_categories(
        par_df,
        dimensions=["Fumador_Label","Diabetes_L","Colesterol_L","Mortalidade"],
        color=par_df["MortAlta"],
        color_continuous_scale=[[0, BLUE],[1, RED]],
        labels={"Fumador_Label":"Tabagismo","Diabetes_L":"Diabetes",
                "Colesterol_L":"Colesterol","Mortalidade":"Mort. Esperada"},
    )
    fig_par.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, size=11),
        margin=dict(l=16, r=16, t=80, b=16),
        title=dict(text="Fluxo de Comorbilidades → Mortalidade (Parallel Categories)",
                   x=0.01, font=dict(size=15, color=TEXT)),
        coloraxis_showscale=False,
    )
    chart(fig_par,
          "Fluxo de doentes através de combinações de comorbilidades até ao nível de mortalidade esperada.",
          "Cada linha vertical é uma dimensão. As faixas horizontais representam fluxos de doentes. "
          "Linhas vermelhas indicam doentes com mortalidade esperada alta (≥ Q3). "
          "Combinações que concentram mais linhas vermelhas são perfis de maior risco.",
          "Variáveis **Fumador**, **Diabetes**, **Colesterol** e **MortEsperada** da base de dados. "
          "Mortalidade Alta = score ≥ percentil 75 da amostra.",
          "O gráfico permite identificar trajectórias de risco: por exemplo, "
          "fumadores com diabetes e colesterol tendem a concentrar maior mortalidade esperada.")

    # Radar
    st.markdown('<div class="section-title">Perfis Clínicos</div>',
                unsafe_allow_html=True)
    from sklearn.preprocessing import MinMaxScaler
    radar_vars = ["Freq_Resp","pH","pO2_AntesTrat","IMC","Glicemia_AntesTrat"]
    radar_labels = ["Freq. Resp.","pH","pO₂ Antes","IMC","Glicemia"]
    radar_df = df.groupby("TipodeDoente_Label")[radar_vars].mean().reset_index()
    scaler = MinMaxScaler()
    radar_df[radar_vars] = scaler.fit_transform(radar_df[radar_vars])

    fig_radar = go.Figure()
    cores_radar = [BLUE, AMBER]
    fill_radar  = ["rgba(91,141,217,0.2)", "rgba(245,158,11,0.2)"]
    for i, row in radar_df.iterrows():
        vals = list(row[radar_vars]) + [row[radar_vars[0]]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals,
            theta=radar_labels + [radar_labels[0]],
            fill="toself",
            name=str(row["TipodeDoente_Label"]),
            line_color=cores_radar[i % len(cores_radar)],
            fillcolor=fill_radar[i % len(fill_radar)],
        ))
    fig_radar.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font=dict(color=TEXT),
        polar=dict(
            bgcolor=CARD_BG,
            radialaxis=dict(visible=True, range=[0,1], color=MUTED, gridcolor=GRID),
            angularaxis=dict(color=TEXT, gridcolor=GRID),
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
        margin=dict(l=16, r=16, t=80, b=16),
        title=dict(text="Perfis Clínicos Médios por Tipo de Doente (normalizado)",
                   x=0.01, font=dict(size=15, color=TEXT)),
    )
    chart(fig_radar,
          "Comparação de perfis clínicos médios normalizados [0,1] por tipo de doente.",
          "Cada eixo representa uma variável clínica normalizada. "
          "Quanto mais afastado do centro, maior o valor médio relativo. "
          "A área maior indica um perfil clínico mais comprometido nessas dimensões.",
          "Variáveis **Freq_Resp**, **pH**, **pO2_AntesTrat**, **IMC** e **Glicemia_AntesTrat** "
          "normalizadas com MinMaxScaler. Agrupamento por **TipodeDoente**.",
          None)


# ══════════════════════════════════════════════════════════════════════════════
# ABA 2 — POR HOSPITAL
# ══════════════════════════════════════════════════════════════════════════════
if 2 in abas_acesso:
    with tab_map[2]:

        tab_header(
            audiencia="Gestão · Administração",
            decisao="Comparar desempenho entre hospitais e identificar unidades com maior risco ou volume",
            janela="Período completo 2011–2025 · Agregados por unidade hospitalar",
            dados="Variáveis **Hospital**, Dias_Inter, MortEsperada, Idade, IMC, pO2_AntesTrat, "
                  "pO2_DepoisTrat, TipodeADM e TipodeDoente da base Hospitais.xlsx.",
            glossario_dict={
                "Case-mix": "Conjunto de patologias e graus de complexidade dos doentes atendidos por um hospital.",
                "Mortalidade Esperada": "Score médio de probabilidade de morte. Não é a taxa real de mortalidade.",
                "pO₂": "Pressão parcial de oxigénio no sangue (mmHg). Valores normais: 75–100 mmHg.",
                "PPP": "Parceria Público-Privada. Hospital gerido por empresa privada com contrato público.",
            },
        )

        # KPIs
        hosp_stats = df.groupby("Hospital").agg(
            n=("ID_Doente","count"),
            dias=("Dias_Inter","mean"),
            mort=("MortEsperada_Pct","mean"),
            idade=("Idade","mean"),
            imc=("IMC","mean"),
        ).round(2).reset_index()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            h_maior = hosp_stats.loc[hosp_stats["n"].idxmax(), "Hospital"]
            kpi("Maior Volume", h_maior,
                f"{hosp_stats['n'].max()} doentes", BLUE)
        with c2:
            h_menor_mort = hosp_stats.loc[hosp_stats["mort"].idxmin(), "Hospital"]
            kpi("Menor Mortalidade", h_menor_mort,
                f"{hosp_stats['mort'].min():.1f}%", GREEN)
        with c3:
            h_maior_mort = hosp_stats.loc[hosp_stats["mort"].idxmax(), "Hospital"]
            kpi("Maior Mortalidade", h_maior_mort,
                f"{hosp_stats['mort'].max():.1f}%", RED)
        with c4:
            h_mais_dias = hosp_stats.loc[hosp_stats["dias"].idxmax(), "Hospital"]
            kpi("Mais Dias Intern.", h_mais_dias,
                f"{hosp_stats['dias'].max():.1f} dias", AMBER)

        # Tabela comparativa
        st.markdown('<div class="section-title">Comparativo Detalhado</div>',
                    unsafe_allow_html=True)
        tabela = hosp_stats.copy()
        tabela.columns = ["Hospital","Doentes","Dias Inter. (média)",
                           "Mort. Esp. (%)","Idade Média","IMC Médio"]
        st.dataframe(
            tabela.style
            .format({"Doentes":"{:.0f}","Dias Inter. (média)":"{:.1f}",
                     "Mort. Esp. (%)":"{:.1f}","Idade Média":"{:.1f}","IMC Médio":"{:.2f}"})
            .map(lambda v: f"color: {RED}; font-weight:600" if isinstance(v, float) and v > 28
                 else (f"color: {AMBER}; font-weight:600" if isinstance(v, float) and v > 22
                       else ""), subset=["Mort. Esp. (%)"]),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown('<div class="section-title">Análise Visual por Hospital</div>',
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            # Dias de internamento
            hs = hosp_stats.sort_values("dias")
            fig = px.bar(hs, y="Hospital", x="dias", orientation="h",
                         color="Hospital", color_discrete_map=HOSP_COLORS,
                         text=hs["dias"].round(1))
            fig.update_traces(textposition="outside", textfont_color=TEXT,
                              marker_line_width=0)
            apply_layout(fig, "Dias de Internamento Médio por Hospital",
                         margin=dict(l=16, r=16, t=80, b=16))
            fig.update_layout(showlegend=False)
            chart(fig,
                  "Duração média do internamento por unidade hospitalar.",
                  "Barras mais longas indicam internamentos mais prolongados. "
                  "Diferenças entre hospitais podem reflectir case-mix, especialização ou eficiência operacional.",
                  "Variáveis **Hospital** e **Dias_Inter** da base de dados. Média aritmética por hospital.",
                  "Hospitais com internamentos mais longos podem ter populações mais complexas "
                  "ou diferentes protocolos de alta clínica.")

        with col2:
            # Mortalidade por hospital
            def mort_color(v):
                if v > 28: return RED
                elif v > 22: return AMBER
                return GREEN

            hs2 = hosp_stats.sort_values("mort")
            hs2["cor"] = hs2["mort"].apply(mort_color)
            fig2 = go.Figure()
            for _, row in hs2.iterrows():
                fig2.add_trace(go.Bar(
                    y=[row["Hospital"]], x=[row["mort"]],
                    orientation="h",
                    marker_color=row["cor"],
                    marker_line_width=0,
                    text=f"{row['mort']:.1f}%",
                    textposition="outside",
                    textfont_color=TEXT,
                    name=row["Hospital"],
                    showlegend=False,
                    hovertemplate=f"<b>{row['Hospital']}</b><br>Mort. Esp.: {row['mort']:.1f}%<extra></extra>",
                ))
            apply_layout(fig2, "Mortalidade Esperada por Hospital",
                         margin=dict(l=16, r=16, t=80, b=16))
            chart(fig2,
                  "Score médio de mortalidade esperada por hospital. Verde ≤22% · Âmbar 22-28% · Vermelho >28%.",
                  "O semáforo de cores (verde/âmbar/vermelho) classifica os hospitais por nível de risco. "
                  "Um score mais alto pode reflectir um case-mix mais grave, não necessariamente pior qualidade.",
                  "Variável **MortEsperada** (×100) média por hospital. "
                  "Limiares: baixo ≤22%, moderado 22–28%, elevado >28%.",
                  "Hospitais com mortalidade esperada elevada devem ser analisados em conjunto com "
                  "a complexidade da sua população para evitar comparações injustas.")

        col3, col4 = st.columns(2)

        with col3:
            # pO2 antes/depois
            po2 = df.groupby("Hospital").agg(
                antes=("pO2_AntesTrat","mean"),
                depois=("pO2_DepoisTrat","mean"),
            ).round(2).reset_index()
            fig3 = go.Figure()
            for col_v, label, cor in [("antes","pO₂ Antes",BLUE),("depois","pO₂ Depois",GREEN)]:
                fig3.add_trace(go.Bar(
                    x=po2["Hospital"], y=po2[col_v],
                    name=label, marker_color=cor,
                    marker_line_width=0,
                ))
            apply_layout(fig3, "pO₂ Antes vs Depois do Tratamento por Hospital",
                         legend=dict(orientation="h", yanchor="top", y=1.18,
                                     xanchor="left", x=-0.02,
                                     bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                     font=dict(color=TEXT, size=11)),
                         margin=dict(l=16, r=16, t=100, b=16))
            fig3.update_layout(barmode="group")
            chart(fig3,
                  "Comparação da pressão parcial de oxigénio antes e após tratamento, por hospital.",
                  "Barras mais próximas indicam menor variação com o tratamento. "
                  "Uma queda no valor pós-tratamento não é necessariamente negativa — "
                  "pode reflectir o tipo de intervenção realizada.",
                  "Variáveis **pO2_AntesTrat** e **pO2_DepoisTrat** da base de dados (mmHg). Média por hospital.",
                  None)

        with col4:
            # Bubble mortalidade vs dias
            fig4 = go.Figure()
            for _, row in hosp_stats.iterrows():
                fig4.add_trace(go.Scatter(
                    x=[row["dias"]], y=[row["mort"]],
                    mode="markers+text",
                    marker=dict(size=row["n"]/3, color=HOSP_COLORS.get(row["Hospital"], BLUE),
                                opacity=0.75, line=dict(width=1.5, color="white")),
                    text=[row["Hospital"]],
                    textposition="top center",
                    textfont=dict(color=TEXT, size=10),
                    name=row["Hospital"],
                    showlegend=False,
                    hovertemplate=f"<b>{row['Hospital']}</b><br>"
                                  f"Dias: {row['dias']:.1f}<br>Mort.: {row['mort']:.1f}%<br>"
                                  f"Doentes: {row['n']}<extra></extra>",
                ))
            apply_layout(fig4, "Mortalidade vs Dias de Internamento (tamanho = n.º doentes)",
                         margin=dict(l=16, r=16, t=80, b=16))
            fig4.update_xaxes(title_text="Dias de Internamento (média)", title_font_color=MUTED)
            fig4.update_yaxes(title_text="Mortalidade Esperada (%)", title_font_color=MUTED)
            chart(fig4,
                  "Cada bolha é um hospital. Tamanho proporcional ao volume de doentes.",
                  "Hospitais no canto superior direito têm simultaneamente mais dias de internamento "
                  "e maior mortalidade — potencial indicador de população mais grave ou de ineficiência. "
                  "O tamanho da bolha contextualiza o peso de cada hospital na amostra.",
                  "Variáveis **Dias_Inter** (média), **MortEsperada_Pct** (média) e "
                  "contagem de doentes por hospital.",
                  "A correlação entre dias de internamento e mortalidade esperada, "
                  "se existente, sugere que doentes de maior risco tendem a permanecer mais tempo internados.")

        # Sunburst
        st.markdown('<div class="section-title">Hierarquia Hospitalar</div>',
                    unsafe_allow_html=True)
        sb_df = df.groupby(["Hospital","TipodeADM_Label","TipodeDoente_Label"]).size().reset_index(name="n")
        fig_sb = px.sunburst(
            sb_df, path=["Hospital","TipodeADM_Label","TipodeDoente_Label"],
            values="n", color="Hospital",
            color_discrete_map=HOSP_COLORS,
        )
        fig_sb.update_traces(textfont_color="white")
        fig_sb.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font=dict(color=TEXT),
            margin=dict(l=16, r=16, t=80, b=16),
            title=dict(text="Distribuição Hierárquica: Hospital → Tipo de Admissão → Tipo de Doente",
                       x=0.01, font=dict(size=15, color=TEXT)),
        )
        chart(fig_sb,
              "Hierarquia de 3 níveis: Hospital → Tipo de Admissão → Tipo de Doente. Clique para explorar.",
              "O anel interior representa os hospitais, o intermédio o tipo de admissão (Urgente/Programada), "
              "e o exterior o tipo de doente. A dimensão de cada segmento é proporcional ao n.º de doentes.",
              "Variáveis **Hospital**, **TipodeADM_Label** e **TipodeDoente_Label** da base de dados.",
              None)


# ══════════════════════════════════════════════════════════════════════════════
# ABA 3 — TRATAMENTO
# ══════════════════════════════════════════════════════════════════════════════
if 3 in abas_acesso:
    with tab_map[3]:

        tab_header(
            audiencia="Gestão · Administração",
            decisao="Avaliar o impacto terapêutico nos parâmetros clínicos e identificar padrões de resposta",
            janela="Antes e depois do tratamento · Três momentos de plaquetas (M1/M2/M3)",
            dados="Variáveis **pO2_AntesTrat**, pO2_DepoisTrat, Glicemia_AntesTrat, Glicemia_DepoisTrat, "
                  "Satur_O2_*, Plaquetas_M1/M2/M3 e todas as variáveis quantitativas da base Hospitais.xlsx.",
            glossario_dict={
                "pO₂": "Pressão parcial de oxigénio arterial (mmHg). Normal: 75–100 mmHg. Baixo: hipoxemia.",
                "Glicemia": "Concentração de glucose no sangue (mg/dL). Normal em jejum: 70–100 mg/dL.",
                "Plaquetas M1/M2/M3": "Contagem de plaquetas (×10³/μL) em três momentos de avaliação.",
                "KDE": "Kernel Density Estimation — estimativa suavizada da distribuição de probabilidade.",
                "Correlação de Pearson (r)": "Medida de associação linear entre duas variáveis. Varia de −1 a +1.",
            },
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi("pO₂ Antes Trat.", f"{df['pO2_AntesTrat'].mean():.1f}",
                "mmHg · média", BLUE)
        with c2:
            kpi("pO₂ Depois Trat.", f"{df['pO2_DepoisTrat'].mean():.1f}",
                f"mmHg · Δ {df['pO2_DepoisTrat'].mean()-df['pO2_AntesTrat'].mean():.1f}", CYAN)
        with c3:
            kpi("Glicemia Antes", f"{df['Glicemia_AntesTrat'].mean():.1f}",
                "mg/dL · média", AMBER)
        with c4:
            kpi("Glicemia Depois", f"{df['Glicemia_DepoisTrat'].mean():.1f}",
                f"mg/dL · Δ {df['Glicemia_DepoisTrat'].mean()-df['Glicemia_AntesTrat'].mean():.1f}", RED)

        st.markdown('<div class="section-title">Parâmetros Respiratórios</div>',
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            # KDE pO2
            from scipy.stats import gaussian_kde
            kde_colors = {
                "Antes": (BLUE, "rgba(91,141,217,0.2)"),
                "Depois": (GREEN, "rgba(16,185,129,0.2)"),
            }
            fig_kde = go.Figure()
            for serie, label, cor_line in [
                (df["pO2_AntesTrat"], "Antes", BLUE),
                (df["pO2_DepoisTrat"], "Depois", GREEN),
            ]:
                vals = serie.dropna()
                xs = np.linspace(vals.min(), vals.max(), 200)
                kde = gaussian_kde(vals)
                _, fill_c = kde_colors[label]
                fig_kde.add_trace(go.Scatter(
                    x=xs, y=kde(xs), mode="lines",
                    name=label, line=dict(color=cor_line, width=2.5),
                    fill="tozeroy",
                    fillcolor=fill_c,
                    hovertemplate=f"pO₂=%{{x:.1f}} mmHg<extra>{label}</extra>",
                ))
            apply_layout(fig_kde, "KDE — pO₂ Antes vs Depois do Tratamento",
                         legend=dict(orientation="h", yanchor="top", y=1.18,
                                     xanchor="left", x=-0.02,
                                     bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                     font=dict(color=TEXT, size=11)),
                         margin=dict(l=16, r=16, t=100, b=16))
            fig_kde.update_xaxes(title_text="pO₂ (mmHg)", title_font_color=MUTED)
            fig_kde.update_yaxes(title_text="Densidade", title_font_color=MUTED)
            chart(fig_kde,
                  "Estimativa de densidade kernel da pO₂ antes e depois do tratamento.",
                  "As curvas representam a distribuição suavizada dos valores de pO₂. "
                  "Um deslocamento da curva para a direita indica melhoria nos valores de oxigenação. "
                  "Sobreposição ampla indica pouca diferença entre os dois momentos.",
                  "Variáveis **pO2_AntesTrat** e **pO2_DepoisTrat** (mmHg). "
                  "KDE calculado com scipy.stats.gaussian_kde.",
                  "A distribuição pós-tratamento mais larga sugere resposta heterogénea — "
                  "alguns doentes melhoram significativamente, outros não.")
            del fig_kde

        with col2:
            # Dispersão pO2 antes vs depois com regressão
            fig_sc = px.scatter(df, x="pO2_AntesTrat", y="pO2_DepoisTrat",
                                color="Hospital", color_discrete_map=HOSP_COLORS,
                                opacity=0.6,
                                hover_data=["Hospital","Idade","Dias_Inter"],
                                trendline="ols",
                                trendline_scope="overall",
                                trendline_color_override=AMBER)
            apply_layout(fig_sc, "Dispersão pO₂ Antes vs Depois com Reta de Regressão",
                         legend=dict(orientation="h", yanchor="top", y=1.18,
                                     xanchor="left", x=-0.02,
                                     bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                     font=dict(color=TEXT, size=11)),
                         margin=dict(l=16, r=16, t=100, b=16))
            fig_sc.update_xaxes(title_text="pO₂ Antes (mmHg)", title_font_color=MUTED)
            fig_sc.update_yaxes(title_text="pO₂ Depois (mmHg)", title_font_color=MUTED)
            chart(fig_sc,
                  "Cada ponto é um doente. A linha dourada é a reta de regressão linear global.",
                  "Pontos acima da diagonal indicam melhoria pós-tratamento. "
                  "Pontos abaixo indicam deterioração. A reta de regressão mostra a tendência global. "
                  "A cor diferencia os hospitais.",
                  "Variáveis **pO2_AntesTrat** e **pO2_DepoisTrat** (mmHg). "
                  "Regressão OLS calculada com plotly trendline.",
                  "Doentes afastados da reta de regressão (outliers) merecem investigação clínica individual.")

        st.markdown('<div class="section-title">Glicemia e Plaquetas</div>',
                    unsafe_allow_html=True)
        col3, col4 = st.columns(2)

        with col3:
            # Glicemia por hospital
            glic = df.groupby("Hospital").agg(
                antes=("Glicemia_AntesTrat","mean"),
                depois=("Glicemia_DepoisTrat","mean"),
            ).round(1).reset_index()
            fig_g = go.Figure()
            for col_v, label, cor in [("antes","Antes",AMBER),("depois","Depois",RED)]:
                fig_g.add_trace(go.Bar(
                    x=glic["Hospital"], y=glic[col_v],
                    name=label, marker_color=cor, marker_line_width=0,
                ))
            apply_layout(fig_g, "Glicemia Antes vs Depois por Hospital",
                         legend=dict(orientation="h", yanchor="top", y=1.18,
                                     xanchor="left", x=-0.02,
                                     bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                     font=dict(color=TEXT, size=11)),
                         margin=dict(l=16, r=16, t=100, b=16))
            fig_g.update_layout(barmode="group")
            fig_g.update_xaxes(tickangle=-20)
            chart(fig_g,
                  "Glicemia média (mg/dL) antes e depois do tratamento, por hospital.",
                  "Barras agrupadas permitem comparar o efeito do tratamento na glicemia. "
                  "Um aumento pós-tratamento pode ser esperado em doentes diabéticos sujeitos a corticoides.",
                  "Variáveis **Glicemia_AntesTrat** e **Glicemia_DepoisTrat** (mg/dL). Média por hospital.",
                  None)

        with col4:
            # Plaquetas por tipo de doente ao longo dos anos
            plaq_ano = df.groupby(["Ano","TipodeDoente_Label"]).agg(
                m1=("Plaquetas_M1","mean"),
            ).round(1).reset_index()
            fig_p = px.line(plaq_ano, x="Ano", y="m1", color="TipodeDoente_Label",
                            color_discrete_map={"Tipo 1": BLUE, "Tipo 2": AMBER},
                            markers=True, line_shape="spline")
            fig_p.update_traces(line_width=2.5, marker_size=6)
            apply_layout(fig_p, "Evolução das Plaquetas (M1) por Tipo de Doente e Ano",
                         legend=dict(orientation="h", yanchor="top", y=1.18,
                                     xanchor="left", x=-0.02,
                                     bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                     font=dict(color=TEXT, size=11)),
                         margin=dict(l=16, r=16, t=100, b=16))
            fig_p.update_yaxes(title_text="Plaquetas (×10³/μL)", title_font_color=MUTED)
            chart(fig_p,
                  "Evolução temporal do valor médio de plaquetas no momento M1, por tipo de doente.",
                  "Cada linha representa um tipo de doente. "
                  "Quedas acentuadas num determinado ano podem indicar eventos clínicos ou alterações populacionais. "
                  "O Tipo 1 tende a apresentar maior variabilidade por ter menos doentes.",
                  "Variáveis **Plaquetas_M1**, **TipodeDoente** e **Ano** da base de dados. "
                  "Média anual de plaquetas por tipo.",
                  "A maior variabilidade do Tipo 1 é consistente com a sua menor dimensão amostral (n≈26), "
                  "o que amplifica o efeito de casos individuais na média.")

        # Heatmap correlações
        st.markdown('<div class="section-title">Correlações entre Variáveis Quantitativas</div>',
                    unsafe_allow_html=True)
        num_cols = ["Idade","Peso","Altura","IMC","Dias_Inter","Num_Cirurgias","Grau_Dor",
                    "Freq_Resp","pCO2","pH","pO2_AntesTrat","pO2_DepoisTrat",
                    "Satur_O2_AntesTrat","Satur_O2_DepoisTrat",
                    "Glicemia_AntesTrat","Glicemia_DepoisTrat",
                    "Plaquetas_M1","Plaquetas_M2","Plaquetas_M3","MortEsperada_Pct"]
        corr = df[num_cols].corr().round(2)
        fig_hm = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale="RdBu_r", zmin=-1, zmax=1,
            text=corr.values.round(2),
            texttemplate="%{text}",
            textfont_size=8,
            hovertemplate="<b>%{x}</b> × <b>%{y}</b><br>r = %{z:.2f}<extra></extra>",
            colorbar=dict(title="r", tickfont=dict(color=TEXT), titlefont=dict(color=TEXT)),
        ))
        apply_layout(fig_hm, "Heatmap de Correlações (Pearson)",
                     margin=dict(l=80, r=16, t=80, b=80))
        fig_hm.update_xaxes(tickangle=-45, tickfont_size=9)
        fig_hm.update_yaxes(tickfont_size=9)
        fig_hm.update_layout(height=520)
        chart(fig_hm,
              "Coeficiente de correlação de Pearson entre todas as variáveis quantitativas.",
              "Vermelho escuro = correlação positiva forte (+1). Azul escuro = negativa forte (−1). "
              "Branco = sem correlação. A diagonal é sempre 1 (cada variável correlaciona-se consigo própria). "
              "Valores |r| > 0.5 merecem atenção analítica.",
              "Calculado com pandas .corr() sobre todas as variáveis quantitativas da base de dados filtrada.",
              "Correlações fortes entre pO₂ e Saturação O₂ (antes e depois) são esperadas fisiologicamente. "
              "Correlações entre Peso/IMC/Altura reflectem a definição matemática do IMC.")


# ══════════════════════════════════════════════════════════════════════════════
# ABA 4 — RISCO & MORTALIDADE
# ══════════════════════════════════════════════════════════════════════════════
if 4 in abas_acesso:
    with tab_map[4]:

        tab_header(
            audiencia="Administração (acesso exclusivo)",
            decisao="Identificar segmentos de maior risco e validar hipóteses estatísticas sobre mortalidade",
            janela="Período completo · Score de mortalidade contínuo por doente",
            dados="Variável **MortEsperada** (score contínuo 0–1) cruzada com Sexo, Hospital, Faixa_Etaria "
                  "e comorbilidades. Testes estatísticos calculados com scipy.stats sobre a amostra filtrada.",
            glossario_dict={
                "Mortalidade Esperada": "Score probabilístico contínuo [0–1] que estima o risco de morte. Aqui expresso em percentagem.",
                "H₀ (hipótese nula)": "Hipótese de partida que assume ausência de efeito ou diferença.",
                "p-value": "Probabilidade de obter um resultado igual ou mais extremo assumindo H₀ verdadeira. Se p < 0,05, rejeita-se H₀.",
                "Teste t": "Testa se as médias de dois grupos independentes são estatisticamente diferentes.",
                "Qui-quadrado (χ²)": "Testa se duas variáveis qualitativas são independentes numa tabela de contingência.",
            },
        )
        mort_m_val = df[df["Sexo"]=="M"]["MortEsperada_Pct"].mean()
        mort_f_val = df[df["Sexo"]=="F"]["MortEsperada_Pct"].mean()
        h_maior_risco = df.groupby("Hospital")["MortEsperada_Pct"].mean().idxmax()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi("Mortalidade Geral", f"{mort_geral:.1f}%",
                "score médio da amostra filtrada", RED)
        with c2:
            kpi("Mortalidade Feminina", f"{mort_f_val:.1f}%",
                f"Δ vs masculino: {mort_f_val-mort_m_val:+.1f}pp", PINK)
        with c3:
            kpi("Mortalidade Masculina", f"{mort_m_val:.1f}%",
                "referência", BLUE)
        with c4:
            kpi("Hospital Maior Risco", h_maior_risco,
                f"{df.groupby('Hospital')['MortEsperada_Pct'].mean()[h_maior_risco]:.1f}%", AMBER)

        st.markdown('<div class="section-title">Risco por Segmento</div>',
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            # Mortalidade por hospital (semáforo)
            hm = df.groupby("Hospital")["MortEsperada_Pct"].mean().round(1).reset_index()
            hm.columns = ["Hospital","mort"]
            hm = hm.sort_values("mort", ascending=True)
            hm["cor"] = hm["mort"].apply(
                lambda v: RED if v > 28 else (AMBER if v > 22 else GREEN))
            fig = go.Figure()
            for _, row in hm.iterrows():
                fig.add_trace(go.Bar(
                    y=[row["Hospital"]], x=[row["mort"]],
                    orientation="h",
                    marker_color=row["cor"], marker_line_width=0,
                    text=f"{row['mort']:.1f}%",
                    textposition="outside", textfont_color=TEXT,
                    name=row["Hospital"], showlegend=False,
                    hovertemplate=f"<b>{row['Hospital']}</b><br>{row['mort']:.1f}%<extra></extra>",
                ))
            apply_layout(fig, "Mortalidade Esperada por Hospital (Semáforo)",
                         margin=dict(l=16, r=16, t=80, b=16))
            chart(fig,
                  "Verde ≤22% (baixo risco) · Âmbar 22–28% (moderado) · Vermelho >28% (elevado).",
                  "O semáforo de cores permite identificar rapidamente hospitais com risco elevado. "
                  "Esta classificação é relativa à distribuição da amostra, não a limiares clínicos absolutos.",
                  "Variável **MortEsperada** (×100). Limiares definidos com base na distribuição da amostra.",
                  "Hospitais de risco elevado devem ser analisados em contexto — "
                  "um case-mix mais grave justifica naturalmente scores mais altos.")

        with col2:
            # Mortalidade por faixa etária
            fe_mort = df.groupby("Faixa_Etaria", observed=False)["MortEsperada_Pct"].mean().round(1).reset_index()
            fe_mort["Faixa_Etaria"] = pd.Categorical(fe_mort["Faixa_Etaria"],
                                                       categories=FAIXA_ORDER, ordered=True)
            fe_mort = fe_mort.sort_values("Faixa_Etaria")
            grad = [GREEN, CYAN, AMBER, "#f97316", RED]
            fig2 = px.bar(fe_mort, x="Faixa_Etaria", y="MortEsperada_Pct",
                          color="Faixa_Etaria",
                          color_discrete_sequence=grad,
                          text=fe_mort["MortEsperada_Pct"].apply(lambda v: f"{v:.1f}%"))
            fig2.update_traces(textposition="outside", textfont_color=TEXT,
                               marker_line_width=0)
            apply_layout(fig2, "Mortalidade Esperada por Faixa Etária",
                         margin=dict(l=16, r=16, t=80, b=16))
            fig2.update_layout(showlegend=False)
            fig2.update_xaxes(categoryorder="array", categoryarray=FAIXA_ORDER)
            chart(fig2,
                  "Score médio de mortalidade esperada por grupo etário (gradiente verde → vermelho).",
                  "O gradiente de cor reflecte o aumento do risco com a idade. "
                  "A progressão crescente é esperada — doentes mais idosos têm maior fragilidade clínica.",
                  "Variáveis **Idade** (agrupada em faixas) e **MortEsperada** da base de dados.",
                  "A relação crescente entre idade e mortalidade esperada é consistente com "
                  "a literatura geriátrica. O salto entre 70-80 e >80 é particularmente relevante.")

        # Mortalidade por comorbilidade
        st.markdown('<div class="section-title">Impacto das Comorbilidades</div>',
                    unsafe_allow_html=True)
        comorb_mort = []
        for col_c, label in COMORB_MAP.items():
            m_s = df[df[col_c]=="S"]["MortEsperada_Pct"].mean()
            m_n = df[df[col_c]=="N"]["MortEsperada_Pct"].mean()
            comorb_mort.append({"Comorbilidade": label, "Com (S)": round(m_s,1), "Sem (N)": round(m_n,1)})
        cm_df = pd.DataFrame(comorb_mort)
        fig3 = go.Figure()
        for col_v, label, cor in [("Com (S)","Com condição",RED),("Sem (N)","Sem condição",BLUE)]:
            fig3.add_trace(go.Bar(
                x=cm_df["Comorbilidade"], y=cm_df[col_v],
                name=label, marker_color=cor, marker_line_width=0,
                text=cm_df[col_v].apply(lambda v: f"{v:.1f}%"),
                textposition="outside", textfont_color=TEXT,
            ))
        apply_layout(fig3, "Mortalidade Esperada por Comorbilidade — Com vs Sem",
                     legend=dict(orientation="h", yanchor="top", y=1.18,
                                 xanchor="left", x=-0.02,
                                 bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                 font=dict(color=TEXT, size=11)),
                     margin=dict(l=16, r=16, t=100, b=16))
        fig3.update_layout(barmode="group")
        chart(fig3,
              "Mortalidade esperada média em doentes com e sem cada comorbilidade.",
              "Barras vermelhas (Com) superiores às azuis (Sem) indicam que a comorbilidade "
              "está associada a maior risco de mortalidade. "
              "Comorbilidades com maior diferença têm maior impacto no perfil de risco.",
              "Variáveis de comorbilidade (S/N) cruzadas com **MortEsperada** (×100). "
              "Médias calculadas para cada subgrupo.",
              "A insuficiência cardíaca tende a apresentar a maior diferença de mortalidade "
              "entre grupos, o que é clinicamente esperado pela sua gravidade intrínseca.")

        # Testes estatísticos
        st.markdown('<div class="section-title">Evidência Estatística Inferencial</div>',
                    unsafe_allow_html=True)
        from scipy import stats as sp_stats

        testes = []

        # Teste 1: t Mortalidade por Sexo
        g_m = df[df["Sexo"]=="M"]["MortEsperada_Pct"].dropna()
        g_f = df[df["Sexo"]=="F"]["MortEsperada_Pct"].dropna()
        t1, p1 = sp_stats.ttest_ind(g_m, g_f, equal_var=True)
        testes.append({
            "Teste": "Teste t — Mortalidade por Sexo",
            "H₀": "Mortalidade igual entre M e F",
            "Estatística": f"t = {t1:.3f}",
            "p-value": f"{p1:.4f}",
            "Conclusão": "✅ Não rejeitar H₀" if p1 > 0.05 else "❌ Rejeitar H₀",
        })

        # Teste 2: Qui-quadrado Fumador × Diabetes
        ct = pd.crosstab(df["Fumador"], df["Diabetes"])
        chi2, p2, dof, _ = sp_stats.chi2_contingency(ct)
        testes.append({
            "Teste": "Qui-quadrado — Fumador × Diabetes",
            "H₀": "Fumador e Diabetes são independentes",
            "Estatística": f"χ² = {chi2:.3f}",
            "p-value": f"{p2:.4f}",
            "Conclusão": "✅ Não rejeitar H₀" if p2 > 0.05 else "❌ Rejeitar H₀",
        })

        # Teste 3: t Dias_Inter por Diabetes
        g_s = df[df["Diabetes"]=="S"]["Dias_Inter"].dropna()
        g_n = df[df["Diabetes"]=="N"]["Dias_Inter"].dropna()
        t3, p3 = sp_stats.ttest_ind(g_s, g_n, equal_var=True)
        testes.append({
            "Teste": "Teste t — Dias Internamento por Diabetes",
            "H₀": "Dias internamento igual com/sem Diabetes",
            "Estatística": f"t = {t3:.3f}",
            "p-value": f"{p3:.4f}",
            "Conclusão": "✅ Não rejeitar H₀" if p3 > 0.05 else "❌ Rejeitar H₀",
        })

        testes_df = pd.DataFrame(testes)
        st.dataframe(
            testes_df.style.applymap(
                lambda v: f"color: {GREEN}" if "✅" in str(v) else (f"color: {RED}" if "❌" in str(v) else ""),
                subset=["Conclusão"]
            ),
            use_container_width=True,
            hide_index=True,
        )
        with st.expander("📖 Como interpretar os testes estatísticos"):
            st.markdown(f"""
**Nível de significância:** α = 0,05

**Teste t de Student:** compara médias entre dois grupos independentes. Um p-value < 0,05 indica
diferença estatisticamente significativa entre os grupos.

**Teste do Qui-quadrado:** testa a independência entre duas variáveis qualitativas.
Um p-value < 0,05 indica associação estatisticamente significativa.

**Não rejeitar H₀** não significa que H₀ é verdadeira — significa apenas que não há evidência
suficiente para a refutar com base na amostra disponível.
""")

        insight("O único teste com resultado significativo (p=0,008) é o Teste t para Dias de "
                "Internamento por Diabetes — doentes diabéticos internam em média ~1,9 dias a mais.")


# ══════════════════════════════════════════════════════════════════════════════
# RODAPÉ
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="footer">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px">
        <div>
            <div style="color:{TEXT};font-weight:700;font-size:0.88rem;margin-bottom:6px">
                🏥 Dashboard Hospitalar · Região de Lisboa
            </div>
            <div>Análise Estatística Avançada · ISCTE – Instituto Universitário de Lisboa</div>
            <div>Data Science & Business Analytics · 2025/2026</div>
        </div>
        <div>
            <div style="color:{TEXT};font-weight:600;margin-bottom:6px">Dados</div>
            <div>Base de dados: Hospitais.xlsx</div>
            <div>n = 449 doentes · 6 hospitais · 2011–2025</div>
            <div>Limpeza: 4 anomalias corrigidas</div>
        </div>
        <div>
            <div style="color:{TEXT};font-weight:600;margin-bottom:6px">Tecnologia</div>
            <div>Python · Streamlit · Plotly</div>
            <div>pandas · scipy · scikit-learn</div>
        </div>
        <div>
            <div style="color:{TEXT};font-weight:600;margin-bottom:6px">Autor</div>
            <div>Ricardo Manuel Freire Santos</div>
            <div>N.º 143318</div>
            <div>Docente: João Curado Silva</div>
        </div>
    </div>
    <hr style="border-color:{GRID};margin:16px 0 8px">
    <div style="text-align:center;font-size:0.72rem">
        Dashboard desenvolvido no âmbito do Projeto de Análise Estatística Avançada · ISCTE · Mai/2026
        · Todos os dados são fictícios para fins académicos
    </div>
</div>
""", unsafe_allow_html=True)