"""
=============================================================================
  main.py  —  Shared Bibliometric Utilities
  -----------------------------------------------------------------------------
  Imported by all biblio_*.py libraries.

  Contents
  --------
  CSV_SEP, CSV_ENCODING          — input file format
  clean_doi(raw)                 — normalise a DOI string
  author_short_label(full_name)  — "Jean-Claude Carret" → "J-C. Carret"
  resolve_output_dir(base)       — smart output folder management
  apply_plot_style(palette, ...) — configure matplotlib / seaborn style
  save_figure(fig, ...)          — save figure to disk (always)
  draw_network(G, ax, ...)       — shared networkx graph renderer
=============================================================================
"""

from __future__ import annotations

import os
import re

import matplotlib.pyplot as plt
import networkx as nx


# =============================================================================
#  SECTION 1 — CSV FORMAT CONSTANTS
# =============================================================================

CSV_SEP      = ";"
CSV_ENCODING = "latin-1"

# ISO-2 country code → full English country name
# Used by save_summary_report (biblio_data) and plot_world_map (biblio_viz_API).
ISO2_NAMES: dict[str, str] = {
    "FR": "France",          "US": "United States",    "SE": "Sweden",
    "NL": "Netherlands",     "BE": "Belgium",          "GB": "United Kingdom",
    "DE": "Germany",         "ES": "Spain",            "CN": "China",
    "IT": "Italy",           "CA": "Canada",           "CL": "Chile",
    "ZA": "South Africa",    "TR": "Turkey",           "ID": "Indonesia",
    "JO": "Jordan",          "AU": "Australia",        "BR": "Brazil",
    "IN": "India",           "KR": "South Korea",      "JP": "Japan",
    "PL": "Poland",          "PT": "Portugal",         "CZ": "Czech Republic",
    "RO": "Romania",         "DZ": "Algeria",          "MA": "Morocco",
    "MX": "Mexico",          "AR": "Argentina",        "IR": "Iran",
    "SA": "Saudi Arabia",    "EG": "Egypt",            "DK": "Denmark",
    "NO": "Norway",          "FI": "Finland",          "AT": "Austria",
    "CH": "Switzerland",     "GR": "Greece",           "NZ": "New Zealand",
    "TH": "Thailand",        "MY": "Malaysia",         "TW": "Taiwan",
    "HK": "Hong Kong",       "SG": "Singapore",        "PK": "Pakistan",
    "VN": "Vietnam",         "PH": "Philippines",      "HR": "Croatia",
    "HU": "Hungary",         "IL": "Israel",           "CO": "Colombia",
    "PE": "Peru",            "VE": "Venezuela",        "EC": "Ecuador",
    "TN": "Tunisia",         "NG": "Nigeria",          "KE": "Kenya",
    "LB": "Lebanon",         "AE": "United Arab Emirates", "QA": "Qatar",
    "RU": "Russia",          "UA": "Ukraine",          "RS": "Serbia",
    "BG": "Bulgaria",        "SK": "Slovakia",         "BY": "Belarus",
}


# =============================================================================
#  SECTION 2 — DOI UTILITIES
# =============================================================================

def clean_doi(raw: str) -> str | None:
    """Strip URL prefix, reject placeholders, validate 10.<reg>/ pattern."""
    if not isinstance(raw, str):
        return None
    value = re.sub(
        r"https?://(?:dx\.)?doi\.org/", "", raw.strip(), flags=re.IGNORECASE
    ).strip()
    if not value or value.lower().startswith("not") or value.lower() == "x":
        return None
    if value.startswith("http") or not re.match(r"^10\.\d{4,}/", value):
        return None
    return value.lower()


# =============================================================================
#  SECTION 3 — AUTHOR SHORT LABEL
# =============================================================================

def author_short_label(full_name: str) -> str:
    """
    Build "Initials. Family" from "Family, Given" format.
    "Carret, Jean-Claude" → "J-C. Carret"   "Sauzéat, Cédric" → "C. Sauzéat"
    "Gudmarsson, A"       → "A. Gudmarsson"  "Boz, ilker"      → "I. Boz"
    """
    if "," not in full_name:
        return full_name.strip()
    family, given = full_name.split(",", 1)
    family, given = family.strip(), given.strip()
    if not given:
        return family
    first = given.split()[0].replace(".", "")
    if not first:
        return family
    initials = "-".join(p[0].upper() for p in first.split("-") if p) \
               if "-" in first else first[0].upper()
    return f"{initials}. {family}"


# =============================================================================
#  SECTION 4 — OUTPUT FOLDER MANAGEMENT
# =============================================================================

