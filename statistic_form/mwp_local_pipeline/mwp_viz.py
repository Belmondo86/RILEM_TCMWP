"""
mwp_viz.py — draws the 4 figures of the UT/IRT analysis.
(Same role as biblio_viz.py in the DOI_MWP bibliometric study: one function
per panel; styling comes from run_local.py via main.apply_style.)
Version 3.0 — 2026-07-28.
"""

from __future__ import annotations

import matplotlib.pyplot as plt

from main import save_figure


def _pie(series, colors, title, path, cfg):
    fig = plt.figure(figsize=(7.5, 6))
    plt.pie(series, labels=[f"{k}\n{v} articles" for k, v in series.items()],
            autopct="%1.1f%%", startangle=90, colors=colors,
            labeldistance=1.12, pctdistance=0.75,
            wedgeprops={"edgecolor": "white"})
    plt.title(title)
    save_figure(fig, path, cfg.DPI)


def _barh(series_pct, color, title, xlabel, path, cfg):
    fig = plt.figure(figsize=(9, 5.5))
    series_pct.sort_values().plot(kind="barh", color=color, edgecolor="black")
    for i, v in enumerate(series_pct.sort_values()):
        plt.text(v + 0.7, i, f"{v}%", va="center", fontsize=cfg.FONT_SIZE - 1)
    plt.xlabel(xlabel)
    plt.title(title)
    save_figure(fig, path, cfg.DPI)


def plot_technique_share(st, out, cfg):
    """% of articles using UT only / IRT only / both / neither."""
    tech = st["technique"]
    colors = [cfg.PALETTE["primary"], cfg.PALETTE["accent"],
              cfg.PALETTE["secondary"], cfg.PALETTE["neutral"]][:len(tech)]
    _pie(tech, colors, f"MWP technique used per article (n = {st['n']})",
         f"{out}/panel_technique_share.png", cfg)


def plot_material_types(st, out, cfg):
    """% distribution of material types (multi-label)."""
    pct = (100 * st["materials"] / st["n"]).round(1)
    _barh(pct, cfg.PALETTE["primary"], "Material types studied",
          f"% of articles (n = {st['n']}; multi-label, sum > 100%)",
          f"{out}/panel_material_types.png", cfg)


def plot_relevance(st, out, cfg):
    """Distribution of TC MWP relevance ratings."""
    rel = st["relevance"]
    cmap = {"High": cfg.PALETTE["good"], "Medium": cfg.PALETTE["accent"],
            "Low": cfg.PALETTE["bad"]}
    _pie(rel, [cmap.get(k, cfg.PALETTE["neutral"]) for k in rel.index],
         f"Relevance for TC MWP objectives (n = {st['n']})",
         f"{out}/panel_relevance.png", cfg)


def plot_geometries(st, out, cfg):
    """Distribution of specimen geometries in UT/IRT test blocks (multi-label)."""
    pct = (100 * st["geometry"] / st["n_geo"]).round(1)
    _barh(pct, cfg.PALETTE["accent"],
          "Specimen geometries used in UT / IRT test blocks",
          f"% of articles (n = {st['n_geo']}; multi-label, sum > 100%)",
          f"{out}/panel_geometries.png", cfg)


ALL_PANELS = [plot_technique_share, plot_material_types,
              plot_relevance, plot_geometries]
