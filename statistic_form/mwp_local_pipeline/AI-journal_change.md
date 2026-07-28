# AI-journal_change — RILEM TC MWP bibliometric pipeline

Change journal of every AI-made modification. One row per change.
Types: `NEW` (file created), `REFACTOR` (structure), `FIX` (correction),
`IMPROVE` (quality), `DOC` (documentation), `OUTPUT` (regenerated deliverable).

| ID | Date | File | Type | Change | Justification | Impact on results |
|----|------|------|------|--------|---------------|-------------------|
| 001 | 2026-07-28 | config_mwp.py | NEW | Central configuration module: paths, taxonomy labels, all keyword rule tables (`UT_KEYS`, `IRT_KEYS`, `CONV_KEYS`, `APP_RULES`, `MATERIAL_RULES`, `GEOMETRY_RULES`), plot styling | Single source of truth; rules editable without touching logic; alignment with method structure (config separated from functions) | None (rules transcribed from v1) |
| 002 | 2026-07-28 | functions_mwp.py | REFACTOR | v1.0 → v2.0: all constants imported from `config_mwp`; typed signatures; `_first_match()` rule-table normalizer replaces if/elif chains for materials and geometries | Maintainability, traceability of every label to a rule row | See 004 |
| 003 | 2026-07-28 | functions_mwp.py | IMPROVE | New `validate_dataset()` QC stage: detects duplicate Article IDs, missing relevance, missing IDs, non-standard years; findings written to journal | PhD-level reproducibility: data-quality findings must be logged, not silent | Journal now reports P95/P131 duplicates and P51/P125 missing relevance |
| 004 | 2026-07-28 | functions_mwp.py | FIX | Material rule `hma` now matches as substring (v1 required exact `s == "hma"`); P20 entry "only the numerical model of the HMA mixture" now → HMA | The v1 rule missed an explicit HMA mention in free text | Materials chart: `Other / not specified` 4.7% → 3.7% (all other statistics identical) |
| 005 | 2026-07-28 | functions_mwp.py | FIX | Application-axis secondary labels use controlled short names from `APP_RULES` (`(+ stiffness)`, `(+ damage)`, `(+ QC)`) instead of string-mangled fragments (`(+ lve stiffness)`) | Label consistency in the classification table | Labels only; counts unchanged |
| 006 | 2026-07-28 | run_pipeline.py | REFACTOR | v1 monolithic `main()` split into 5 explicit stages: `load_and_validate` → `classify_forms` → `merge_duplicates` → `compute_stats_and_charts` → `persist`; chart helpers `_pie` / `_barh` factored | Mirrors the pipeline schema of the bibliometric method (README diagram) | None |
| 007 | 2026-07-28 | run_pipeline.py | FIX | Duplicate-merge rewritten as explicit group iteration (v1 `groupby().apply()` raised `KeyError` on pandas ≥ 2.2 group-key exclusion) | Robustness across pandas versions | None (was already hot-fixed in v1 run) |
| 008 | 2026-07-28 | run_pipeline.py | IMPROVE | CLI added (`argparse`, `--no-xlsx`); XLSX writer callable from the pipeline (single command recompiles everything); journal messages prefixed by stage | One-command reproducibility: `python3 run_pipeline.py` | None |
| 009 | 2026-07-28 | run_pipeline.py | IMPROVE | Pie labels: `labeldistance`/`pctdistance` tuned to remove label overlap of small slices (v1 fig1: `UT + IRT` label collided with `Neither`) | Figure legibility | Figures re-rendered (fig1–fig4) |
| 010 | 2026-07-28 | write_xlsx.py | FIX | Statistics sheet uses raw counts persisted by the pipeline (`materials_cnt`, `geometry_cnt`) instead of counts back-computed from rounded percentages | Removes rounding-error risk in the deliverable | Statistics sheet exact; visible values unchanged |
| 011 | 2026-07-28 | write_xlsx.py | IMPROVE | Workbook gains sheet `AI-journal_change` (this table) so the deliverable is self-documenting | Method requirement: change journal as a table inside the deliverable | New sheet |
| 012 | 2026-07-28 | corrections.md | DOC/NEW | Corrections document: 7 data-quality findings (D1–D7), 4 methodological corrections (C1–C4), 4 verified non-issues (V1–V4), 3 limitations | Method requirement | — |
| 013 | 2026-07-28 | README.md | DOC/NEW | Project README with pipeline schema (Mermaid + ASCII), function-level diagrams, taxonomy tables, usage, outputs | Method requirement (same structure as the companion bibliometric study) | — |
| 014 | 2026-07-28 | out/* | OUTPUT | Full recompilation: classification table (CSV + XLSX, recalc 29 formulas / 0 errors), fig1–fig4, journal.log regenerated with v2.0 | Deliverables must match code version | Statistics identical to v1 except item 004 |

**Statistical integrity check (v1.0 → v2.0):** technique shares, relevance
distribution, geometry distribution and classification-category counts are
bit-identical; the only numerical change is documented in row 004.

## Session 3 — 2026-07-28 — Alignment on the DOI_MWP bibliometric method (v3.0)

| ID | Date | File | Type | Change | Justification | Impact on results |
|----|------|------|------|--------|---------------|-------------------|
| 015 | 2026-07-28 | (project) | REFACTOR | Architecture aligned on the DOI_MWP study: `main.py` (shared utilities) / `mwp_data.py` (data + report) / `mwp_viz.py` (4 panel functions) / `run_local.py` (only file to edit) / `write_xlsx.py` | User provided the original README; method requires this exact file architecture | None (statistics verified identical to v2.0) |
| 016 | 2026-07-28 | AI_tables/*.csv | NEW | The 6 keyword rule sets exported from `config_mwp.py` to editable CSVs: technique, conventional, application, material (row order = priority), geometry, comparison | Method requirement: "AI-generated classification tables are plain CSV files — fix errors in Excel"; correction workflow without touching code | None (rules transcribed verbatim) |
| 017 | 2026-07-28 | main.py | NEW | `load_tables()`, `save_figure()`, `apply_style()` (PALETTE/FONT_SIZE/DPI from run_local), `resolve_output_dir()` with the [1] overwrite / [2] new-folder prompt, journal helpers | Same utility roles as `main.py` of the DOI_MWP study | None |
| 018 | 2026-07-28 | run_local.py | NEW | Single settings block: INFO_XLSX, OUTPUT_DIR, TABLES_DIR, PALETTE, FONT_SIZE, DPI, WRITE_XLSX | Method requirement: "the only file you need to edit" | Figures restyled with the DOI_MWP palette (#4472C4 / #F4A261, bg #F7F9FC) |
| 019 | 2026-07-28 | mwp_data.py | REFACTOR | Classifiers now read keywords from the loaded AI tables at call time; `save_summary_report()` added (report.txt in the DOI_MWP format) | Corrections in AI_tables apply on next run without code change; report.txt is a method deliverable | None |
| 020 | 2026-07-28 | mwp_viz.py | REFACTOR | Figures renamed `panel_technique_share / panel_material_types / panel_relevance / panel_geometries`; one function per panel, `ALL_PANELS` registry | Method naming convention (`panel_*.png`) | File names only |
| 021 | 2026-07-28 | flowchart_mwp.dot/.png | NEW | Graphviz pipeline diagram (source + rendered PNG), mirroring `flowchart_local.dot` of the DOI_MWP study | Method requirement | — |
| 022 | 2026-07-28 | README.md | DOC | Rewritten in the exact DOI_MWP README format: overview, key-features table, architecture, flowchart (Graphviz + mermaid), plain-words steps, input/output tables, install/run/configure, AI-tables correction workflow, file-description table, AI-methodology loop, sessions table, licence | User request: "un readme.md avec des schémas de pipeline des fonctions comme dans bibliometric study" | — |
| 023 | 2026-07-28 | out/* → mwp_output/* | OUTPUT | Full recompilation under the new architecture; xlsx recalc-verified; integrity check: all distributions bit-identical to v2.0 | Deliverables must match code version | None |

## Session 4 — 2026-07-28 — Re-verification and documentation update (v3.1)

| ID | Date | File | Type | Change | Justification | Impact on results |
|----|------|------|------|--------|---------------|-------------------|
| 024 | 2026-07-28 | (data check) | FIX | Verified the 1995 lower bound of the year coverage: P88, Kim & Lee (1995) is a legitimate form entry (with P91 2001 and P144 2003). The AI's chat-side suspicion of a Year typo is retracted; README and corrections.md now state the verified coverage 1995–2025 | Re-verification pass requested by the user; earlier AI comment was unverified speculation | None (no data changed; documentation corrected) |
| 025 | 2026-07-28 | README.md | FIX | Input-specification table: row "UT / IRT block fields" had 2 cells instead of 3 (broken Markdown rendering); file-descriptions table completed with `corrections_v2_archive.md`; headline results now state coverage 1995–2025 and the verified oldest entry | Proofreading of the .md files | — |
| 026 | 2026-07-28 | write_xlsx.py | FIX | AI-journal_change sheet parser now skips the repeated header rows of later session tables (the Session-3 header previously appeared as a data row in the workbook sheet) | The change journal now spans several sessions, each with its own Markdown table header | Workbook sheet only |
| 027 | 2026-07-28 | mwp_data.py | IMPROVE | `validate_dataset()` additionally logs the year coverage and any non-numeric Year values | Turns the manual year check of this session into a permanent automated QC step | journal.log gains one QC line |
| 028 | 2026-07-28 | corrections.md | DOC | Session 4 added: verification results (V5–V7), the three fixes above, and the retraction note | Method requirement: every session documented | — |
| 029 | 2026-07-28 | mwp_output/* | OUTPUT | Recompiled with v3.1; xlsx recalc-verified; integrity check: classification table bit-identical to v3.0/v2.0 | Deliverables must match code version | None |
