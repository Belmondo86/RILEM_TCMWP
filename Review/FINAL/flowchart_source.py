"""
flowchart_source.py
-------------------
Generates  flowchart_local.png  — function call graph of the local
bibliometric pipeline.

Software : Python 3 + Matplotlib  (FancyBboxPatch + ax.annotate)
Usage    : python flowchart_source.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch

# ─── palette ─────────────────────────────────────────────────────────────────
C = {
    "input"  : "#1D9E75",   # green  — CSV input & output files
    "data"   : "#2E86AB",   # blue   — biblio_data.py functions
    "logic"  : "#7F77DD",   # purple — internal / shared helpers (main.py)
    "viz"    : "#D85A30",   # coral  — biblio_viz.py
    "ai_tbl" : "#B06A10",   # amber  — AI-generated, user-editable tables
    "df"     : "#555E70",   # dark grey — DataFrame
    "out"    : "#639922",   # dark green — output artefacts
    "bg"     : "#F7F9FC",
    "text"   : "#0D1B2A",
    "edge"   : "#5A6070",
}

def box(ax, cx, cy, w, h, main_lbl, sub=None, color=C["data"], fs=9):
    ax.add_patch(FancyBboxPatch(
        (cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.07", lw=0.7,
        facecolor=color, edgecolor="white", zorder=3))
    if sub:
        ax.text(cx, cy+h*0.17, main_lbl, ha="center", va="center",
                fontsize=fs, fontweight="bold", color="white", zorder=4)
        ax.text(cx, cy-h*0.22, sub, ha="center", va="center",
                fontsize=fs-1.5, color="white", alpha=0.9, zorder=4)
    else:
        ax.text(cx, cy, main_lbl, ha="center", va="center",
                fontsize=fs, fontweight="bold", color="white", zorder=4)

def arr(ax, x1, y1, x2, y2, color=C["edge"], lw=1.3, dashed=False):
    style = dict(arrowstyle="->", color=color, lw=lw)
    if dashed: style.update(linestyle="dashed", lw=0.9, color="#AAAAAA")
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=style, zorder=2)

def note(ax, x, y, txt, color="#8FA7C0"):
    ax.text(x, y, txt, ha="right", va="center",
            fontsize=6.8, color=color, style="italic")

# ─── layout ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 14))
ax.set_xlim(0, 14); ax.set_ylim(0, 14)
ax.axis("off")
fig.patch.set_facecolor(C["bg"]); ax.set_facecolor(C["bg"])

fig.text(0.5, 0.97, "Local bibliometric pipeline",
         ha="center", fontsize=13, fontweight="bold", color=C["text"])
fig.text(0.5, 0.945, "Function call graph  ·  Python + Matplotlib  ·  no internet required",
         ha="center", fontsize=9, color="#6A7080")

# ── ROW 1 : inputs ────────────────────────────────────────────────────────────
box(ax, 4.5, 12.8, 3.8, 0.55, "info_DOI_MWP.csv",
    sub="Authors · Year · Title · Journal · DOI", color=C["input"])
note(ax, 13.8, 12.8, "input")

# ── ROW 2 : AI_tables block ──────────────────────────────────────────────────
# Background panel for AI_tables
ax.add_patch(FancyBboxPatch((0.25, 10.4), 5.3, 2.0,
    boxstyle="round,pad=0.1", lw=1.2,
    facecolor="#FBF0E4", edgecolor=C["ai_tbl"], zorder=1, linestyle="--"))
ax.text(2.9, 12.25, "AI_tables/  —  user-editable",
        ha="center", fontsize=8, color=C["ai_tbl"], fontweight="bold")
ax.text(2.9, 12.05, "✏  Open in Excel to correct AI classifications",
        ha="center", fontsize=7.2, color=C["ai_tbl"], style="italic")

CSV_FILES = [
    ("AI_table_book_doi.csv",       "3"),
    ("AI_table_conf_doi.csv",       "6"),
    ("AI_table_conf_keywords.csv",  "17"),
    ("AI_table_book_keywords.csv",  "7"),
    ("AI_table_publisher_doi.csv",  "15"),
    ("AI_table_publisher_name.csv", "23"),
]
for k, (fname, nrows) in enumerate(CSV_FILES):
    col, row = k % 3, k // 3
    bx = 0.45 + col * 1.72
    by = 11.35 - row * 0.50
    ax.add_patch(FancyBboxPatch((bx, by-0.18), 1.58, 0.34,
        boxstyle="round,pad=0.04", lw=0.6,
        facecolor="white", edgecolor=C["ai_tbl"], zorder=2))
    ax.text(bx+0.79, by+0.04, fname.replace("AI_table_","").replace(".csv",""),
            ha="center", va="center", fontsize=6.5, color=C["ai_tbl"],
            fontweight="bold", zorder=3)
    ax.text(bx+0.79, by-0.10, f"{nrows} rows",
            ha="center", va="center", fontsize=6.0, color="#9A7040", zorder=3)

# load_tables
box(ax, 2.9, 10.0, 3.4, 0.50, "load_tables(AI_tables/)",
    sub="biblio_data.py", color=C["ai_tbl"])
arr(ax, 2.9, 10.40, 2.9, 10.25, color=C["ai_tbl"], lw=1.0)
note(ax, 13.8, 10.0, "biblio_data.py")

# ── ROW 3 : load_dataset ──────────────────────────────────────────────────────
box(ax, 7.8, 12.8, 3.6, 0.52, "load_dataset(info_csv, tables)",
    sub="biblio_data.py", color=C["data"])
arr(ax, 7.8, 12.8,  7.0, 10.25, color=C["edge"], lw=0.8, dashed=True)   # tables →
arr(ax, 4.4, 12.53, 6.1, 11.70, color=C["edge"])                          # csv →

# ── ROW 4 : sub-functions ─────────────────────────────────────────────────────
box(ax, 5.0, 11.20, 2.6, 0.46, "_load_info_csv()",
    sub="CSV → info_lookup", color=C["data"], fs=8.5)
box(ax, 8.5, 11.20, 3.0, 0.46, "_build_from_info(info, tables)",
    sub="assemble DataFrame", color=C["data"], fs=8.5)
arr(ax, 6.8, 12.53, 5.2, 11.43)
arr(ax, 8.9, 12.53, 8.7, 11.43)
note(ax, 13.8, 11.20, "biblio_data.py")

# inference helpers
box(ax, 7.2, 10.20, 2.8, 0.44, "_infer_doc_type(j, doi, tables)",
    color=C["logic"], fs=8)
box(ax, 10.4, 10.20, 2.8, 0.44, "_infer_publisher(j, doi, tables)",
    color=C["logic"], fs=8)
arr(ax, 8.0, 10.97, 7.3, 10.42, dashed=True)
arr(ax, 9.2, 10.97, 10.3, 10.42, dashed=True)
# tables feed into inference (orange arrow)
arr(ax, 4.5, 9.75, 6.4, 10.20, color=C["ai_tbl"], lw=1.0)
note(ax, 13.8, 10.20, "main.py / biblio_data.py")

# ── ROW 5 : DataFrame ─────────────────────────────────────────────────────────
box(ax, 7.5, 9.20, 4.4, 0.52, "DataFrame",
    sub="doi · year · journal · type · publisher · authors · …", color=C["df"])
arr(ax, 5.0, 10.97, 6.0, 9.46)
arr(ax, 8.5, 10.97, 7.9, 9.46)
note(ax, 13.8, 9.20, "pandas")

# ── ROW 6 : outputs fork ──────────────────────────────────────────────────────
box(ax, 2.0, 8.0, 2.8, 0.50, "save_summary_report()",
    sub="biblio_data.py", color=C["data"], fs=8.5)
box(ax, 8.6, 8.0, 6.0, 0.52, "biblio_viz.py — 8 plot functions",
    sub="plot_top_journals · plot_bradford_law · plot_coauthor_network · …",
    color=C["viz"], fs=8.5)
arr(ax, 5.6, 8.94, 2.6, 8.25)
arr(ax, 7.8, 8.94, 9.5, 8.25)
note(ax, 13.8, 8.0, "biblio_viz.py")

# ── ROW 7 : shared helpers ────────────────────────────────────────────────────
box(ax, 5.2, 6.90, 2.8, 0.44, "main.draw_network()", color=C["logic"], fs=8.5)
box(ax, 8.7, 6.90, 2.8, 0.44, "main.apply_plot_style()", color=C["logic"], fs=8.5)
box(ax, 11.8, 6.90, 2.2, 0.44, "main.save_figure()", color=C["logic"], fs=8.5)
arr(ax, 7.4, 7.74, 5.5, 7.12, dashed=True)
arr(ax, 8.7, 7.74, 8.7, 7.12, dashed=True)
arr(ax, 11.0, 7.74, 11.8, 7.12, dashed=True)
note(ax, 13.8, 6.90, "main.py")

# ── ROW 8 : output artefacts ──────────────────────────────────────────────────
box(ax, 2.0, 5.80, 2.6, 0.46, "→ report.txt", color=C["out"], fs=8.5)
box(ax, 8.6, 5.80, 5.6, 0.52, "8 × panel_*.png",
    sub="biblio_output/", color=C["out"])
arr(ax, 2.0, 7.75, 2.0, 6.03)
arr(ax, 11.8, 6.68, 11.3, 6.06)
note(ax, 13.8, 5.80, "output folder")

# ── run_local.py call-out ──────────────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((0.2, 8.7), 1.5, 1.6,
    boxstyle="round,pad=0.2", lw=0.8,
    facecolor="#EEF3FB", edgecolor="#4472C4", zorder=1))
ax.text(0.95, 9.75, "run_local.py", ha="center", fontsize=7.5,
        fontweight="bold", color="#4472C4")
ax.text(0.95, 9.50, "config &", ha="center", fontsize=7, color="#4472C4")
ax.text(0.95, 9.28, "orchestration", ha="center", fontsize=7, color="#4472C4")
arr(ax, 1.72, 9.20, 5.5, 9.20, color="#4472C4", lw=0.9)

# ── LEGEND ────────────────────────────────────────────────────────────────────
legend_items = [
    (C["input"],   "Input / Output file"),
    (C["ai_tbl"],  "AI_tables/ — AI-generated, user-editable CSVs"),
    (C["data"],    "biblio_data.py"),
    (C["viz"],     "biblio_viz.py"),
    (C["logic"],   "main.py  (shared helpers)"),
    (C["df"],      "DataFrame (pandas)"),
]
for k, (color, lbl) in enumerate(legend_items):
    col, row = k % 3, k // 3
    bx = 0.4 + col * 4.4
    by = 5.05 - row * 0.50
    ax.add_patch(FancyBboxPatch((bx, by-0.14), 0.30, 0.28,
        boxstyle="round,pad=0.04", facecolor=color,
        edgecolor="white", lw=0.4, zorder=3))
    ax.text(bx + 0.42, by + 0.0, lbl, va="center",
            fontsize=7.5, color=C["text"])

fig.tight_layout(rect=[0, 0.02, 1, 0.96])
fig.savefig("flowchart_local.png", dpi=150, bbox_inches="tight", facecolor=C["bg"])
plt.close(fig)
print("flowchart_local.png saved")
