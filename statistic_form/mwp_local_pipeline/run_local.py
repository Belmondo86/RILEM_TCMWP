"""
run_local.py — RILEM TC MWP: UT/IRT statistical analysis of the review forms.
THE ONLY FILE YOU NEED TO EDIT. All settings are below.

Run:  python3 run_local.py
Outputs go to OUTPUT_DIR (report.txt, classification table, 4 panel_*.png,
journal.log). Classification rules are editable CSVs in TABLES_DIR.
Version 3.0 — 2026-07-28.
"""

# ----------------------------- SETTINGS -------------------------------------
INFO_XLSX = "/mnt/project/input_RILEM_TC_MWP__Literature_Review_Form.xlsx"
OUTPUT_DIR = "mwp_output"          # where figures and reports are saved
TABLES_DIR = "AI_tables"           # where the classification CSVs are

PALETTE = {
    "primary":   "#4472C4",   # main colour — UT, material bars
    "secondary": "#2E86AB",   # secondary colour — UT+IRT slice
    "accent":    "#F4A261",   # highlight — IRT, geometry bars, Medium
    "good":      "#2ca02c",   # High relevance
    "bad":       "#d62728",   # Low relevance
    "neutral":   "#9e9e9e",   # Neither / not reported
    "bg":        "#F7F9FC",   # figure background
}
FONT_SIZE = 10     # base font size in points
DPI = 150          # resolution (150 = screen, 300 = print)
WRITE_XLSX = True  # also write the formatted 4-sheet workbook
# -----------------------------------------------------------------------------

import sys


class _Cfg:                       # bundle settings for the modules
    pass


def main() -> None:
    import main as M
    import mwp_data as D
    import mwp_viz as V

    cfg = _Cfg()
    for k in ("PALETTE", "FONT_SIZE", "DPI"):
        setattr(cfg, k, globals()[k])

    out = M.resolve_output_dir(OUTPUT_DIR)
    M.apply_style(cfg)

    T = M.load_tables(TABLES_DIR)                     # 1. AI tables
    arts = D.load_dataset(INFO_XLSX, T)               # 2. read + classify + merge
    st = D.compute_stats(arts)                        # 3. statistics
    D.save_summary_report(arts, st, f"{out}/report.txt")
    arts[D.TABLE_COLS].to_csv(f"{out}/MWP_classification_table.csv", index=False)
    M.log(f"run_local: classification table written ({len(arts)} articles).")

    for panel in V.ALL_PANELS:                        # 4. figures
        panel(st, out, cfg)

    if WRITE_XLSX:                                    # 5. formatted workbook
        import write_xlsx
        write_xlsx.write(arts, st, f"{out}/MWP_UT_IRT_classification_table.xlsx")
        M.log("run_local: formatted XLSX workbook written.")

    M.write_journal(f"{out}/journal.log")
    M.log("run_local: pipeline complete.")


if __name__ == "__main__":
    sys.exit(main())
