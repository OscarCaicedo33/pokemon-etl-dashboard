"""
Interfaz Streamlit del proyecto Pokemon ETL.
Ejecutar: streamlit run app.py
"""

import base64
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DB_PATH  = Path(__file__).parent / "data" / "output" / "pokemon.db"
CSV_PATH = Path(__file__).parent / "data" / "processed" / "pokemon_clean.csv"

ACCENT   = "#2962FF"
BG       = "#F5F7FA"
CARD_BG  = "#FFFFFF"
TEXT     = "#111111"
TEXT_SUB = "#555555"

TYPE_COLORS = {
    "normal": "#A8A878", "fire": "#F08030", "water": "#6890F0",
    "electric": "#F8D030", "grass": "#78C850", "ice": "#98D8D8",
    "fighting": "#C03028", "poison": "#A040A0", "ground": "#E0C068",
    "flying": "#A890F0", "psychic": "#F85888", "bug": "#A8B820",
    "rock": "#B8A038", "ghost": "#705898", "dragon": "#7038F8",
    "dark": "#705848", "steel": "#B8B8D0", "fairy": "#EE99AC",
}

STAT_COLS = ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]
STAT_LABELS = {
    "hp": "HP", "attack": "Ataque", "defense": "Defensa",
    "special_attack": "Sp. Ataque", "special_defense": "Sp. Defensa", "speed": "Velocidad",
}

ARTWORK = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{id}.png"

NAV_PAGES = [
    "Vista General",
    "Estadísticas",
    "Galería",
    "Comparación",
    "Resumen ETL",
]

st.set_page_config(
    page_title="Pokemon ETL — Portfolio",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def inject_css() -> None:
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
        '&family=Press+Start+2P&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    css = f"""
<style>

* {{ font-family: 'Inter', sans-serif !important; }}

/* Los íconos de Streamlit usan la fuente Material Symbols: si se les aplica
   Inter, se ve el nombre del ícono como texto (keyboard_double_arrow_left) */
span[data-testid="stIconMaterial"] {{
    font-family: 'Material Symbols Rounded' !important;
}}

.pokemon-brand {{
    font-family: 'Press Start 2P', monospace !important;
    line-height: 1.7;
    letter-spacing: 0.02em;
}}

.stApp {{ background-color: {BG} !important; color: {TEXT} !important; }}
.main .block-container {{
    padding-top: 2rem;
    padding-bottom: 2.5rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    background: {CARD_BG};
    border-radius: 24px;
    box-shadow: 0 4px 28px rgba(0,0,0,0.07);
}}

.card {{
    background: {CARD_BG};
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    animation: fadeUp 0.5s ease both;
}}
.kpi-card {{
    background: {CARD_BG};
    border-radius: 16px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 4px solid {ACCENT};
    animation: fadeUp 0.5s ease both;
    margin-bottom: 0.75rem;
}}
.kpi-value {{
    font-size: 1.9rem;
    font-weight: 700;
    color: {ACCENT};
    margin: 0;
    line-height: 1.1;
}}
.kpi-label {{
    font-size: 0.75rem;
    color: {TEXT_SUB};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0 0 0.15rem;
}}

.hero-container {{
    background: linear-gradient(135deg, #EEF2FF 0%, #E8F4FD 100%);
    border-radius: 24px;
    padding: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 300px;
    animation: slideIn 0.6s ease both;
}}
.hero-badge {{
    background: {ACCENT};
    color: white;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.4rem;
}}

.poke-card {{
    background: {CARD_BG};
    border-radius: 16px;
    padding: 1rem 0.8rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    animation: fadeUp 0.4s ease both;
    margin-bottom: 0.5rem;
}}
.poke-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 8px 24px rgba(41,98,255,0.15);
}}
.poke-name {{
    font-weight: 600;
    color: {TEXT};
    font-size: 0.82rem;
    margin: 0.4rem 0 0.2rem;
    text-transform: capitalize;
}}
.type-badge {{
    border-radius: 12px;
    padding: 0.15rem 0.6rem;
    font-size: 0.68rem;
    font-weight: 600;
    color: white;
    display: inline-block;
    margin: 0.1rem;
}}
.bst-label {{
    font-size: 0.72rem;
    color: {TEXT_SUB};
    margin-top: 0.3rem;
}}

.section-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {TEXT};
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {ACCENT}22;
}}
.page-header {{ margin-bottom: 1.4rem; padding-bottom: 1rem; border-bottom: 2px solid {ACCENT}22; }}
.page-header h2 {{ color: {TEXT}; font-size: 0.80rem; font-weight: 400; margin: 0; line-height: 1.9; letter-spacing: 0.02em; }}
.page-header p  {{ color: {TEXT_SUB}; margin: 0.5rem 0 0; font-size: 0.58rem; line-height: 2.0; letter-spacing: 0.02em; }}