def resolve_output_dir(base: str) -> str:
    """
    Resolve an output directory path, handling existing folders gracefully.

    · If the folder does not exist → create and return it.
    · If it already exists → ask the user:
        [1] Overwrite  (reuse same folder)
        [2] New folder (base_1, base_2, … next available number)
    """
    if not os.path.exists(base):
        os.makedirs(base)
        print(f"  Created output folder: {base}")
        return base

    # Find the next available numbered folder
    n = 1
    while os.path.exists(f"{base}_{n}"):
        n += 1
    numbered = f"{base}_{n}"

    print(f"\n  Output folder '{base}' already exists.")
    print(f"  [1] Overwrite existing files")
    print(f"  [2] Create new folder  '{numbered}'")
    choice = input("  Choice [1/2]: ").strip()

    if choice == "2":
        os.makedirs(numbered)
        print(f"  Using: {numbered}\n")
        return numbered
    else:
        print(f"  Overwriting: {base}\n")
        return base


# =============================================================================
#  SECTION 5 — VISUALISATION STYLE & OUTPUT
# =============================================================================

# Populated by apply_plot_style() — do not edit directly.
PALETTE: dict[str, str] = {}


def apply_plot_style(palette    : dict[str, str],
                     font_family: str = "DejaVu Sans",
                     font_size  : int = 10) -> None:
    """Set a consistent matplotlib / seaborn style for all figures."""
    import seaborn as sns
    global PALETTE
    PALETTE = palette
    sns.set_style("whitegrid")
    plt.rcParams.update({
        "font.family"      : font_family,
        "font.size"        : font_size,
        "axes.titlesize"   : font_size + 2,
        "axes.titleweight" : "bold",
        "axes.facecolor"   : palette["bg"],
        "figure.facecolor" : palette["bg"],
        "axes.spines.top"  : False,
        "axes.spines.right": False,
        "axes.edgecolor"   : palette["muted"],
        "axes.labelcolor"  : palette["dark"],
        "xtick.color"      : palette["dark"],
        "ytick.color"      : palette["dark"],
        "grid.color"       : "#DDE4ED",
        "grid.linewidth"   : 0.7,
    })


def save_figure(fig       : plt.Figure,
                filename  : str,
                output_dir: str,
                dpi       : int = 150) -> None:
    """Save figure to output_dir/filename and close it."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=dpi, bbox_inches="tight",
                facecolor=PALETTE.get("bg", "white"))
    plt.close(fig)
    print(f"  ✓  {path}")


# =============================================================================
#  SECTION 6 — SHARED NETWORK RENDERER
# =============================================================================

def draw_network(G               : nx.Graph,
                 ax              : plt.Axes,
                 title           : str,
                 top_n           : int,
                 label_min_degree: int,
                 label_fontsize  : float) -> None:
    """
    Render a weighted NetworkX graph as a spring-layout diagram.
    Shared by biblio_viz.py and biblio_viz_API.py.
    Node colour reflects relative degree (primary / secondary / light quartiles).
    Edge width is proportional to normalised weight.
    """
    if len(G.nodes) == 0:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, fontsize=11,
                color=PALETTE.get("muted", "#888"))
        ax.set_title(title)
        ax.axis("off")
        return

    # ── Keep only top_n most-connected nodes ─────────────────────────────────
    top   = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:top_n]
    G     = G.subgraph([n for n, _ in top]).copy()
    pos   = nx.spring_layout(G, seed=42, k=2.0, iterations=60)

    degrees = [G.degree(n) for n in G.nodes()]
    weights = [G[u][v].get("weight", 1) for u, v in G.edges()]
    max_w   = max(weights) if weights else 1
    max_d   = max(degrees) if degrees else 1

    # ── Edges ─────────────────────────────────────────────────────────────────
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        width=[0.5 + 2.5 * (w / max_w) for w in weights],
        alpha=0.3,
        edge_color=PALETTE.get("muted", "#8FA7C0"),
    )

    # ── Nodes ─────────────────────────────────────────────────────────────────
    node_colors = [
        PALETTE.get("primary",   "#4472C4") if d >= max_d * 0.75 else
        PALETTE.get("secondary", "#2E86AB") if d >= max_d * 0.40 else
        PALETTE.get("light",     "#D6E8F5")
        for d in degrees
    ]
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=[80 + d * 65 for d in degrees],
        edgecolors=PALETTE.get("dark", "#0D1B2A"),
        linewidths=0.6,
    )

    # ── Labels (only above threshold degree) ─────────────────────────────────
    nx.draw_networkx_labels(
        G, pos,
        labels={n: n for n in G.nodes() if G.degree(n) >= label_min_degree},
        ax=ax,
        font_size=label_fontsize,
        font_color=PALETTE.get("dark", "#0D1B2A"),
        font_weight="bold",
        bbox={"boxstyle": "round,pad=0.15", "facecolor": "white",
              "alpha": 0.55, "edgecolor": "none"},
    )

    ax.set_title(f"{title}\n(top {top_n} nodes — edge width ∝ link strength)")
    ax.axis("off")
