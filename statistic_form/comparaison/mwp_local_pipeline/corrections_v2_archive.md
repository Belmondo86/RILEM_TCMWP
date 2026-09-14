# corrections.md — RILEM TC MWP bibliometric analysis (UT / IRT)

Pipeline version: **2.0** — 2026-07-28.
Scope: corrections and data-quality findings identified when re-applying the
bibliometric method to `input_RILEM_TC_MWP__Literature_Review_Form.xlsx`
(109 review forms, 742 fields). All findings derive from the forms only.

---

## 1. Data-quality findings (source spreadsheet — flagged, not altered)

The source file is read-only; no value was modified in it. Findings are handled
in the pipeline and traced in `journal.log` (Stage 1 QC).

| # | Finding | Records | Handling in pipeline |
|---|---------|---------|----------------------|
| D1 | Duplicate reviews of the same article | P95, P131 (2 forms each) | Merged at article level: union of labels; relevance kept as `Low/Medium (2 reviews, discordant)` |
| D2 | Discordant relevance ratings between the two reviewers | P95 (Medium vs Low), P131 (Medium vs Low) | Flagged, not arbitrated — TC should reconcile |
| D3 | Missing relevance rating | P51, P125 | Category `Not reported` (kept in denominator) |
| D4 | `C2 = "Other"` with empty "specify the test name" field | P07, P87, P113, P117 | No UT/IRT block filled either → `Neither UT nor IRT` (verified against UT/IRT block fields) |
| D5 | Free-text heterogeneity in Geometry (e.g. `Slabs`, `plate`, `cubic specimen`, `In‑situ` with non-breaking hyphen) | ~20 non-standard entries | Rule-table normalization (`GEOMETRY_RULES`), incl. Unicode hyphen variant |
| D6 | Free-text heterogeneity in Material Type (e.g. `only binder`, `only the numerical model of the HMA mixture`) | ~10 non-standard entries | Rule-table normalization (`MATERIAL_RULES`) |
| D7 | Non-atomic multi-answers in single-choice fields (e.g. `Cylinder, Disc`) | 4 geometry entries | Multi-label split by keyword matching |

## 2. Methodological corrections applied in v2.0

| # | Correction | Before (v1.0) | After (v2.0) | Impact on results |
|---|-----------|---------------|--------------|-------------------|
| C1 | Material matching of `"...the HMA mixture"` free text (P20) | Not matched → `Other / not specified` | Substring rule `hma` → `Hot Mix Asphalt (HMA)` | Materials chart: `Other / not specified` 4.7% → 3.7%; HMA count unchanged (P20 already counted HMA via Material 1) |
| C2 | Application-axis secondary labels | Mixed-case artifacts (`(+ lve stiffness)`) | Controlled short labels from `APP_RULES` (`(+ stiffness)`, `(+ damage)`, `(+ QC)`) | Labels only; counts unchanged |
| C3 | Duplicate-merge implementation | `groupby().apply()` (pandas-version fragile, raised `KeyError`) | Explicit iteration over groups | Robustness only |
| C4 | Statistics sheet counts | Percentages back-converted to counts (rounding risk) | Raw counts persisted (`materials_cnt`, `geometry_cnt`), % as spreadsheet formulas | Numerical exactness of the Statistics sheet |

## 3. Verified non-issues (checked, no correction needed)

| # | Check | Result |
|---|-------|--------|
| V1 | Articles classified `UT + IRT` | Exactly 1 (P45), confirmed by both `C2` selections in the form |
| V2 | The 6 `Neither UT nor IRT` articles | Confirmed: no UT/IRT block field filled (AE, GPR/monitoring reviews, ML prediction, E* back-analysis, adhesion) |
| V3 | `Other` test names mapped to UT-family (`UPV test`, `5-point bending together with UT`, `SASW`) and IRT-family (`non-contact resonance`, `Resonant Column`) | Traceability note stored per form (`_note` column of the state file) |
| V4 | Workbook formulas | `recalc`: 29 formulas, 0 errors |

## 4. Known limitations (unchanged, by design)

1. The reviewers' own method files (readme / pipeline of the companion
   *bibliometric study* conversation) were not available in this project; the
   architecture was rebuilt to the described pattern. Rules are centralized in
   `config_mwp.py` for easy alignment once the original file is provided.
2. Keyword classification of the Application axis is deterministic but shallow;
   16 articles remain `Other / not specified in form` because the relevant
   free-text fields are empty in their forms.
3. Percentages for materials and geometries are multi-label (sum > 100%),
   stated on every figure.
