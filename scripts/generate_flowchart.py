"""
Genera el diagrama de flujo PNG del pipeline ETL Pokemon.
Uso: python generate_flowchart.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "output" / "etl_flowchart.png"

COLORS = {
    "extract":    "#1565C0",
    "transform":  "#E65100",
    "load":       "#2E7D32",
    "decision":   "#6A1B9A",
    "artifact":   "#37474F",
    "arrow":      "#455A64",
    "bg":         "#FAFAFA",
    "white":      "#FFFFFF",
    "header_bg":  "#1A237E",
    "text_light": "#FFFFFF",
    "text_dark":  "#212121",
    "text_gray":  "#546E7A",
    "success":    "#00897B",
}


def _box(ax, x, y, w, h, color, text, text_size=9, text_color="white",
         radius=0.3, subtext=None):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=1.2, edgecolor=color, facecolor=color, zorder=3,
    )
    ax.add_patch(box)
    if subtext:
        ax.text(x, y + h * 0.12, text, ha="center", va="center",
                fontsize=text_size, fontweight="bold", color=text_color, zorder=4)
        ax.text(x, y - h * 0.22, subtext, ha="center", va="center",
                fontsize=text_size - 1.5, color=text_color, alpha=0.88, zorder=4)
    else:
        ax.text(x, y, text, ha="center", va="center",
                fontsize=text_size, fontweight="bold", color=text_color, zorder=4)


def _diamond(ax, x, y, w, h, color, text):
    dx, dy = w / 2, h / 2
    diamond = plt.Polygon(
        [[x, y + dy], [x + dx, y], [x, y - dy], [x - dx, y]],
        closed=True, facecolor=color, edgecolor=color, linewidth=1.2, zorder=3,
    )
    ax.add_patch(diamond)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=7.5, fontweight="bold", color="white", zorder=4)


def _artifact(ax, x, y, w, h, text, tag):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0,rounding_size=0.15",
        linewidth=1, edgecolor=COLORS["artifact"], facecolor="#ECEFF1", zorder=3,
    )
    ax.add_patch(box)
    ax.text(x - w / 2 + 0.35, y, tag, ha="center", va="center",
            fontsize=8, fontweight="bold", color=COLORS["extract"], zorder=4)
    ax.text(x + 0.1, y, text, ha="center", va="center",
            fontsize=7.8, color=COLORS["artifact"], zorder=4)


def _arrow(ax, x1, y1, x2, y2):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->,head_width=0.35,head_length=0.2",
            color=COLORS["arrow"], lw=1.5,
        ),
        zorder=2,
    )


def _phase_label(ax, x, y, text, color):
    ax.text(x, y, text, ha="center", va="center",
            fontsize=8, fontweight="bold", color=color,
            bbox=dict(boxstyle="round,pad=0.3", fc=color, ec=color, alpha=0.15),
            zorder=5)


def generate():
    fig, ax = plt.subplots(figsize=(14, 18))
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 18)
    ax.axis("off")

    # ── Header ────────────────────────────────────────────────────────────────
    header = FancyBboxPatch((0.5, 16.8), 13, 1,
                            boxstyle="round,pad=0,rounding_size=0.3",
                            facecolor=COLORS["header_bg"], edgecolor="none", zorder=3)
    ax.add_patch(header)
    ax.text(7, 17.45, "POKEMON ETL  --  DIAGRAMA DE FLUJO", ha="center",
            fontsize=14, fontweight="bold", color="white", zorder=4)
    ax.text(7, 17.05, "PokéAPI  -->  Extraccion  -->  Transformacion  -->  Carga  -->  Visualizacion",
            ha="center", fontsize=9, color="#90CAF9", zorder=4)

    # ── CONFIG ────────────────────────────────────────────────────────────────
    _box(ax, 7, 16.0, 4.2, 0.6, "#455A64", "config.py  +  .env",
         text_size=9, radius=0.2)
    _arrow(ax, 7, 15.7, 7, 15.25)

    # ── START ─────────────────────────────────────────────────────────────────
    _box(ax, 7, 15.0, 2.4, 0.55, "#00897B", "INICIO", text_size=11, radius=0.27)
    _arrow(ax, 7, 14.72, 7, 14.2)

    # ══ FASE EXTRACT ══════════════════════════════════════════════════════════
    ax.axhline(y=14.1, xmin=0.04, xmax=0.96, color=COLORS["extract"],
               linewidth=0.6, linestyle="--", alpha=0.45)
    _phase_label(ax, 2.3, 13.8, "FASE  EXTRACT", COLORS["extract"])

    _box(ax, 7, 14.0, 4.4, 0.58, COLORS["extract"],
         "GET /pokemon?limit=N",
         subtext="PokéAPI  |  Rate limit 100 req/min  |  tenacity retry", text_size=9)
    _arrow(ax, 7, 13.71, 7, 13.12)

    _diamond(ax, 7, 12.82, 3.3, 0.72, COLORS["decision"], "HTTP 200?")

    # No -> retry branch
    ax.annotate("", xy=(10.3, 12.82), xytext=(8.65, 12.82),
                arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.18",
                                color=COLORS["arrow"], lw=1.4), zorder=2)
    _box(ax, 11.55, 12.82, 2.3, 0.52, "#B71C1C", "Retry\n(max 3 intentos)", text_size=8)
    ax.annotate("", xy=(11.55, 14.0), xytext=(11.55, 13.08),
                arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.17",
                                color=COLORS["arrow"], lw=1.3, linestyle="dashed"), zorder=2)
    ax.annotate("", xy=(9.2, 14.0), xytext=(11.55, 14.0),
                arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.17",
                                color=COLORS["arrow"], lw=1.3), zorder=2)
    ax.text(10.1, 12.62, "No -->", fontsize=7.5, color=COLORS["text_gray"])
    ax.text(6.6, 12.32, "Si", fontsize=7.5, color=COLORS["text_gray"])

    _arrow(ax, 7, 12.46, 7, 11.88)
    _artifact(ax, 7, 11.65, 4.4, 0.52, "data/raw/pokemon_raw.json", "[JSON]")
    _arrow(ax, 7, 11.39, 7, 10.78)

    # ══ FASE TRANSFORM ════════════════════════════════════════════════════════
    ax.axhline(y=10.7, xmin=0.04, xmax=0.96, color=COLORS["transform"],
               linewidth=0.6, linestyle="--", alpha=0.45)
    _phase_label(ax, 2.4, 10.44, "FASE  TRANSFORM", COLORS["transform"])

    _box(ax, 7, 10.33, 5.0, 0.58, COLORS["transform"],
         "flatten_pokemon()",
         subtext="Desanida types / stats / abilities  (JSON --> columnas planas)", text_size=9)
    _arrow(ax, 7, 10.04, 7, 9.46)

    _box(ax, 7, 9.24, 5.0, 0.52, COLORS["transform"],
         "Calculo de campos derivados",
         subtext="BST · altura_m · peso_kg · IMC · generation · power_tier (pd.cut)", text_size=9)
    _arrow(ax, 7, 8.98, 7, 8.44)

    _diamond(ax, 7, 8.18, 3.5, 0.72, COLORS["decision"], "Valores nulos?")
    ax.annotate("", xy=(10.45, 8.18), xytext=(8.75, 8.18),
                arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.18",
                                color=COLORS["arrow"], lw=1.4), zorder=2)
    _box(ax, 11.65, 8.18, 2.3, 0.52, "#F57F17", "Imputacion\n/ descarte", text_size=8)
    ax.annotate("", xy=(11.65, 9.24), xytext=(11.65, 8.44),
                arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.17",
                                color=COLORS["arrow"], lw=1.3, linestyle="dashed"), zorder=2)
    ax.annotate("", xy=(9.5, 9.24), xytext=(11.65, 9.24),
                arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.17",
                                color=COLORS["arrow"], lw=1.3), zorder=2)
    ax.text(10.1, 7.98, "Si -->", fontsize=7.5, color=COLORS["text_gray"])
    ax.text(6.55, 7.68, "No", fontsize=7.5, color=COLORS["text_gray"])

    _arrow(ax, 7, 7.82, 7, 7.24)
    _artifact(ax, 7, 7.0, 5.0, 0.52, "data/processed/pokemon_clean.csv  (151 filas x 21 columnas)", "[CSV]")
    _arrow(ax, 7, 6.74, 7, 6.14)

    # ══ FASE LOAD ═════════════════════════════════════════════════════════════
    ax.axhline(y=6.06, xmin=0.04, xmax=0.96, color=COLORS["load"],
               linewidth=0.6, linestyle="--", alpha=0.45)
    _phase_label(ax, 2.2, 5.82, "FASE  LOAD", COLORS["load"])

    _box(ax, 7, 5.72, 4.4, 0.58, COLORS["load"],
         "load_to_sqlite()",
         subtext="pandas.to_sql  -->  data/output/pokemon.db  (tabla: pokemon)", text_size=9)
    _arrow(ax, 7, 5.43, 7, 4.86)

    # Bifurcacion dos salidas visuales
    ax.plot([7, 7], [4.86, 4.6], color=COLORS["arrow"], lw=1.5)
    ax.plot([3.8, 10.2], [4.6, 4.6], color=COLORS["arrow"], lw=1.5)
    _arrow(ax, 3.8, 4.6, 3.8, 4.1)
    _arrow(ax, 10.2, 4.6, 10.2, 4.1)
    ax.text(7.1, 4.72, "generate_viz()", fontsize=7.5,
            color=COLORS["text_gray"], ha="center")

    _box(ax, 3.8, 3.82, 4.0, 0.58, "#1565C0",
         "Dashboard interactivo",
         subtext="Plotly make_subplots  -->  dashboard.html", text_size=8.5)
    _box(ax, 10.2, 3.82, 4.0, 0.58, "#2E7D32",
         "Reporte estatico",
         subtext="Matplotlib + Seaborn  -->  stats_report.png", text_size=8.5)

    # Convergencia hacia Streamlit
    _arrow(ax, 3.8, 3.53, 3.8, 3.0)
    _arrow(ax, 10.2, 3.53, 10.2, 3.0)
    ax.plot([3.8, 10.2], [3.0, 3.0], color=COLORS["arrow"], lw=1.5)
    _arrow(ax, 7.0, 3.0, 7.0, 2.48)

    _box(ax, 7, 2.24, 5.6, 0.58, "#AD1457",
         "Streamlit  --  Interfaz Web interactiva",
         subtext="app.py  |  Filtros, KPIs y graficas para portafolio", text_size=9)
    _arrow(ax, 7, 1.95, 7, 1.45)

    # ── END ───────────────────────────────────────────────────────────────────
    _box(ax, 7, 1.2, 2.6, 0.58, COLORS["success"], "FIN", text_size=12, radius=0.29)

    # ── Leyenda ───────────────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=COLORS["extract"],   label="Extract   - Consumo de la API"),
        mpatches.Patch(color=COLORS["transform"], label="Transform - Limpieza y enriquecimiento"),
        mpatches.Patch(color=COLORS["load"],      label="Load      - Persistencia en SQLite"),
        mpatches.Patch(color=COLORS["decision"],  label="Decision  - Validacion de datos"),
        mpatches.Patch(color="#AD1457",           label="Streamlit - Interfaz web (portafolio)"),
    ]
    ax.legend(
        handles=legend_items, loc="lower left", bbox_to_anchor=(0.0, 0.0),
        fontsize=8, framealpha=0.92, edgecolor="#CFD8DC",
        title="Referencias", title_fontsize=8.5,
    )

    plt.tight_layout(pad=0.5)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(OUTPUT_PATH), dpi=160, bbox_inches="tight",
                facecolor=COLORS["bg"])
    plt.close()
    print(f"Diagrama generado: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate()