@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes slideIn {{
    from {{ opacity: 0; transform: translateX(-20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(to right, #FFFFFF 0%, #EEF2FF 100%) !important;
    border-right: 1px solid rgba(41,98,255,0.15);
}}
[data-testid="stSidebar"] > div:first-child {{
    padding-top: 0.6rem !important;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] {{
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label {{
    padding: 0.5rem 0.75rem;
    border-radius: 10px;
    cursor: pointer;
    font-family: 'Press Start 2P', monospace !important;
    font-size: 0.58rem !important;
    line-height: 2.2;
    color: {TEXT_SUB} !important;
    transition: background 0.15s ease, color 0.15s ease;
    width: 100%;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
    background: rgba(41,98,255,0.08);
    color: {ACCENT} !important;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {{
    display: none;
}}

[data-testid="stMetric"] {{
    background: {CARD_BG};
    border-radius: 16px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    border-left: 3px solid {ACCENT};
}}

[data-testid="stPlotlyChart"] {{
    background: {CARD_BG};
    border-radius: 20px;
    padding: 0.6rem 0.8rem 0.4rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.07);
    margin-bottom: 0.25rem;
    overflow: hidden;
}}
.js-plotly-plot, .plot-container, .svg-container {{
    overflow: hidden !important;
}}

.chart-conclusion {{
    font-size: 0.80rem;
    color: {TEXT_SUB};
    background: #F8FAFF;
    border-radius: 10px;
    padding: 0.55rem 0.9rem;
    margin: 0.3rem 0 0.9rem;
    border-left: 3px solid {ACCENT}55;
    line-height: 1.6;
}}

.main div[data-testid="stSelectbox"] {{
    background: {CARD_BG};
    border: 1.5px solid {ACCENT}33;
    border-radius: 16px;
    padding: 0.3rem 0.75rem 0.2rem;
    box-shadow: 0 2px 10px rgba(41,98,255,0.07);
}}
.main div[data-testid="stSelectbox"] label {{
    font-size: 0.62rem !important;
    font-weight: 600 !important;
    color: {ACCENT} !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0 !important;
}}
.main div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    min-height: 32px !important;
    padding-top: 2px !important;
    padding-bottom: 2px !important;
    font-size: 0.82rem !important;
}}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


@st.cache_data
def load_data() -> pd.DataFrame:
    if DB_PATH.exists():
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql("SELECT * FROM pokemon", conn)
    elif CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
    else:
        st.error("No se encontró el dataset. Ejecuta: python main.py --limit 151")
        st.stop()
    df["generation"] = df["generation"].fillna(0).astype(int)
    if "sprite_url" not in df.columns:
        df["sprite_url"] = df["id"].apply(
            lambda i: f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{i}.png"
        )
    df["artwork_url"] = df["id"].apply(lambda i: ARTWORK.format(id=int(i)))
    return df


def sidebar_nav_and_filters(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """Returns (current_page, filtered_df)."""

    # ── Logo (pegado al tope) ─────────────────────────────────────────────────
    st.sidebar.markdown(
        f"<div style='padding:0 0 1.6rem;text-align:center'>"
        f"<p class='pokemon-brand' style='color:{ACCENT};font-size:0.85rem;margin:0'>Pokémon ETL</p>"
        f"<p class='pokemon-brand' style='color:{TEXT_SUB};font-size:0.52rem;margin:0.6rem 0 0'>Portfolio · Generación I</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Navegación ────────────────────────────────────────────────────────────
    st.sidebar.markdown(
        f"<p class='pokemon-brand' style='font-size:0.52rem;color:{TEXT_SUB};"
        f"letter-spacing:0.05em;margin-bottom:0.5rem'>Navegación</p>",
        unsafe_allow_html=True,
    )
    selected_label = st.sidebar.radio("nav", options=NAV_PAGES, label_visibility="collapsed")
    current_page = selected_label

    st.sidebar.divider()

    # ── Filtros globales ──────────────────────────────────────────────────────
    st.sidebar.markdown(
        f"<p class='pokemon-brand' style='font-size:0.52rem;color:{TEXT_SUB};"
        f"letter-spacing:0.05em;margin:0.2rem 0 0.4rem'>Filtros</p>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f"<p style='font-size:0.68rem;color:{TEXT_SUB};margin:0 0 0.15rem'>Tipo primario</p>",
        unsafe_allow_html=True,
    )
    _ALL = "Todos"
    type_options = [_ALL] + sorted(df["type_primary"].dropna().unique().tolist())
    selected_type = st.sidebar.selectbox(
        "Tipo primario", options=type_options,
        format_func=lambda n: "Todos los tipos" if n == _ALL else n.capitalize(),
        label_visibility="collapsed",
    )
    st.sidebar.markdown(
        f"<p style='font-size:0.68rem;color:{TEXT_SUB};margin:0.5rem 0 0.15rem'>Tier de poder</p>",
        unsafe_allow_html=True,
    )
    tier_options = [_ALL] + sorted(df["power_tier"].dropna().unique().tolist())
    selected_tier = st.sidebar.selectbox(
        "Tier de poder", options=tier_options,
        format_func=lambda n: "Todos los tiers" if n == _ALL else n,
        label_visibility="collapsed",
    )

    df_filtered = df.copy()
    if selected_type != _ALL:
        df_filtered = df_filtered[df_filtered["type_primary"] == selected_type]
    if selected_tier != _ALL:
        df_filtered = df_filtered[df_filtered["power_tier"] == selected_tier]

    return current_page, df_filtered


def hero_todos(df: pd.DataFrame) -> None:
    strongest = df.loc[df["bst"].idxmax(), "name"].capitalize()

    # ── KPIs globales ─────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    kpi_def = [
        (k1, "Total Pokémon",    str(len(df)),                        ACCENT),
        (k2, "BST Promedio",     f"{df['bst'].mean():.0f}",           ACCENT),
        (k3, "Tipos distintos",  str(df["type_primary"].nunique()),    ACCENT),
        (k4, "Más poderoso",     strongest,                            "#F59E0B"),
    ]
    for col, label, value, color in kpi_def:
        with col:
            st.markdown(
                f'<div class="kpi-card" style="border-left-color:{color}">'
                f'<p class="kpi-label">{label}</p>'
                f'<p class="kpi-value" style="color:{color};font-size:1.35rem">{value}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)

    # ── Tira de sprites ───────────────────────────────────────────────────────
    items_html = ""
    for _, row in df.sort_values("id").iterrows():
        sprite = (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master"
            f"/sprites/pokemon/{int(row['id'])}.png"
        )
        tc = TYPE_COLORS.get(row["type_primary"], "#90A4AE")
        items_html += (
            f'<div style="display:inline-block;text-align:center;min-width:78px;'
            f'vertical-align:top;padding:0.3rem">'
            f'<img src="{sprite}" width="62"'
            f' style="filter:drop-shadow(0 2px 6px rgba(0,0,0,0.13))"/>'
            f'<p style="font-size:0.62rem;font-weight:600;color:{TEXT};margin:0.15rem 0 0.1rem;'
            f'text-transform:capitalize;white-space:normal">{row["name"]}</p>'
            f'<span style="background:{tc};color:white;border-radius:8px;'
            f'padding:0.05rem 0.35rem;font-size:0.56rem;font-weight:600">{row["type_primary"]}</span>'
            f'</div>'
        )
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#EEF2FF 0%,#E8F4FD 100%);'
        f'border-radius:24px;padding:1rem 1.5rem 1rem;animation:slideIn 0.6s ease both">'
        f'<p style="font-size:0.78rem;font-weight:600;color:{TEXT_SUB};margin:0 0 0.6rem">'
        f'Generación 1: Desliza para ver -></p>'
        f'<div style="overflow-x:auto;white-space:nowrap;padding-bottom:0.5rem">'
        f'<div style="display:inline-flex;gap:6px;align-items:flex-start">'
        f'{items_html}'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )


def hero_section(df_full: pd.DataFrame, selected_id: int) -> None:
    hero       = df_full[df_full["id"] == selected_id].iloc[0]
    type_color = TYPE_COLORS.get(hero["type_primary"], ACCENT)
    fill_rgba  = _hex_to_rgba(type_color, 0.25)
    artwork_src = ARTWORK.format(id=int(selected_id))

    type2_badge = ""
    if pd.notna(hero.get("type_secondary")):
        t2c = TYPE_COLORS.get(hero["type_secondary"], "#90A4AE")
        type2_badge = (
            f'<span class="type-badge" style="background:{t2c}">'
            f'{hero["type_secondary"]}</span>'
        )

    col_art, col_radar, col_kpis = st.columns([1, 1.1, 1])

    with col_art:
        st.markdown(
            f'<div class="hero-container">'
            f'<div style="text-align:center">'
            f'<span class="hero-badge">Pokémon Destacado</span><br>'
            f'<img src="{artwork_src}" width="200"'
            f' style="filter:drop-shadow(0 8px 24px rgba(0,0,0,0.15));animation:fadeUp 0.8s ease"/>'
            f'<p style="font-size:1.3rem;font-weight:700;color:{TEXT};'
            f'margin:0.5rem 0 0.15rem;text-transform:capitalize">'
            f'#{int(hero["id"])} {hero["name"]}</p>'
            f'<span class="type-badge" style="background:{type_color}">{hero["type_primary"]}</span>'
            f'{type2_badge}'
            f'<p style="color:{TEXT_SUB};font-size:0.82rem;margin-top:0.4rem">'
            f'BST&nbsp;<b style="color:{ACCENT}">{hero["bst"]}</b>'
            f'&nbsp;·&nbsp;Gen.&nbsp;{int(hero["generation"])}</p>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    with col_radar:
        stat_vals   = [int(hero[s]) for s in STAT_COLS]
        stat_labels = list(STAT_LABELS.values())
        fig = go.Figure(go.Scatterpolar(
            r=stat_vals + [stat_vals[0]],
            theta=stat_labels + [stat_labels[0]],
            fill="toself",
            fillcolor=fill_rgba,
            line=dict(color=type_color, width=2.5),
            marker=dict(color=type_color, size=6),
        ))
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 160], showticklabels=False,
                                gridcolor="#E5E7EB"),
                angularaxis=dict(tickfont=dict(size=11, color=TEXT)),
            ),
            showlegend=False,
            height=310,
            margin=dict(t=30, b=10, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            title=dict(
                text=f"<b>{hero['name'].capitalize()}</b> — Stats base",
                font=dict(size=13, color=TEXT), x=0.5,
            ),
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

    with col_kpis:
        st.markdown(
            f'<div class="kpi-card">'
            f'<p class="kpi-label">BST Total</p>'
            f'<p class="kpi-value">{int(hero["bst"])}</p>'
            f'</div>'
            f'<div class="kpi-card">'
            f'<p class="kpi-label">HP</p>'
            f'<p class="kpi-value">{int(hero["hp"])}</p>'
            f'</div>'
            f'<div class="kpi-card">'
            f'<p class="kpi-label">Ataque</p>'
            f'<p class="kpi-value">{int(hero["attack"])}</p>'
            f'</div>'
            f'<div class="kpi-card" style="border-left-color:#10B981">'
            f'<p class="kpi-label">Defensa</p>'
            f'<p class="kpi-value" style="color:#10B981">{int(hero["defense"])}</p>'
            f'</div>'
            f'<div class="kpi-card" style="border-left-color:#F59E0B">'
            f'<p class="kpi-label">Velocidad</p>'
            f'<p class="kpi-value" style="color:#F59E0B">{int(hero["speed"])}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="page-header">'
        f'<h2 class="pokemon-brand">{title}</h2>'
        f'<p class="pokemon-brand">{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def tab_overview(df: pd.DataFrame, df_full: pd.DataFrame) -> None:
    col_hero_sel, _ = st.columns([1, 2])
    with col_hero_sel:
        _TODOS = "— Todos —"
        poke_all = [_TODOS] + sorted(df_full["name"].tolist())
        sel_name = st.selectbox(
            "Pokemon destacado",
            options=poke_all,
            index=0,
            format_func=lambda n: "Todos los Pokémon" if n == _TODOS else n.capitalize(),
            key="pokemon_destacado_sel",
        )

    page_header("Vista General",
                "Análisis completo de los 151 Pokémon de la primera generación")

    if sel_name == _TODOS:
        hero_todos(df)
    else:
        sel_id = int(df_full[df_full["name"] == sel_name]["id"].iloc[0])
        hero_section(df_full, sel_id)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        type_counts = df["type_primary"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        bar_colors = [TYPE_COLORS.get(t, "#90A4AE") for t in type_counts["type"]]
        fig = go.Figure(go.Bar(
            x=type_counts["type"], y=type_counts["count"],
            marker=dict(color=bar_colors, line=dict(color="white", width=0.5)),
            text=type_counts["count"], textposition="outside",
            hovertemplate="<b>%{x}</b><br>Cantidad: %{y}<extra></extra>",
        ))
        fig.update_layout(
            title="Tipos Primarios más comunes", xaxis_tickangle=-40, height=420,
            margin=dict(t=50, b=90, l=10, r=10), template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, type_counts["count"].max() * 1.22]),
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})
        top_type  = type_counts.iloc[0]["type"].capitalize()
        top_count = int(type_counts.iloc[0]["count"])
        n_types   = len(type_counts)
        rare_type = type_counts.iloc[-1]["type"].capitalize()
        st.markdown(
            f'<p class="chart-conclusion"><b>{top_type}</b> es el tipo primario más '
            f'frecuente con <b>{top_count}</b> Pokémon. La Gen&nbsp;I cuenta con '
            f'<b>{n_types}</b> tipos distintos; <b>{rare_type}</b> es el menos '
            f'representado.</p>',
            unsafe_allow_html=True,
        )

    with col_right:
        tier_counts = df["power_tier"].value_counts().reset_index()
        tier_counts.columns = ["Tier", "Cantidad"]
        fig2 = px.pie(
            tier_counts, names="Tier", values="Cantidad",
            hole=0.5,
            color_discrete_sequence=[ACCENT, "#10B981", "#F59E0B", "#EF4444", "#90A4AE"],
            title="Distribución por Tier de Poder",
        )
        fig2.update_traces(
            textinfo="label+percent",
            marker=dict(line=dict(color="white", width=2)),
        )
        fig2.update_layout(
            height=420, margin=dict(t=50, b=80, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="top", y=-0.12, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})
        top_tier       = tier_counts.iloc[0]["Tier"]
        top_tier_count = int(tier_counts.iloc[0]["Cantidad"])
        total_poke     = int(tier_counts["Cantidad"].sum())
        pct_tier       = round(top_tier_count / total_poke * 100)
        st.markdown(
            f'<p class="chart-conclusion">El tier <b>{top_tier}</b> agrupa la mayor '
            f'cantidad de Pokémon (<b>{top_tier_count}</b> de {total_poke}, '
            f'{pct_tier}%). La distribución confirma que la mayoría de la Gen&nbsp;I '
            f'tiene un poder base intermedio.</p>',
            unsafe_allow_html=True,
        )

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        top = df.nlargest(15, "bst")[["name", "bst", "type_primary", "id"]].sort_values("bst")
        top_colors = [TYPE_COLORS.get(t, "#90A4AE") for t in top["type_primary"]]
        fig3 = go.Figure(go.Bar(
            x=top["bst"], y=top["name"].str.capitalize(), orientation="h",
            marker=dict(color=top_colors, line=dict(color="white", width=0.4)),
            text=top["bst"], textposition="outside",
            hovertemplate="<b>%{y}</b><br>BST: %{x}<extra></extra>",
        ))
        bst_min = int(top["bst"].min())
        bst_max = int(top["bst"].max())
        x_range_start = bst_min - 140
        x_sprite = bst_min - 12   # right edge of each sprite, just before bars
        sprite_bst_width = 90     # sprite width in BST data units
        fig3.update_layout(
            title="Top 15 por BST", height=520,
            template="plotly_white", margin=dict(t=50, b=50, l=90, r=60),
            xaxis=dict(range=[x_range_start, bst_max + 40]),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        n = len(top)
        for i, (_, row) in enumerate(top.iterrows()):
            sprite = (
                "https://raw.githubusercontent.com/PokeAPI/sprites/master"
                f"/sprites/pokemon/{int(row['id'])}.png"
            )
            y_pos = (i + 0.5) / n
            fig3.add_layout_image(
                source=sprite,
                xref="x", yref="paper",
                x=x_sprite, y=y_pos,
                sizex=sprite_bst_width, sizey=0.058,
                xanchor="right", yanchor="middle",
                layer="above",
            )
        st.plotly_chart(fig3, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

        leader     = top.nlargest(1, "bst")["name"].iloc[0].capitalize()
        leader_bst = int(top["bst"].max())
        dom_type   = top["type_primary"].value_counts().idxmax().capitalize()
        avg_top15  = int(top["bst"].mean())
        avg_all    = int(df["bst"].mean())
        st.markdown(
            f'<p class="chart-conclusion"><b>{leader}</b> encabeza el ranking con '
            f'<b>{leader_bst}</b> puntos de BST. El tipo <b>{dom_type}</b> es el más '
            f'representado en el top&nbsp;15. El BST promedio de este grupo '
            f'({avg_top15}&nbsp;pts) supera en <b>{avg_top15 - avg_all}&nbsp;pts</b> '
            f'al promedio general de la Generación&nbsp;I.</p>',
            unsafe_allow_html=True,
        )

    with col_b:
        avg_by_type = (
            df.groupby("type_primary")[["attack", "defense"]].mean().round(1).reset_index()
        )
        tc_list = [TYPE_COLORS.get(t, "#90A4AE") for t in avg_by_type["type_primary"]]
        ax_min = min(avg_by_type["attack"].min(), avg_by_type["defense"].min()) * 0.88
        ax_max = max(avg_by_type["attack"].max(), avg_by_type["defense"].max()) * 1.12
        fig4 = go.Figure()
        fig4.add_shape(
            type="line", x0=ax_min, y0=ax_min, x1=ax_max, y1=ax_max,
            line=dict(color="#CBD5E1", dash="dot", width=1.5),
        )
        fig4.add_trace(go.Scatter(
            x=avg_by_type["attack"], y=avg_by_type["defense"],
            mode="markers+text",
            marker=dict(color=tc_list, size=14, opacity=0.88,
                        line=dict(color="white", width=1.5)),
            text=avg_by_type["type_primary"],
            textposition="top center",
            textfont=dict(size=9, color=TEXT),
            hovertemplate="<b>%{text}</b><br>Ataque: %{x}<br>Defensa: %{y}<extra></extra>",
        ))
        fig4.update_layout(
            title="Ataque vs Defensa Promedio por Tipo",
            xaxis_title="Ataque Promedio", yaxis_title="Defensa Promedio",
            height=520, template="plotly_white",
            margin=dict(t=50, b=50, l=50, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[ax_min, ax_max]),
            yaxis=dict(range=[ax_min, ax_max]),
            showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

        most_off = avg_by_type.assign(d=avg_by_type["attack"] - avg_by_type["defense"]).nlargest(1, "d")["type_primary"].iloc[0].capitalize()
        most_def = avg_by_type.assign(d=avg_by_type["defense"] - avg_by_type["attack"]).nlargest(1, "d")["type_primary"].iloc[0].capitalize()
        balanced = avg_by_type.assign(d=(avg_by_type["attack"] - avg_by_type["defense"]).abs()).nsmallest(1, "d")["type_primary"].iloc[0].capitalize()
        st.markdown(
            f'<p class="chart-conclusion">Los puntos sobre la diagonal punteada son más '
            f'defensivos que ofensivos. <b>{most_off}</b> es el tipo más ofensivo y '
            f'<b>{most_def}</b> el más defensivo. <b>{balanced}</b> muestra el mejor '
            f'equilibrio entre Ataque y Defensa.</p>',
            unsafe_allow_html=True,
        )


def tab_stats(df: pd.DataFrame) -> None:
    page_header("Estadísticas",
                "Descubre patrones ocultos en las estadísticas base de cada Pokémon")

    # ── Selectores encima del scatter, alineados sobre col2 ──────────────────
    _, ctrl_col = st.columns(2)
    with ctrl_col:
        xc, yc = st.columns(2)
        with xc:
            x_stat = st.selectbox("Eje X", options=STAT_COLS,
                                   format_func=lambda s: STAT_LABELS[s], index=1)
        with yc:
            y_stat = st.selectbox("Eje Y", options=STAT_COLS,
                                   format_func=lambda s: STAT_LABELS[s], index=2)

    col1, col2 = st.columns(2)

    with col1:
        corr = df[STAT_COLS].corr().round(2)
        labels = list(STAT_LABELS.values())
        fig = go.Figure(go.Heatmap(
            z=corr.values, x=labels, y=labels, colorscale="RdBu", zmid=0,
            text=corr.values.round(2), texttemplate="%{text}",
            hovertemplate="<b>%{y} vs %{x}</b><br>r = %{z:.2f}<extra></extra>",
        ))
        fig.update_layout(title="Correlación de Estadísticas Base", height=420,
                          template="plotly_white", margin=dict(t=50, b=40, l=10, r=10),
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

        corr_pairs = [
            (corr.iloc[i, j], STAT_COLS[i], STAT_COLS[j])
            for i in range(len(STAT_COLS))
            for j in range(i + 1, len(STAT_COLS))
        ]
        max_r, max_a, max_b = max(corr_pairs, key=lambda x: x[0])
        min_r, min_a, min_b = min(corr_pairs, key=lambda x: x[0])
        st.markdown(
            f'<p class="chart-conclusion"><b>{STAT_LABELS[max_a]}</b> y '
            f'<b>{STAT_LABELS[max_b]}</b> tienen la mayor correlación (r&nbsp;=&nbsp;{max_r}): '
            f'los Pokémon fuertes en una tienden a serlo en la otra. '
            f'<b>{STAT_LABELS[min_a]}</b> y <b>{STAT_LABELS[min_b]}</b> son las stats '
            f'menos relacionadas (r&nbsp;=&nbsp;{min_r}).</p>',
            unsafe_allow_html=True,
        )

    with col2:
        colors = [TYPE_COLORS.get(t, "#90A4AE") for t in df["type_primary"]]
        fig2 = go.Figure(go.Scatter(
            x=df[x_stat], y=df[y_stat], mode="markers",
            marker=dict(color=colors, size=8, opacity=0.8,
                        line=dict(color="white", width=0.5)),
            text=df["name"].str.capitalize(),
            hovertemplate=(
                "<b>%{text}</b><br>"
                f"{STAT_LABELS[x_stat]}: %{{x}}<br>"
                f"{STAT_LABELS[y_stat]}: %{{y}}<extra></extra>"
            ),
        ))
        fig2.update_layout(
            title=f"{STAT_LABELS[x_stat]} vs {STAT_LABELS[y_stat]}",
            xaxis_title=STAT_LABELS[x_stat], yaxis_title=STAT_LABELS[y_stat],
            height=420, template="plotly_white", margin=dict(t=50, b=50, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

        pearson_r = round(df[[x_stat, y_stat]].corr().iloc[0, 1], 2)
        strength  = "fuerte" if abs(pearson_r) > 0.5 else "moderada" if abs(pearson_r) > 0.3 else "débil"
        direction = "positiva" if pearson_r > 0 else "negativa"
        top_x = df.nlargest(1, x_stat)[["name", x_stat]].iloc[0]
        top_y = df.nlargest(1, y_stat)[["name", y_stat]].iloc[0]
        st.markdown(
            f'<p class="chart-conclusion">Correlación <b>{direction} {strength}</b> '
            f'(r&nbsp;=&nbsp;{pearson_r}) entre {STAT_LABELS[x_stat]} y {STAT_LABELS[y_stat]}. '
            f'<b>{top_x["name"].capitalize()}</b> lidera en {STAT_LABELS[x_stat]} '
            f'({int(top_x[x_stat])}&nbsp;pts) y <b>{top_y["name"].capitalize()}</b> '
            f'en {STAT_LABELS[y_stat]} ({int(top_y[y_stat])}&nbsp;pts).</p>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        f'<p class="section-title">Stats promedio por tipo</p>',
        unsafe_allow_html=True,
    )
    avg = df.groupby("type_primary")[STAT_COLS].mean().round(1)
    avg.columns = list(STAT_LABELS.values())
    avg = avg.sort_values("Ataque", ascending=False)
    fig3 = px.imshow(avg, color_continuous_scale="Blues", aspect="auto",
                     title="Heatmap de stats promedio por tipo",
                     labels=dict(color="Promedio"))
    fig3.update_layout(height=420, margin=dict(t=50, b=50, l=10, r=10),
                       paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

    avg_raw = df.groupby("type_primary")[STAT_COLS].mean()
    best_atk = avg_raw["attack"].idxmax().capitalize()
    best_def = avg_raw["defense"].idxmax().capitalize()
    best_spd = avg_raw["speed"].idxmax().capitalize()
    weakest  = avg_raw.mean(axis=1).idxmin().capitalize()
    st.markdown(
        f'<p class="chart-conclusion"><b>{best_atk}</b> domina en Ataque promedio y '
        f'<b>{best_def}</b> destaca en Defensa. <b>{best_spd}</b> es el tipo más veloz de '
        f'la primera generación. <b>{weakest}</b> presenta los valores globales más bajos '
        f'en todas las estadísticas.</p>',
        unsafe_allow_html=True,
    )


def tab_gallery(df: pd.DataFrame) -> None:
    page_header("Galería", "Arte oficial de los 151 Pokémon · Ordena, filtra y explora")

    col_ord, col_cols, col_search = st.columns([2, 2, 3])
    with col_ord:
        order = st.selectbox(
            "Ordenar por", ["bst", "name", "attack", "speed", "hp"],
            format_func=lambda s: STAT_LABELS.get(s, s.upper()),
        )
    with col_cols:
        n_cols = st.slider("Columnas", 3, 6, 5)
    with col_search:
        search = st.text_input("Buscar Pokémon", placeholder="Ej: charizard")

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["name"].str.contains(search.lower(), na=False)]
    filtered = filtered.sort_values(order, ascending=(order == "name")).reset_index(drop=True)

    if filtered.empty:
        st.info("Ningún Pokémon coincide con la búsqueda.")
        return

    st.caption(f"{len(filtered)} Pokémon mostrados")
    rows = [filtered.iloc[i:i + n_cols] for i in range(0, len(filtered), n_cols)]
    for row_df in rows:
        cols = st.columns(n_cols)
        for col, (_, poke) in zip(cols, row_df.iterrows()):
            artwork_src = ARTWORK.format(id=int(poke["id"]))
            type_color  = TYPE_COLORS.get(poke["type_primary"], "#90A4AE")
            type2_badge = ""
            if pd.notna(poke.get("type_secondary")):
                t2c = TYPE_COLORS.get(poke["type_secondary"], "#90A4AE")
                type2_badge = (
                    f'<span class="type-badge" style="background:{t2c}">'
                    f'{poke["type_secondary"]}</span>'
                )
            bst_val = int(poke["bst"]) if pd.notna(poke.get("bst")) else "—"
            with col:
                st.markdown(
                    f'<div class="poke-card">'
                    f'<img src="{artwork_src}" width="88"'
                    f' style="filter:drop-shadow(0 4px 8px rgba(0,0,0,0.1))"/>'
                    f'<p class="poke-name">#{int(poke["id"])} {poke["name"]}</p>'
                    f'<span class="type-badge" style="background:{type_color}">'
                    f'{poke["type_primary"]}</span>'
                    f'{type2_badge}'
                    f'<p class="bst-label">BST: <b style="color:{ACCENT}">{bst_val}</b></p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def tab_explorer(df: pd.DataFrame) -> None:
    page_header("Comparación", "Cara a cara · Compara dos Pokémon stat por stat y descubre quién gana")

    poke_names = sorted(df["name"].tolist())
    default_a = poke_names.index("bulbasaur") if "bulbasaur" in poke_names else 0
    default_b = poke_names.index("charmander") if "charmander" in poke_names else min(3, len(poke_names) - 1)

    col_a, col_vs, col_b = st.columns([5, 1, 5])
    with col_a:
        name_a = st.selectbox("Pokémon A", options=poke_names, index=default_a,
                               format_func=str.capitalize, key="cmp_a")
    with col_vs:
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:center;height:72px">'
            f'<p class="pokemon-brand" style="color:{ACCENT};font-size:0.85rem;margin:0">VS</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_b:
        name_b = st.selectbox("Pokémon B", options=poke_names, index=default_b,
                               format_func=str.capitalize, key="cmp_b")

    if name_a == name_b:
        st.markdown(
            f'<div style="text-align:center;padding:2.5rem 1rem;background:#F8FAFF;'
            f'border-radius:20px;border:2px dashed {ACCENT}33;margin-top:1rem">'
            f'<p class="pokemon-brand" style="color:{ACCENT};font-size:0.80rem;margin:0 0 0.6rem">!</p>'
            f'<p style="color:{TEXT_SUB};font-size:0.88rem;margin:0">'
            f'Selecciona dos Pokémon diferentes para ver la comparación.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        return

    poke_a = df[df["name"] == name_a].iloc[0]
    poke_b = df[df["name"] == name_b].iloc[0]
    color_a = TYPE_COLORS.get(poke_a["type_primary"], ACCENT)
    color_b = TYPE_COLORS.get(poke_b["type_primary"], "#EF4444")
    CMP_A, CMP_B = ACCENT, "#F59E0B"  # colores fijos para gráficas comparativas
    vals_a = [int(poke_a[s]) for s in STAT_COLS]
    vals_b = [int(poke_b[s]) for s in STAT_COLS]
    stat_labels_list = list(STAT_LABELS.values())

    def _poke_panel(poke, accent_color: str) -> str:
        type2_badge = ""
        if pd.notna(poke.get("type_secondary")):
            t2c = TYPE_COLORS.get(poke["type_secondary"], "#90A4AE")
            type2_badge = (
                f'<span class="type-badge" style="background:{t2c};font-size:0.72rem">'
                f'{poke["type_secondary"]}</span> '
            )
        artwork = ARTWORK.format(id=int(poke["id"]))
        return (
            f'<div style="text-align:center;background:{CARD_BG};border-radius:20px;'
            f'padding:1.5rem 1rem;box-shadow:0 4px 18px rgba(0,0,0,0.07);">'
            f'<img src="{artwork}" width="140" '
            f'style="filter:drop-shadow(0 6px 16px rgba(0,0,0,0.15));animation:fadeUp 0.7s ease"/>'
            f'<p style="font-size:1.1rem;font-weight:700;color:{TEXT};'
            f'margin:0.6rem 0 0.3rem;text-transform:capitalize">#{int(poke["id"])} {poke["name"]}</p>'
            f'<span class="type-badge" style="background:{accent_color};font-size:0.72rem">'
            f'{poke["type_primary"]}</span> '
            f'{type2_badge}'
            f'<p style="color:{TEXT_SUB};font-size:0.8rem;margin:0.6rem 0 0">'
            f'BST: <b style="color:{accent_color}">{int(poke["bst"])}</b></p>'
            f'</div>'
        )

    col_img_a, col_radar, col_img_b = st.columns([1, 1.4, 1])

    with col_img_a:
        st.markdown(_poke_panel(poke_a, color_a), unsafe_allow_html=True)

    with col_radar:
        labels = stat_labels_list
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals_a + [vals_a[0]], theta=labels + [labels[0]],
            fill="toself", fillcolor=_hex_to_rgba(CMP_A, 0.20),
            line=dict(color=CMP_A, width=2.5),
            name=poke_a["name"].capitalize(),
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=vals_b + [vals_b[0]], theta=labels + [labels[0]],
            fill="toself", fillcolor=_hex_to_rgba(CMP_B, 0.20),
            line=dict(color=CMP_B, width=2.5),
            name=poke_b["name"].capitalize(),
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 200], showticklabels=False,
                                gridcolor="#E5E7EB"),
                angularaxis=dict(tickfont=dict(size=11, color=TEXT)),
            ),
            legend=dict(orientation="h", yanchor="top", y=-0.14, x=0.5, xanchor="center"),
            showlegend=True,
            height=380,
            margin=dict(t=30, b=80, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            title=dict(text="Comparación de Stats", font=dict(size=13, color=TEXT), x=0.5),
        )
        st.plotly_chart(fig_radar, use_container_width=True,
                        config={"scrollZoom": False, "displayModeBar": False})

    with col_img_b:
        st.markdown(_poke_panel(poke_b, color_b), unsafe_allow_html=True)

    st.markdown("<div style='margin:1rem 0 0.2rem'></div>", unsafe_allow_html=True)

    # ── Tarjetas de ganador por stat ──────────────────────────────────────────
    st.markdown(
        f'<p class="section-title" style="margin-top:0.4rem">Resultado por estadística</p>',
        unsafe_allow_html=True,
    )
    stat_result_cols = st.columns(len(STAT_COLS))
    for col, label, va, vb in zip(stat_result_cols, stat_labels_list, vals_a, vals_b):
        if va > vb:
            winner, w_val, badge_color = poke_a["name"].capitalize(), va, CMP_A
        elif vb > va:
            winner, w_val, badge_color = poke_b["name"].capitalize(), vb, CMP_B
        else:
            winner, w_val, badge_color = "Empate", va, "#90A4AE"
        with col:
            st.markdown(
                f'<div class="kpi-card" style="border-left-color:{badge_color};text-align:center;'
                f'padding:0.7rem 0.5rem">'
                f'<p class="kpi-label">{label}</p>'
                f'<p class="kpi-value" style="color:{badge_color};font-size:1.15rem">{w_val}</p>'
                f'<p style="font-size:0.68rem;color:{TEXT_SUB};margin:0.25rem 0 0;'
                f'text-transform:capitalize;font-weight:600">{winner}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Conclusión automática ──────────────────────────────────────────────────
    wins_a = sum(1 for a, b in zip(vals_a, vals_b) if a > b)
    wins_b = sum(1 for a, b in zip(vals_a, vals_b) if b > a)
    ties   = sum(1 for a, b in zip(vals_a, vals_b) if a == b)
    bst_a, bst_b = int(poke_a["bst"]), int(poke_b["bst"])
    bst_winner = poke_a["name"].capitalize() if bst_a >= bst_b else poke_b["name"].capitalize()
    bst_diff = abs(bst_a - bst_b)
    best_a_idx = max(range(len(vals_a)), key=lambda i: vals_a[i] - vals_b[i])
    best_b_idx = max(range(len(vals_b)), key=lambda i: vals_b[i] - vals_a[i])

    tie_txt = f" ({ties} empate{'s' if ties > 1 else ''})" if ties else ""
    conclusion = (
        f'<b>{poke_a["name"].capitalize()}</b> supera en <b>{wins_a}</b> stats, '
        f'<b>{poke_b["name"].capitalize()}</b> en <b>{wins_b}</b>{tie_txt}. '
        f'El BST total favorece a <b>{bst_winner}</b> por <b>{bst_diff}&nbsp;pts</b>. '
        f'<b>{poke_a["name"].capitalize()}</b> destaca en '
        f'<b>{stat_labels_list[best_a_idx]}</b> '
        f'({vals_a[best_a_idx]} vs {vals_b[best_a_idx]}), mientras que '
        f'<b>{poke_b["name"].capitalize()}</b> sobresale en '
        f'<b>{stat_labels_list[best_b_idx]}</b> '
        f'({vals_b[best_b_idx]} vs {vals_a[best_b_idx]}).'
    )
    st.markdown(f'<p class="chart-conclusion">{conclusion}</p>', unsafe_allow_html=True)

    # ── Gráfico de barras agrupadas por stat ──────────────────────────────────
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name=poke_a["name"].capitalize(), x=stat_labels_list, y=vals_a,
        marker_color=CMP_A, opacity=0.88,
        text=vals_a, textposition="outside",
        hovertemplate="<b>" + poke_a["name"].capitalize() + "</b><br>%{x}: %{y}<extra></extra>",
    ))
    fig_bar.add_trace(go.Bar(
        name=poke_b["name"].capitalize(), x=stat_labels_list, y=vals_b,
        marker_color=CMP_B, opacity=0.88,
        text=vals_b, textposition="outside",
        hovertemplate="<b>" + poke_b["name"].capitalize() + "</b><br>%{x}: %{y}<extra></extra>",
    ))
    fig_bar.update_layout(
        barmode="group",
        title="Comparación estadística detallada",
        height=400,
        margin=dict(t=50, b=50, l=10, r=10),
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="top", y=-0.14, x=0.5, xanchor="center"),
        yaxis=dict(range=[0, max(max(vals_a), max(vals_b)) * 1.22]),
    )
    st.plotly_chart(fig_bar, use_container_width=True,
                    config={"scrollZoom": False, "displayModeBar": False})


def tab_pipeline() -> None:
    page_header("Resumen ETL",
                "De PokéAPI a SQLite · Arquitectura técnica del proyecto paso a paso")

    phases = [
        ("Extract", "#2962FF",
         "**Fuente:** PokéAPI REST\n\n"
         "**URL:** `https://pokeapi.co/api/v2`\n\n"
         "**Registros:** 151 Pokémon (Gen I)\n\n"
         "**Rate limit:** 100 req/min\n\n"
         "**Reintentos:** tenacity (exp. backoff)\n\n"
         "**Salida:** `data/raw/pokemon_raw.json`"),
        ("Transform", "#10B981",
         "**Entrada:** JSON anidado (arrays)\n\n"
         "**Operaciones:**\n"
         "- Desanida types, stats, abilities\n"
         "- Calcula BST (suma 6 stats)\n"
         "- Clasifica generación por ID\n"
         "- Calcula altura_m, peso_kg, IMC\n"
         "- Categoriza en power_tier\n"
         "- Genera sprite_url por ID\n\n"
         "**Salida:** `pokemon_clean.csv` (22 cols)"),
        ("Load", "#F59E0B",
         "**Destinos:**\n"
         "- SQLite → `pokemon.db`\n"
         "- CSV procesado (referencia)\n"
         "- `dashboard.html` (Plotly)\n"
         "- `stats_report.png` (Matplotlib)\n\n"
         "**Esta app:** Streamlit sobre SQLite\n\n"
         "**Queries:** pandas + sqlite3"),
    ]

    cols = st.columns(3)
    for col, (phase, color, content) in zip(cols, phases):
        with col:
            st.markdown(
                f'<div class="card" style="border-top:4px solid {color}">'
                f'<p style="font-size:1.05rem;font-weight:700;color:{color};margin:0 0 0.8rem">'
                f'{phase}</p></div>',
                unsafe_allow_html=True,
            )
            st.markdown(content)

    st.markdown("<div style='margin-top:1.8rem'></div>", unsafe_allow_html=True)

    narrative = [
        (
            "¿Por qué?",
            "#2962FF",
            "",
            "La mayoría de los datos en el mundo real no llegan limpios ni estructurados. "
            "Este proyecto nació con el objetivo de demostrar un flujo de ingeniería de datos "
            "completo y reproducible: desde una fuente pública hasta un dashboard interactivo, "
            "pasando por todas las etapas de transformación. Se eligió PokéAPI porque ofrece "
            "datos reales, anidados y con complejidad suficiente para justificar un pipeline "
            "real, sin depender de datos ficticios ni datasets preconstruidos."
        ),
        (
            "¿Qué?",
            "#10B981",
            "",
            "Se extrajeron los 151 Pokémon de la Primera Generación desde la PokéAPI, "
            "una API REST pública con más de 300 millones de llamadas mensuales. "
            "El resultado es un dataset limpio de 22 columnas que incluye estadísticas base, "
            "tipos, dimensiones físicas, clasificación de poder y URLs de sprites, "
            "almacenado en SQLite y expuesto en este dashboard para análisis interactivo."
        ),
        (
            "¿Cómo?",
            "#F59E0B",
            "",
            "El pipeline se construyó en Python puro con tres capas bien separadas. "
            "En la extracción, se utilizó <b>requests</b> con reintentos automáticos via "
            "<b>tenacity</b> para respetar el rate limit de la API (100 req/min). "
            "En la transformación, <b>pandas</b> desanidó arrays JSON, calculó el BST "
            "(suma de 6 stats), derivó variables físicas y categorizó cada Pokémon en un "
            "tier de poder. En la carga, <b>sqlite3</b> persiste el dataset para consultas "
            "eficientes, mientras Streamlit y Plotly construyen todas las visualizaciones "
            "en tiempo real sobre esa misma base de datos."
        ),
    ]

    for title, color, icon, text in narrative:
        st.markdown(
            f'<div style="background:{CARD_BG};border-radius:16px;padding:1.4rem 1.6rem;'
            f'box-shadow:0 2px 12px rgba(0,0,0,0.06);margin-bottom:1rem;'
            f'border-left:4px solid {color}">'
            f'<p style="font-size:0.90rem;font-weight:700;color:{color};margin:0 0 0.5rem">'
            f'{(icon + " ") if icon else ""}{title}</p>'
            f'<p style="font-size:0.88rem;color:{TEXT};line-height:1.75;margin:0">{text}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


def main() -> None:
    inject_css()
    df_full = load_data()
    current_page, df = sidebar_nav_and_filters(df_full)

    _logo_path = Path(__file__).parent / "assets" / "Font-pokemon.png"
    _logo_b64  = base64.b64encode(_logo_path.read_bytes()).decode()
    st.markdown(
        f'<div style="margin-bottom:1.2rem">'
        f'<img src="data:image/png;base64,{_logo_b64}"'
        f' style="height:58px;max-width:100%;display:block"/>'
        f'<p class="pokemon-brand" style="color:{TEXT_SUB};font-size:0.55rem;margin:0.5rem 0 0">'
        f'Dashboard de Análisis · Generación I</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Ningún Pokémon coincide con los filtros seleccionados.")
        return

    if current_page == "Vista General":
        tab_overview(df, df_full)
    elif current_page == "Estadísticas":
        tab_stats(df)
    elif current_page == "Galería":
        tab_gallery(df)
    elif current_page == "Comparación":
        tab_explorer(df)
    elif current_page == "Resumen ETL":
        tab_pipeline()


if __name__ == "__main__":
    main()
