"""
main.py — shared utilities for the MWP UT/IRT bibliometric pipeline.
(Same role as main.py in the DOI_MWP bibliometric study: helpers used by the
other modules. You should not need to edit this file.)
Version 3.0 — 2026-07-28.
"""

from __future__ import annotations

import datetime
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

_JOURNAL: list = []


def log(msg: str) -> None:
    """Timestamped journal entry, printed and kept for journal.log."""
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    _JOURNAL.append(line)
    print(line)


def write_journal(path: str) -> None:
    with open(path, "w") as fh:
        fh.write("\n".join(_JOURNAL) + "\n")


def resolve_output_dir(base: str) -> str:
    """Reproduce the run_local behaviour of the DOI_MWP study:
    if the folder exists, ask [1] overwrite / [2] new folder.
    Non-interactive runs (no TTY) default to overwrite."""
    if not os.path.isdir(base):
        os.makedirs(base)
        return base
    if not sys.stdin.isatty():
        log(f"Output folder '{base}' exists — non-interactive run, overwriting.")
        return base
    print(f"  Output folder '{base}' already exists.")
    print("  [1] Overwrite existing files")
    i = 1
    while os.path.isdir(f"{base}_{i}"):
        i += 1
    print(f"  [2] Create new folder  '{base}_{i}'")
    if input("  Choice [1/2]: ").strip() == "2":
        base = f"{base}_{i}"
        os.makedirs(base)
    return base


def s(v) -> str:
    """Safe lowercase string of a cell."""
    return "" if pd.isna(v) else str(v).strip().lower()


def load_tables(tables_dir: str) -> dict:
    """Load the six AI_tables/*.csv classification tables.
    They are AI-generated and editable in Excel (see README)."""
    T = {}
    T["technique"] = pd.read_csv(f"{tables_dir}/AI_table_technique_keywords.csv")
    T["conventional"] = pd.read_csv(f"{tables_dir}/AI_table_conventional_keywords.csv")
    T["application"] = pd.read_csv(f"{tables_dir}/AI_table_application_keywords.csv")
    T["material"] = pd.read_csv(f"{tables_dir}/AI_table_material_keywords.csv").sort_values("priority")
    T["geometry"] = pd.read_csv(f"{tables_dir}/AI_table_geometry_keywords.csv")
    T["comparison"] = pd.read_csv(f"{tables_dir}/AI_table_comparison_keywords.csv")
    log(f"load_tables(): {len(T)} AI tables loaded from {tables_dir}/.")
    return T


def apply_style(cfg) -> None:
    plt.rcParams.update({
        "font.size": cfg.FONT_SIZE,
        "figure.facecolor": cfg.PALETTE["bg"],
        "savefig.facecolor": cfg.PALETTE["bg"],
        "axes.facecolor": cfg.PALETTE["bg"],
    })


def save_figure(fig, path: str, dpi: int) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    log(f"save_figure(): {os.path.basename(path)}")
