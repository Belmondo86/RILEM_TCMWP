# corrections.md — mwp_contribution

> Living development journal. **Append only — never delete previous entries.**
> Give this file + README.md to any AI agent or collaborator to resume work.

---

## Session 1 — Initial module: Primary-Contribution classification of the 155-paper corpus
*2026-08-24*

### C-01 · Need
Classify each of the 155 papers of `TC_RILEM_Form_TX_AKLB_FULL VERSION.xlsx`
(worksheet "Final for analysis AI and code" ONLY) into exactly one Primary
Contribution (Application Focus / Testing Methodology Focus / Data Analysis
Type) per the TC 18-point specification, using only form content, with
reviewer assessment (ABK/ABL) restricted to tie-breaks.

### C-02 · What was built and why
An exploratory single-script analysis was first produced, then **refactored
into the standard module architecture** (this correction) because the first
delivery did not follow the repository methodology — no `run_*.py` entry
point, no editable `AI_tables/`, no `corrections.md`.

Final structure: `run_classify.py` (entry point, ALL config) / `main.py`
(orchestration) / `mwp_data.py` (loading + table-driven scoring) /
`mwp_viz.py` (10 figures) / `write_xlsx.py` (workbook) / 8 CSVs in
`AI_tables/` holding every keyword/normalization rule.

Key design decisions:
- **AI tables are the correction point, not the code.** All regex keyword
  rules (application evidence, signal-processing levels, property tiers,
  identification levels, material/geometry normalization, non-informative
  answers, tie-break emphasis) were externalized from the code into
  `AI_tables/*.csv`. First-match-wins ordering for normalization tables.
- Scoring thresholds (bin edges for App/Meth scores, etc.) are configuration
  in `run_classify.py`, not constants in libraries.
- Column ranges (EF:EM, GM:GT, NA:NH, ER/GY/NM, ES:EX, GZ:HG, NN:NU,
  AAY:ABC, H:AT, AU, ABJ:ABL) remain constants in `mwp_data.py` because they
  describe the fixed form structure, not tunable classification rules.
- "No / Not reported / N/A" never earns credit anywhere
  (`AI_table_noinfo_values.csv`).
- DA = 3 requires BOTH a meaningful property (PropC ≥ 1) AND an
  inverse/back-analysis identification (IdM = 3); FFT/FEM/"complex modulus"
  keywords alone never trigger it (enforced by invariant test 6).
- The 4 papers without explicit UT/IRT (P29, P101, P53, P21) are never
  reclassified and are excluded from the UT/IRT/Both denominator (151),
  reported separately (workbook sheet + fig01 caption).

### C-03 · Tests
`mwp_data.check_invariants` runs 8 automated tests at every execution
(155 rows; unique verbatim Paper IDs; Primary sums to 155; Primary ∈ 3
categories; Primary = max score & Secondary only when 2nd ≥ 2; DA=3 ⇒
PropC ≥ 1 ∧ IdM = 3; score ranges; non-UT/IRT never reclassified).
**Result: 8/8 pass**, both in `--test` mode (isolated `tempfile.mkdtemp`
directory) and in the production run.

**Regression check vs the exploratory analysis**: per-paper comparison over
155 papers × 16 classification fields (technique, all 9 scores, primary,
secondary, confidence, tie-break, materials, geometries) → **0 differences**.
The refactoring is behaviour-preserving.

Workbook recalculation (`recalc.py`): 97 formulas, 0 errors.

### C-04 · Headline results (n = 155)
- Technique (AU): UT only 103, IRT only 45, both 3, other 4.
- Relevance (ABJ): High 61 / Medium 46 / Low 46 / Not reported 2.
- Primary: Application 70 (45.2%) / Methodology 65 (41.9%) /
  Data Analysis 20 (12.9%) — sums to 155.
- Confidence: High 84 / Medium 48 / Low 23 (tie-break invoked for 71 papers;
  the 23 Low-confidence papers are the natural candidates for TC
  reconciliation).
- 354 form columns are blank for all 155 papers (listed in the workbook).

### C-05 · Known limitations / open points for the TC
- Keyword rules are deterministic but were AI-drafted: the TC should review
  `AI_tables/*.csv` (especially application keywords and property tiers) the
  same way the LRF-study AI tables were reviewed.
- 71 tie-breaks reflect the coarseness of 0–3 scales; threshold bins in
  `run_classify.py` (`app_bins`, `meth_bins`) can be tuned and everything
  regenerates deterministically.
