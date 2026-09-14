"""
=============================================================================
  run_local.py  —  Local Bibliometric Runner
  -----------------------------------------------------------------------------
  Reads info_DOI_MWP.csv and generates 8 figures — no internet required.

  Usage :  python run_local.py
=============================================================================
"""

# =============================================================================
#  CONFIGURATION — edit only this section
# =============================================================================

# ── Source file ───────────────────────────────────────────────────────────────
INFO_CSV    = "info_DOI_MWP.csv"
OUTPUT_DIR  = "biblio_output"
TABLES_DIR  = "AI_tables"          # AI-generated lookup CSVs — edit to correct classifications

# ── Visual style ──────────────────────────────────────────────────────────────
PALETTE = {
    "primary"   : "#4472C4",
    "secondary" : "#2E86AB",
    "accent"    : "#F4A261",
    "light"     : "#D6E8F5",
    "dark"      : "#0D1B2A",
    "muted"     : "#8FA7C0",
    "bg"        : "#F7F9FC",
}
FONT_FAMILY = "DejaVu Sans"
FONT_SIZE   = 10
DPI         = 150

# ── Chart parameters ──────────────────────────────────────────────────────────
TOP_JOURNALS_N      = 15
TOP_AUTHORS_N       = 20
COAUTHOR_TOP_N      = 40
PUBLISHER_MIN_COUNT = 3

# ── Colour maps ───────────────────────────────────────────────────────────────
CMAP_PUBLISHERS     = "Blues_r"

# ── Network label options ─────────────────────────────────────────────────────
NETWORK_LABEL_SIZE  = 8
NETWORK_LABEL_MIN   = 3

# ── Figure sizes  (width, height in inches) ───────────────────────────────────
FIGSIZE_TOP_JOURNALS  = (12,  6)
FIGSIZE_DOC_TYPES     = ( 7,  7)
FIGSIZE_AUTHORS_ART   = ( 9,  5)
FIGSIZE_PUBLISHERS    = ( 8,  8)
FIGSIZE_BRADFORD      = ( 9,  6)
FIGSIZE_TYPES_TIME    = (12,  6)
FIGSIZE_NETWORK       = (12, 10)
FIGSIZE_TOP_AUTHORS   = (10,  9)

# ── Output filenames ──────────────────────────────────────────────────────────
FILE_TOP_JOURNALS  = "panel_top_journals.png"
FILE_DOC_TYPES     = "panel_document_types.png"
FILE_AUTHORS_ART   = "panel_authors_per_article.png"
FILE_PUBLISHERS    = "panel_publisher_share.png"
FILE_BRADFORD      = "panel_bradford_law.png"
FILE_TYPES_TIME    = "panel_types_over_time.png"
FILE_NETWORK       = "panel_coauthor_network.png"
FILE_TOP_AUTHORS   = "panel_top_authors.png"


# =============================================================================
#  SETUP
# =============================================================================

import matplotlib
matplotlib.use("Agg")                # always save to file
import matplotlib.pyplot as plt

import main
import biblio_data as bdata
import biblio_viz  as bviz


# =============================================================================
#  STEP 1 — Prepare
# =============================================================================

main.apply_plot_style(PALETTE, FONT_FAMILY, FONT_SIZE)
OUTPUT_DIR = main.resolve_output_dir(OUTPUT_DIR)

tables = bdata.load_tables(TABLES_DIR)
df = bdata.load_dataset(info_csv=INFO_CSV, tables=tables)
if df is None:
    raise SystemExit("No data — check INFO_CSV path.")

bdata.save_summary_report(df, OUTPUT_DIR)


# =============================================================================
#  STEP 2 — Figures  (comment out any block you do not need)
# =============================================================================

fig, ax = plt.subplots(figsize=FIGSIZE_TOP_JOURNALS)
bviz.plot_top_journals(df, ax, n=TOP_JOURNALS_N)
fig.tight_layout()
main.save_figure(fig, FILE_TOP_JOURNALS, OUTPUT_DIR, DPI)

fig, ax = plt.subplots(figsize=FIGSIZE_DOC_TYPES)
bviz.plot_document_types(df, ax)
fig.tight_layout()
main.save_figure(fig, FILE_DOC_TYPES, OUTPUT_DIR, DPI)

fig, ax = plt.subplots(figsize=FIGSIZE_AUTHORS_ART)
bviz.plot_authors_per_article(df, ax)
fig.tight_layout()
main.save_figure(fig, FILE_AUTHORS_ART, OUTPUT_DIR, DPI)

fig, ax = plt.subplots(figsize=FIGSIZE_PUBLISHERS)
bviz.plot_publisher_share(df, ax, min_count=PUBLISHER_MIN_COUNT,
                           cmap=CMAP_PUBLISHERS)
fig.tight_layout()
main.save_figure(fig, FILE_PUBLISHERS, OUTPUT_DIR, DPI)

fig, ax = plt.subplots(figsize=FIGSIZE_BRADFORD)
bviz.plot_bradford_law(df, ax)
fig.tight_layout()
main.save_figure(fig, FILE_BRADFORD, OUTPUT_DIR, DPI)

fig, ax = plt.subplots(figsize=FIGSIZE_TYPES_TIME)
bviz.plot_types_over_time(df, ax)
fig.tight_layout()
main.save_figure(fig, FILE_TYPES_TIME, OUTPUT_DIR, DPI)

fig, ax = plt.subplots(figsize=FIGSIZE_NETWORK)
bviz.plot_coauthor_network(df, ax, top_n=COAUTHOR_TOP_N,
                            label_fontsize=NETWORK_LABEL_SIZE,
                            label_min_degree=NETWORK_LABEL_MIN)
fig.tight_layout()
main.save_figure(fig, FILE_NETWORK, OUTPUT_DIR, DPI)

fig, ax = plt.subplots(figsize=FIGSIZE_TOP_AUTHORS)
bviz.plot_top_authors(df, ax, n=TOP_AUTHORS_N)
fig.tight_layout()
main.save_figure(fig, FILE_TOP_AUTHORS, OUTPUT_DIR, DPI)
