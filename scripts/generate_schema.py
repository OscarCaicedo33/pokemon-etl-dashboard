"""
Genera el diagrama de esquema de datos del proyecto Pokemon ETL.
Modelo estrella: tabla pokemon (SQLite) al centro con sus grupos de columnas.
Uso:  python scripts/generate_schema.py
Salida: data/output/schema_diagram.png
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.patches import Ellipse

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "output" / "schema_diagram.png"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

BG        = "#EAECF0"
ARROW_CLR = "#6B7280"
TEXT_CLR  = "#2D2D2D"
FONT      = "DejaVu Sans"

# (display_label, hex_color, cx, cy)  — canvas [0, 13] × [0, 9]
NODES = {
    "pokemon":        ("pokemon\n(SQLite · 151 filas × 21 cols)", "#E74C3C", 6.5, 5.0),
    "pokeapi":        ("PokéAPI\n(/pokemon/{id})",                "#2980B9", 6.5, 7.8),
    "types":          ("Tipos\n(type_primary · type_secondary)",  "#E67E22", 2.5, 7.2),
    "stats":          ("Base Stats\nhp·atk·def·sp_atk·sp_def·spd·bst", "#8E44AD", 1.5, 5.0),
    "physical":       ("Físico\nheight_m · weight_kg · bmi_index","#27AE60", 2.5, 2.8),
    "classification": ("Clasificación\ngeneration · power_tier",  "#16A085", 10.5, 2.8),
    "identity":       ("Identidad\nid · name · abilities",        "#7F8C8D", 10.5, 7.2),
}

EDGES = [
    ("pokeapi",        "pokemon",        "HTTP GET /pokemon/{id}"),
    ("pokemon",        "types",          "type_primary\ntype_secondary"),
    ("pokemon",        "stats",          "6 stats + bst"),
    ("pokemon",        "physical",       "altura · peso"),
    ("pokemon",        "classification", "generation · power_tier"),
    ("pokemon",        "identity",       "id · name · abilities"),
]

ICON_W = 1.25
ICON_H = 0.92
MARGIN = 0.66


def _darker(rgb, f=0.70):
    return tuple(max(0.0, c * f) for c in rgb)

def _lighter(rgb, f=1.12):
    return tuple(min(1.0, c * f) for c in rgb)


def draw_db_icon(ax, cx, cy, color, w=ICON_W, h=ICON_H, z=4):
    """3-D database cylinder with ring stripes."""
    rgb   = mcolors.to_rgb(color)
    dark  = _darker(rgb)
    light = _lighter(rgb)

    eh     = h * 0.26
    rect_h = h - eh
    y_top  = cy + h / 2 - eh / 2
    y_bot  = y_top - rect_h

    ax.add_patch(mpatches.Rectangle(
        (cx - w / 2, y_bot), w, rect_h,
        facecolor=color, edgecolor="none", zorder=z,
    ))
    ax.add_patch(Ellipse(
        (cx, y_bot), w, eh,
        facecolor=dark, edgecolor="none", zorder=z + 1,
    ))
    ax.add_patch(Ellipse(
        (cx, y_top), w, eh,
        facecolor=light, edgecolor="none", zorder=z + 2,
    ))
    for i in range(3):
        sy = y_top - (i + 0.6) * rect_h * 0.27
        ax.add_patch(Ellipse(
            (cx, sy), w * 0.88, eh * 0.52,
            facecolor="none", edgecolor="white",
            linewidth=1.25, alpha=0.62, zorder=z + 3,
        ))


def edge_pt(cx, cy, tx, ty, margin=MARGIN):
    dx, dy = tx - cx, ty - cy
    d = np.hypot(dx, dy)
    if d < 1e-6:
        return cx, cy
    return cx + margin * dx / d, cy + margin * dy / d


def draw_edge(ax, x1, y1, x2, y2, label):
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="<->",
            color=ARROW_CLR,
            lw=1.75,
            mutation_scale=14,
        ),
        zorder=2,
    )
    ax.text(
        mid_x, mid_y, label,
        ha="center", va="center",
        fontsize=6.5, fontfamily=FONT, color="#555555",
        bbox=dict(boxstyle="round,pad=0.22", fc=BG, ec="none", alpha=0.92),
        zorder=6,
        multialignment="center",
    )


def build():
    fig, ax = plt.subplots(figsize=(13, 9))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9)
    ax.axis("off")

    pos = {k: (v[2], v[3]) for k, v in NODES.items()}

    # Edges (behind icons)
    for src, dst, label in EDGES:
        x1, y1 = pos[src]
        x2, y2 = pos[dst]
        sx, sy = edge_pt(x1, y1, x2, y2)
        ex, ey = edge_pt(x2, y2, x1, y1)
        draw_edge(ax, sx, sy, ex, ey, label)

    # Icons + labels
    for key, (label, color, cx, cy) in NODES.items():
        draw_db_icon(ax, cx, cy, color)
        ax.text(
            cx, cy - ICON_H / 2 - 0.16,
            label,
            ha="center", va="top",
            fontsize=6.8, fontfamily=FONT,
            color=TEXT_CLR, zorder=7,
            multialignment="center",
        )

    plt.tight_layout(pad=0.4)
    return fig


def main():
    print("Generando diagrama de esquema Pokemon ETL...")
    fig = build()
    fig.savefig(str(OUTPUT_PATH), dpi=122, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"PNG guardado: {OUTPUT_PATH}")
    print("Listo.")


if __name__ == "__main__":
    main()
