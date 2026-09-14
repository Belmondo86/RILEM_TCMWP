# mwp_contribution — Primary-Contribution classification of the 155-paper corpus

> Module of the **RILEM TC 331-MWP** research codebase.
> Classifies each of the 155 literature-review forms in
> `TC_RILEM_Form_TX_AKLB_FULL VERSION.xlsx` (worksheet
> **"Final for analysis AI and code"** only) into exactly one Primary
> Contribution — **Application Focus**, **Testing Methodology Focus** or
> **Data Analysis Type** — plus technique, relevance, material, geometry and
> score analyses, per the 18-point TC specification.
>
> Only form content is used. Original papers and external sources are never
> consulted. Reviewer Assessment (ABK/ABL) is used **only** as a tie-break
> criterion and never alters the technical contribution scores.

---

## Overview

```
mwp_contribution/
├── README.md                  ← this file
├── corrections.md             ← development journal — append only, never delete
├── run_classify.py            ← THE ONLY FILE YOU NEED TO RUN (all config here)
├── main.py                    ← orchestration — do not edit
├── mwp_data.py                ← loading + table-driven scoring engine — do not edit
├── mwp_viz.py                 ← the 10 required figures — do not edit
├── write_xlsx.py              ← workbook writer — do not edit
├── AI_tables/                 ← classification rules — open in Excel to correct
│   ├── AI_table_noinfo_values.csv          non-informative answers ("No", "N/A"…)
│   ├── AI_table_application_keywords.csv   Application evidence patterns
│   ├── AI_table_signal_processing.csv      basic vs advanced processing techniques
│   ├── AI_table_property_complexity.csv    basic/mechanical/viscoelastic/advanced tiers
│   ├── AI_table_identification_method.csv  identification levels 1–3
│   ├── AI_table_material_normalization.csv material category mapping (first match wins)
│   ├── AI_table_geometry_normalization.csv geometry category mapping (first match wins)
│   └── AI_table_tiebreak_keywords.csv      ABK/ABL emphasis patterns (tie-break ONLY)
└── classification_output/     ← regenerated at every run
    ├── TC331_MWP_155papers_classification.xlsx   6-sheet colour-coded workbook
    ├── classification_results.csv                one row per paper (diff-friendly)
    ├── run_log.txt                               tests + headline statistics
    └── figures/fig01..fig10.png                  the 10 required graphs
```

## Pipeline

```
TC_RILEM_Form_TX_AKLB_FULL VERSION.xlsx  ──►  mwp_data.load_form
        (sheet "Final for analysis AI and code", 155 rows × 742 cols)
                                │
AI_tables/*.csv  ──────────────►│  mwp_data.classify   (deterministic, table-driven)
                                │
                                ├──►  mwp_data.check_invariants   (8 automated tests)
                                ├──►  classification_results.csv
                                ├──►  write_xlsx.write_workbook   (colour-coded, formulas)
                                └──►  mwp_viz.make_all_figures    (fig01..fig10)
```

## How to use

```bash
python run_classify.py            # full run into classification_output/
python run_classify.py --test     # isolated run in a temp directory (nothing overwritten)
```

**To correct a classification**: open the relevant `AI_tables/*.csv` in Excel,
fix or add a rule (regex pattern → label/category), rerun `run_classify.py`.
The AI tables are the correction point — never the code. Every output is
regenerated deterministically from the tables at each run.

## Classification logic (summary — full rules in the workbook ReadMe sheet)

| Score | Source columns | Rule |
|---|---|---|
| MWP Technique | AU | explicit "Ultrasonic testing (UT)" / "Impact resonance test (IRT)" labels only; 4 papers stay "Other / not explicitly UT or IR" |
| Application 0–3 | Title, H:AT, AU, EL/GS/NG | count of evidence items (keyword table + conventional-test comparison + multi-material + multi-temperature): 0→0, 1→1, 2–3→2, ≥4→3 |
| Methodology 0–3 | IR: EF–EM · UT: GM–GT, NA–NH | count of informative parameter fields: 0→0, 1–2→1, 3–5→2, ≥6→3 |
| Signal Processing 0–2 | IR: EN–EP · UT: GU–GW, NI–NK | advanced technique or ≥3 basic → 2; any basic → 1 |
| Property Complexity 0–3 | ER, GY, NM | constitutive params or ≥2 viscoelastic → 3; 1 viscoelastic → 2; mechanical → 1; basic output → 0 |
| Identification 0–3 | IR: ES–EX · UT: GZ–HG, NN–NU | inverse/back-analysis → 3; FRF/modal/peak → 2; closed-form/empirical → 1 |
| Data Analysis 0–3 | 5A+5B+5C | 3 requires PropC ≥ 1 **and** IdM = 3; FFT/FEM/"complex modulus" alone never suffice |
| Rheology 0–2 | AAY–ABC | descriptive only; model → 1, + TTSP/shift factors/master curve → 2 |
| Primary | — | highest of App/Meth/DA; ties → ABK/ABL emphasis only; unresolved ties → richer form evidence + confidence "Low" |
| Secondary | — | reported only when the 2nd-highest score ≥ 2 |

"No / Not reported / N/A / not specified" **never** earns credit
(`AI_table_noinfo_values.csv`).

## Automated tests (run at every execution, logged in `run_log.txt`)

1. 155 papers, one row each · 2. Paper IDs unique and preserved verbatim ·
3. Primary distribution sums to 155 · 4. every Primary is one of the 3
categories · 5. Primary = max score and Secondary only when 2nd ≥ 2 ·
6. DA=3 ⇒ PropC ≥ 1 and IdM = 3 · 7. all scores within range ·
8. non-UT/IRT papers never reclassified.

## Conventions (inherited from the repository README)

- `run_classify.py` is the entry point; all colours, fonts, figure sizes and
  scoring thresholds live there — zero hardcoded values in libraries.
- No `print()` in library files; all output goes to files (`run_log.txt`,
  CSV, workbook, PNGs; matplotlib Agg backend).
- `AI_table_*.csv` are AI-generated lookup tables — check and correct in Excel.
- `corrections.md` is append-only; tests must pass before every commit.

## AI-assisted development sessions

| Session | Date | Scope |
|---|---|---|
| 1 | 2026-08-24 | Initial module: table-driven engine, 8 tests, workbook + 10 figures; per-paper parity verified against the exploratory analysis |

## Licence
RILEM TC MWP — free to use for all members of the TC group — M.Belmokhtar
(Université Gustave Eiffel).
