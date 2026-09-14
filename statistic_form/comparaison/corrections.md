# corrections.md — Development change log (UT/IRT review-form pipeline)

Same auditability rules as the DOI_MWP bibliometric study: every modification
is recorded with the date, reason, before/after, and test results.
Detailed per-change table: `AI-journal_change.md` (also a sheet of the
delivered workbook). Data-quality findings of the v2.0 audit are archived in
`corrections_v2_archive.md` (findings D1–D7, corrections C1–C4, checks V1–V4).

---

## Session 1 — 2026-07-28 — v1.0 first pipeline

**Need described:** statistical description of the 742-field form export
(table + 4 charts), UT/IRT focus, form-only information.

**Corrections during the session:**
- `groupby().apply()` duplicate merge raised `KeyError: 'Article ID'`
  (pandas ≥ 2.2 excludes the group key) → rewritten as explicit group iteration.

**Tests:** run OK on 109 forms; xlsx recalc 29 formulas / 0 errors;
`Neither UT nor IRT` articles (6) manually verified against UT/IRT block fields;
the single `UT + IRT` article (P45) verified against its C2 selections.

## Session 2 — 2026-07-28 — v2.0 audit and hardening

**Need described:** apply the project method — corrections document,
AI-journal_change table, improved recompiled programs.

**Corrections:**
- *Before:* material rule required exact string `hma` → P20 free text
  "only the numerical model of the HMA mixture" fell to `Other / not specified`.
  *After:* substring match → HMA. Impact: materials chart `Other` 4.7 % → 3.7 %,
  everything else unchanged.
- Application-axis secondary labels standardized (`(+ stiffness)`, `(+ damage)`, `(+ QC)`).
- Statistics sheet: counts persisted raw instead of back-computed from rounded
  percentages.

**Tests:** distributions v1 vs v2 diffed programmatically — single documented
change (P20); recalc 29 formulas / 0 errors.

## Session 3 — 2026-07-28 — v3.0 alignment on the DOI_MWP method

**Need described:** user provided the original README of the *Bibliometric
Analysis — Local Pipeline* (DOI_MWP) → align architecture, correction
workflow and documentation.

**Changes (details in AI-journal_change rows 015–023):**
- File architecture `main.py` / `mwp_data.py` / `mwp_viz.py` / `run_local.py`
  (only editable file) / `write_xlsx.py`.
- All keyword rules moved to **6 editable CSVs** in `AI_tables/`
  (Excel-correctable, applied at next run — same workflow as DOI_MWP).
- `report.txt` summary report; figures renamed `panel_*.png`;
  output-folder overwrite prompt; Graphviz `flowchart_mwp.dot` + `flowchart_mwp.png`;
  README rewritten in the DOI_MWP format.

**Tests:** integrity check — v3.0 distributions bit-identical to v2.0
(technique, materials, relevance, geometries, categories);
xlsx recalc 29 formulas / 0 errors; flowchart renders with graphviz 2.43.

## Known limitations (unchanged)

1. Keyword classification of the Application axis is deterministic but
   shallow; 16 articles remain `Other / not specified in form` (empty
   free-text fields in their forms).
2. Materials and geometries percentages are multi-label (sum > 100 %),
   stated on every figure.
3. Discordant duplicate reviews (P95, P131: Medium vs Low) are flagged,
   not arbitrated — TC reconciliation needed.

## Session 4 — 2026-07-28 — v3.1 re-verification pass

**Need described:** re-verify, correct, proofread, improve and update the
.md files.

**Verifications:**
- *V5 — Year coverage.* The 1995 lower bound flagged in Session 3 was checked
  against the source: **P88, Kim & Lee (1995)**, with P91 (2001) and P144
  (2003), are legitimate form entries. The typo suspicion voiced by the AI in
  the chat is **retracted**; correct coverage is **1995–2025**.
  → now checked automatically: `validate_dataset()` logs the year coverage.
- *V6 — Headline numbers.* All figures quoted in README/report re-checked
  against the recompiled table: UT only 73 (68.2 %), IRT only 27 (25.2 %),
  UT+IRT 1 (0.9 %), neither 6 (5.6 %); HMA 76.6 %; High 36.4 % / Medium
  25.2 % / Low 34.6 %; cylinders/cores 62.1 % of 95. All correct.
- *V7 — Integrity.* v3.1 classification table diffed against v3.0/v2.0:
  bit-identical. Workbook recalc: 29 formulas / 0 errors.

**Corrections:**
- *Before:* README input table row "UT / IRT block fields" had 2 cells for a
  3-column table (broken rendering). *After:* third cell added.
- *Before:* file-descriptions table omitted `corrections_v2_archive.md`.
  *After:* row added.
- *Before:* the AI-journal_change workbook sheet showed the Session-3 table
  header as a data row. *After:* parser skips repeated header rows.

**Tests:** full re-run; recalc 29 formulas / 0 errors; diff v3.1 vs v3.0
table = identical; journal sheet re-checked (single header row).
