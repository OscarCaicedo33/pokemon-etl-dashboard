"""
Fase Load: exporta el dataset limpio a SQLite y genera visualizaciones.
"""

import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots
from loguru import logger

from ..config import PROCESSED_CSV_PATH, SQLITE_DB_PATH, DASHBOARD_HTML_PATH, STATS_REPORT_PATH


def load_to_sqlite(df: pd.DataFrame) -> None:
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(SQLITE_DB_PATH) as conn:
        df.to_sql("pokemon", conn, if_exists="replace", index=False)
    logger.success(f"SQLite actualizado: {SQLITE_DB_PATH} ({len(df)} registros)")


# ── Paleta por tipo Pokemon ────────────────────────────────────────────────────
TYPE_COLORS = {
    "normal": "#A8A878", "fire": "#F08030", "water": "#6890F0",
    "electric": "#F8D030", "grass": "#78C850", "ice": "#98D8D8",
    "fighting": "#C03028", "poison": "#A040A0", "ground": "#E0C068",
    "flying": "#A890F0", "psychic": "#F85888", "bug": "#A8B820",
    "rock": "#B8A038", "ghost": "#705898", "dragon": "#7038F8",
    "dark": "#705848", "steel": "#B8B8D0", "fairy": "#EE99AC",
}

STAT_LABELS = {
    "hp": "HP", "attack": "Ataque", "defense": "Defensa",
    "special_attack": "Sp. Ataque", "special_defense": "Sp. Defensa", "speed": "Velocidad",
}

PALETTE_BLUE = "#1565C0"
PALETTE_ORANGE = "#E65100"
PALETTE_GREEN = "#2E7D32"
PALETTE_PURPLE = "#6A1B9A"
BG_COLOR = "#FAFAFA"
GRID_COLOR = "#EEEEEE"


