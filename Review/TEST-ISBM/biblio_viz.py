"""
=============================================================================
  biblio_viz.py  —  Local Bibliometric Visualisation Layer
  -----------------------------------------------------------------------------
  8 plot functions for the local (no-API) analysis pipeline.
  All functions expect a DataFrame produced by biblio_data.load_dataset(),
  which contains: doi, year, journal, publisher, type, cited_by,
                  references_n, authors, n_authors, title.
  Shared utilities (PALETTE, draw_network, save_figure) live in main.py.
=============================================================================
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import networkx as nx

import main
from main import author_short_label


# ── shortcut for rcParams font size ──────────────────────────────────────────
def _fs(delta: float = 0) -> float:
    return plt.rcParams["font.size"] + delta


# =============================================================================
#  INDIVIDUAL PLOT FUNCTIONS
# =============================================================================

def plot_top_journals(df: pd.DataFrame, ax: plt.Axes, n: int) -> None:
    """Horizontal bar chart of the n most-frequent journals / conferences."""
    counts = df["journal"].replace("", np.nan).dropna().value_counts().head(n)
    colors = [main.PALETTE["primary"]   if i == 0 else
              main.PALETTE["secondary"] if i  < 3 else
              main.PALETTE["muted"]
              for i in range(len(counts))]
    counts[::-1].plot(kind="barh", ax=ax, color=colors[::-1], zorder=3)
    ax.set_title(f"Top {n} journals / conferences")
    ax.set_xlabel("Number of articles")
    ax.tick_params(axis="y", labelsize=_fs(-2))


def plot_document_types(df: pd.DataFrame, ax: plt.Axes) -> None:
    """Pie chart of document types."""
    labels_map = {
        "journal-article"     : "Journal article",
        "proceedings-article" : "Conference proceedings",
        "book-chapter"        : "Book chapter",
    }
    counts = df["type"].value_counts()
    labels = [labels_map.get(t, t) for t in counts.index]
    colors = sns.color_palette(
        [main.PALETTE["primary"], main.PALETTE["secondary"], main.PALETTE["accent"]],
        len(counts),
    )
    ax.pie(counts.values, labels=labels, autopct="%1.1f%%",
           colors=colors, startangle=90,
           wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    for text in ax.texts:
        text.set_fontsize(_fs(-2))
    ax.set_title("Document types")


def plot_authors_per_article(df: pd.DataFrame, ax: plt.Axes) -> None:
    """Bar chart of co-authorship distribution."""
    counts = df["n_authors"].value_counts().sort_index()
    counts = counts[counts.index <= 10]
    ax.bar(counts.index, counts.values,
           color=main.PALETTE["secondary"], alpha=0.85, zorder=3)
    mean = df["n_authors"].mean()
    ax.axvline(mean, color=main.PALETTE["accent"], lw=2, ls="--",
               label=f"Mean: {mean:.1f}")
    ax.set_title("Authors per article")
    ax.set_xlabel("Number of authors")
    ax.set_ylabel("Frequency")
    ax.legend()


def plot_publisher_share(df: pd.DataFrame, ax: plt.Axes,
                         min_count: int, cmap: str) -> None:
    """Pie chart of publisher share.  cmap: seaborn palette name."""
    counts = df["publisher"].value_counts()
    other  = counts[counts < min_count].sum()
    counts = counts[counts >= min_count].copy()
    if other:
        counts["Other"] = other
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%",
           colors=sns.color_palette(cmap, len(counts)), startangle=90,
           wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    for text in ax.texts:
        text.set_fontsize(_fs(-2))
    ax.set_title("Publisher share")


def plot_bradford_law(df: pd.DataFrame, ax: plt.Axes) -> None:
    """Bradford concentration curve — cumulative % vs journal rank."""
    counts     = df["journal"].replace("", "N/A").value_counts()
    cumulative = np.cumsum(counts.values)
    pct        = cumulative / cumulative[-1] * 100
    ranks      = np.arange(1, len(pct) + 1)

    ax.plot(ranks, pct, color=main.PALETTE["primary"], lw=2.5)
    ax.fill_between(ranks, pct, alpha=0.08, color=main.PALETTE["primary"])

    for threshold, color in [(33, main.PALETTE["accent"]),
                              (66, main.PALETTE["secondary"])]:
        ax.axhline(threshold, color=color, ls="--", lw=1.5,
                   label=f"{threshold} %")
        n_venues = int(np.searchsorted(pct, threshold)) + 1
        ax.axvline(n_venues, color=color, ls=":", lw=1)
        ax.annotate(f"{n_venues} venues",
                    xy=(n_venues + 0.3, threshold - 8),
                    fontsize=_fs(-1.5), color=color)

    ax.set_title("Publication concentration — Bradford's law")
    ax.set_xlabel("Journal rank")
    ax.set_ylabel("Cumulative % of articles")
    ax.legend(fontsize=_fs(-1))


def plot_types_over_time(df: pd.DataFrame, ax: plt.Axes) -> None:
    """Stacked bar chart of document types by year."""
    labels_map = {
        "journal-article"     : "Journal article",
        "proceedings-article" : "Conference proceedings",
        "book-chapter"        : "Book chapter",
    }
    pivot = df.groupby(["year", "type"]).size().unstack(fill_value=0)
    pivot.columns = [labels_map.get(c, c) for c in pivot.columns]
    pivot.plot(kind="bar", stacked=True, ax=ax, width=0.75, zorder=3,
               color=[main.PALETTE["primary"],
                      main.PALETTE["secondary"],
                      main.PALETTE["accent"]][: len(pivot.columns)])
    ax.set_title("Document types over time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of articles")
    ax.legend(fontsize=_fs(-2), loc="upper left")
    ax.tick_params(axis="x", rotation=45, labelsize=_fs(-2))


def plot_coauthor_network(df             : pd.DataFrame,
                          ax             : plt.Axes,
                          top_n          : int,
                          label_fontsize : float,
                          label_min_degree: int) -> None:
    """
    Co-author network.  Nodes = "Initials. Family".
    Delegates rendering to main.draw_network.
    """
    pairs: Counter = Counter()
    for author_list in df["authors"]:
        labels = [author_short_label(a) for a in author_list]
        for a, b in combinations(labels, 2):
            pairs[tuple(sorted([a, b]))] += 1

    G = nx.Graph()
    for (a, b), w in pairs.items():
        G.add_edge(a, b, weight=w)

    main.draw_network(G, ax,
                      title="Co-author network",
                      top_n=top_n,
                      label_min_degree=label_min_degree,
                      label_fontsize=label_fontsize)


def plot_top_authors(df: pd.DataFrame, ax: plt.Axes, n: int) -> None:
    """Horizontal bar chart of the n most-prolific authors."""
    all_labels    = [author_short_label(a) for auths in df["authors"] for a in auths]
    names, counts = zip(*Counter(all_labels).most_common(n))
    thr_high      = np.percentile(counts, 85)
    thr_mid       = np.percentile(counts, 50)
    colors        = [main.PALETTE["primary"]   if c >= thr_high else
                     main.PALETTE["secondary"] if c >= thr_mid  else
                     main.PALETTE["muted"]     for c in counts]

    ax.barh(list(names)[::-1], list(counts)[::-1],
            color=colors[::-1], zorder=3)
    for i, c in enumerate(list(counts)[::-1]):
        ax.text(c + 0.05, i, str(c),
                va="center", fontsize=_fs(-1), color=main.PALETTE["dark"])

    ax.set_title(f"Top {n} authors — article count in corpus")
    ax.set_xlabel("Number of articles")
    ax.tick_params(axis="y", labelsize=_fs(-1))