def generate_dashboard(df: pd.DataFrame) -> None:
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "Distribucion de Tipos Primarios",
            "Top 15 Pokemon por BST",
            "Correlacion de Estadisticas Base",
            "BST por Generacion (Boxplot)",
            "Ataque vs Defensa",
            "Distribucion de BST",
        ),
        specs=[
            [{"type": "bar"},     {"type": "bar"}],
            [{"type": "heatmap"}, {"type": "box"}],
            [{"type": "scatter"}, {"type": "histogram"}],
        ],
        vertical_spacing=0.10,
        horizontal_spacing=0.08,
    )

    # ── 1. Distribución de tipos ───────────────────────────────────────────────
    type_counts = df["type_primary"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    bar_colors = [TYPE_COLORS.get(t, "#90A4AE") for t in type_counts["type"]]
    fig.add_trace(
        go.Bar(
            x=type_counts["type"], y=type_counts["count"],
            name="Tipos",
            marker=dict(color=bar_colors, line=dict(color="white", width=0.5)),
            text=type_counts["count"], textposition="outside",
            hovertemplate="<b>%{x}</b><br>Cantidad: %{y}<extra></extra>",
        ),
        row=1, col=1,
    )

    # ── 2. Top 15 por BST ─────────────────────────────────────────────────────
    top15 = df.nlargest(15, "bst")[["name", "bst", "type_primary"]].sort_values("bst")
    top_colors = [TYPE_COLORS.get(t, "#90A4AE") for t in top15["type_primary"]]
    fig.add_trace(
        go.Bar(
            x=top15["bst"], y=top15["name"], orientation="h",
            name="BST",
            marker=dict(color=top_colors, line=dict(color="white", width=0.5)),
            text=top15["bst"], textposition="outside",
            hovertemplate="<b>%{y}</b><br>BST: %{x}<extra></extra>",
        ),
        row=1, col=2,
    )

    # ── 3. Heatmap de correlación ──────────────────────────────────────────────
    stat_cols = list(STAT_LABELS.keys())
    corr = df[stat_cols].corr().round(2)
    labels = list(STAT_LABELS.values())
    fig.add_trace(
        go.Heatmap(
            z=corr.values, x=labels, y=labels,
            colorscale="RdBu", zmid=0,
            text=corr.values.round(2),
            texttemplate="%{text}",
            showscale=True,
            hovertemplate="<b>%{y} vs %{x}</b><br>r = %{z}<extra></extra>",
        ),
        row=2, col=1,
    )

    # ── 4. Boxplot BST por generación ─────────────────────────────────────────
    gen_palette = ["#1565C0", "#E65100", "#2E7D32", "#6A1B9A", "#AD1457",
                   "#00838F", "#4E342E", "#37474F"]
    for i, gen in enumerate(sorted(df["generation"].dropna().unique())):
        subset = df[df["generation"] == gen]["bst"]
        fig.add_trace(
            go.Box(
                y=subset, name=f"Gen {int(gen)}",
                marker_color=gen_palette[i % len(gen_palette)],
                showlegend=False,
                hovertemplate="<b>Gen %{name}</b><br>BST: %{y}<extra></extra>",
            ),
            row=2, col=2,
        )

    # ── 5. Scatter Ataque vs Defensa ──────────────────────────────────────────
    scatter_colors = [TYPE_COLORS.get(t, "#90A4AE") for t in df["type_primary"]]
    fig.add_trace(
        go.Scatter(
            x=df["attack"], y=df["defense"], mode="markers",
            name="Pokemon",
            marker=dict(color=scatter_colors, size=7, opacity=0.75,
                        line=dict(color="white", width=0.4)),
            text=df["name"],
            hovertemplate="<b>%{text}</b><br>Ataque: %{x}<br>Defensa: %{y}<extra></extra>",
        ),
        row=3, col=1,
    )

    # ── 6. Histograma BST ─────────────────────────────────────────────────────
    fig.add_trace(
        go.Histogram(
            x=df["bst"], nbinsx=25,
            name="BST",
            marker=dict(color=PALETTE_ORANGE, line=dict(color="white", width=0.5)),
            hovertemplate="BST %{x}<br>Cantidad: %{y}<extra></extra>",
        ),
        row=3, col=2,
    )

    # ── Layout global ──────────────────────────────────────────────────────────
    fig.update_layout(
        title=dict(
            text="<b>Pokemon ETL — Dashboard Analitico</b>"
                 "<br><sup>Generacion I (151 Pokemon) · Fuente: PokéAPI</sup>",
            x=0.5, xanchor="center", font=dict(size=20),
        ),
        height=1100,
        showlegend=False,
        template="plotly_white",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family="Arial, sans-serif", size=11),
    )

    # Etiquetas de ejes
    fig.update_xaxes(title_text="Tipo", row=1, col=1, tickangle=-35)
    fig.update_yaxes(title_text="Cantidad", row=1, col=1)
    fig.update_xaxes(title_text="BST (Base Stat Total)", row=1, col=2)
    fig.update_xaxes(title_text="Generacion", row=2, col=2)
    fig.update_yaxes(title_text="BST", row=2, col=2)
    fig.update_xaxes(title_text="Ataque", row=3, col=1)
    fig.update_yaxes(title_text="Defensa", row=3, col=1)
    fig.update_xaxes(title_text="BST (Base Stat Total)", row=3, col=2)
    fig.update_yaxes(title_text="Frecuencia", row=3, col=2)

    DASHBOARD_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(DASHBOARD_HTML_PATH))
    logger.success(f"Dashboard guardado en: {DASHBOARD_HTML_PATH}")


def generate_static_report(df: pd.DataFrame) -> None:
    stat_cols = list(STAT_LABELS.keys())
    stat_display = list(STAT_LABELS.values())

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle(
        "Pokemon ETL — Reporte Estadistico  |  Generacion I (151 Pokemon)",
        fontsize=15, fontweight="bold", y=0.98,
    )
    fig.patch.set_facecolor(BG_COLOR)
    for ax in axes.flat:
        ax.set_facecolor(BG_COLOR)

    # ── 1. Distribución de tipos ───────────────────────────────────────────────
    type_counts = df["type_primary"].value_counts()
    colors = [TYPE_COLORS.get(t, "#90A4AE") for t in type_counts.index]
    axes[0, 0].barh(type_counts.index, type_counts.values, color=colors, edgecolor="white")
    axes[0, 0].set_title("Tipos Primarios mas comunes", fontweight="bold", pad=8)
    axes[0, 0].set_xlabel("Cantidad de Pokemon")
    axes[0, 0].invert_yaxis()
    for i, v in enumerate(type_counts.values):
        axes[0, 0].text(v + 0.2, i, str(v), va="center", fontsize=8)

    # ── 2. Top 15 por BST ─────────────────────────────────────────────────────
    top15 = df.nlargest(15, "bst")[["name", "bst", "type_primary"]].sort_values("bst")
    bst_colors = [TYPE_COLORS.get(t, "#90A4AE") for t in top15["type_primary"]]
    axes[0, 1].barh(top15["name"], top15["bst"], color=bst_colors, edgecolor="white")
    axes[0, 1].set_title("Top 15 Pokemon por BST", fontweight="bold", pad=8)
    axes[0, 1].set_xlabel("BST (Base Stat Total)")
    for i, v in enumerate(top15["bst"]):
        axes[0, 1].text(v + 1, i, str(v), va="center", fontsize=8)

    # ── 3. Distribución de BST ────────────────────────────────────────────────
    axes[0, 2].hist(df["bst"], bins=25, color=PALETTE_ORANGE, edgecolor="white", linewidth=0.6)
    axes[0, 2].axvline(df["bst"].mean(), color=PALETTE_BLUE, linestyle="--",
                       linewidth=1.4, label=f"Media: {df['bst'].mean():.0f}")
    axes[0, 2].axvline(df["bst"].median(), color=PALETTE_GREEN, linestyle=":",
                       linewidth=1.4, label=f"Mediana: {df['bst'].median():.0f}")
    axes[0, 2].set_title("Distribucion de BST", fontweight="bold", pad=8)
    axes[0, 2].set_xlabel("BST (Base Stat Total)")
    axes[0, 2].set_ylabel("Frecuencia")
    axes[0, 2].legend(fontsize=8)

    # ── 4. Scatter Ataque vs Defensa ──────────────────────────────────────────
    scatter_c = [TYPE_COLORS.get(t, "#90A4AE") for t in df["type_primary"]]
    axes[1, 0].scatter(df["attack"], df["defense"], c=scatter_c,
                       alpha=0.72, s=45, edgecolors="white", linewidths=0.4)
    axes[1, 0].set_title("Ataque vs Defensa (color = tipo)", fontweight="bold", pad=8)
    axes[1, 0].set_xlabel("Ataque")
    axes[1, 0].set_ylabel("Defensa")

    # ── 5. Heatmap de correlación ──────────────────────────────────────────────
    corr = df[stat_cols].corr()
    corr.index = stat_display
    corr.columns = stat_display
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
                ax=axes[1, 1], linewidths=0.5, cbar_kws={"shrink": 0.8})
    axes[1, 1].set_title("Correlacion de Estadisticas Base", fontweight="bold", pad=8)
    axes[1, 1].tick_params(axis="x", rotation=30, labelsize=8)
    axes[1, 1].tick_params(axis="y", rotation=0, labelsize=8)

    # ── 6. Radar promedio por tipo ─────────────────────────────────────────────
    avg_by_type = df.groupby("type_primary")[stat_cols].mean()
    top_types = avg_by_type.mean(axis=1).nlargest(6).index.tolist()
    type_palette = [TYPE_COLORS.get(t, "#90A4AE") for t in top_types]
    x_pos = range(len(stat_cols))
    for t, col in zip(top_types, type_palette):
        axes[1, 2].plot(x_pos, avg_by_type.loc[t, stat_cols].values,
                        marker="o", label=t, color=col, linewidth=1.8, markersize=5)
    axes[1, 2].set_xticks(list(x_pos))
    axes[1, 2].set_xticklabels(stat_display, rotation=20, fontsize=8)
    axes[1, 2].set_title("Stats promedio — Top 6 tipos por BST", fontweight="bold", pad=8)
    axes[1, 2].set_ylabel("Valor promedio")
    axes[1, 2].legend(fontsize=7.5, loc="upper right")

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    STATS_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(STATS_REPORT_PATH), dpi=150, bbox_inches="tight",
                facecolor=BG_COLOR)
    plt.close()
    logger.success(f"Reporte estatico guardado en: {STATS_REPORT_PATH}")


def run_load(df: pd.DataFrame | None = None, generate_viz: bool = True) -> None:
    if df is None:
        logger.info(f"Cargando CSV procesado desde: {PROCESSED_CSV_PATH}")
        df = pd.read_csv(PROCESSED_CSV_PATH)

    load_to_sqlite(df)

    if generate_viz:
        generate_dashboard(df)
        generate_static_report(df)
