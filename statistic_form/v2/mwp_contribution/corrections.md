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

---

## Session 2 — Robust local execution (input auto-discovery + readable errors)
*2026-08-24*

### C-06 · Need
The module failed when run locally. The root cause was `run_classify.py`
hardcoding the input path as `../TC_RILEM_Form_TX_AKLB_FULL VERSION.xlsx`,
which breaks whenever the file sits elsewhere, is named with underscores
instead of spaces, or the script is launched from another folder.

### C-07 · What changed and why
**Before** — `CONFIG['input_xlsx']` was a fixed relative path; any mismatch
raised a raw `FileNotFoundError` traceback.

**After** — `input_xlsx` defaults to `None` and the entry point now:
1. `check_dependencies()` — names missing packages and prints the exact
   `pip install` line instead of an `ImportError`.
2. `locate_input()` — auto-searches `TC_RILEM_Form*.xlsx`, then
   `*RILEM*Form*.xlsx`, then `*.xlsx` in the module folder, its parent and
   `./input`; skips Excel lock files (`~$…`) and previously generated
   `*classification*.xlsx`. Accepts an explicit path as a command-line
   argument: `python run_classify.py "C:/path/to/form.xlsx"`.
3. Guards the `AI_tables/` folder, the worksheet name (exact
   "Final for analysis AI and code"), and `PermissionError` (workbook still
   open in Excel) — each with an actionable message instead of a traceback.

All paths are resolved from the script's own location, so the module runs
correctly from any working directory.

### C-08 · Tests
Four failure paths exercised: auto-discovery, explicit path argument,
non-existent path, and launching from an unrelated working directory —
all behave as intended. Full run after the change: **8/8 invariant tests
pass** and every headline figure is unchanged (UT 103 / IRT 45 / both 3 /
other 4; Primary 70 / 65 / 20; Confidence 84 / 48 / 23), confirming the fix
is behaviour-preserving.

### C-09 · Follow-up — library files guarded against direct execution
*2026-08-24*

**Need** — a local `FileNotFoundError` was reported showing the *old* hardcoded
path `mwp_contribution\..\TC_RILEM_Form_TX_AKLB_FULL VERSION.xlsx`, raised via
Spyder's `runcell(0, '...main.py')`. Two distinct causes: (a) the pre-C-07
version of `run_classify.py` was still in use; (b) `main.py`, a library file
with no configuration, was being executed directly from the IDE.

**What changed**
- `main.py`, `mwp_data.py`, `mwp_viz.py` and `write_xlsx.py` now raise a
  `SystemExit` with a plain instruction if executed directly, naming
  `run_classify.py` as the entry point (and F5 / Run file in Spyder rather
  than Run cell).
- `HERE` in `run_classify.py` falls back to the current working directory when
  `__file__` is undefined (interactive consoles, some IDE cell modes), and
  self-corrects to the CWD if that is where `AI_tables/` actually lives.

**Tests** — direct execution of each of the four library files now exits with
the guidance message; `--test` and full runs still pass 8/8 with unchanged
results.

### C-10 · main.py made directly runnable
*2026-08-24*

**Need** — running `main.py` from the IDE "did nothing". Two causes: (a)
`main.py` only defined `run_pipeline()` and had no executable block, so
importing/running it produced no output; (b) the C-09 guard raised
`SystemExit` whose message goes to *stderr*, which the IDE console did not
surface — so the file appeared silent rather than refusing.

**What changed** — the guard in `main.py` was replaced by a real
`if __name__ == '__main__':` block that performs a FULL RUN, identical to
`run_classify.py`. It is deliberately not a second copy of the settings: it
imports `run_classify.CONFIG` and its helpers, so there remains exactly one
configuration point. The block also:
- resolves `HERE` from `__file__` with a CWD fallback (undefined in some IDE
  cell modes), self-correcting to the CWD if `AI_tables/` lives there;
- inserts the module folder into `sys.path` and `os.chdir()`s to it, so the
  script works when launched from any working directory;
- echoes the resolved Input / Tables / Output paths to *stdout* before
  running, so a path problem is visible immediately.

Either file may now be run: `python main.py` or `python run_classify.py`
(F5 in Spyder). The guards remain on `mwp_data.py`, `mwp_viz.py` and
`write_xlsx.py`, which are true libraries.

**Tests** — `main.py` run from inside the module folder and from an unrelated
working directory: both complete with 8/8 invariant tests passing and
unchanged results (UT 103 / IRT 45 / both 3 / other 4; Primary 70 / 65 / 20;
Confidence 84 / 48 / 23). `run_classify.py` re-tested afterwards: unchanged,
8/8 pass. No circular-import issue, since `run_classify`'s own `__main__`
block does not execute on import.

### C-11 · Figures — optional on-screen display added
*2026-08-24*

**Need** — the figures appeared to be missing when running locally. They were
not: all 10 PNGs are regenerated into `classification_output/figures/` at
every run. They simply never appear in the IDE's Plots pane, because
`mwp_viz.py` forced the `Agg` (file-only) backend at import time, per the
repository convention that libraries write to files and open no windows.

**What changed**
- `matplotlib.use('Agg')` moved from module import into `make_all_figures()`,
  where it is applied only when `viz['show_figures']` is False. An IDE's
  inline backend is therefore preserved when the user opts in.
- New helper `_finish(fig, path, viz)` saves every figure, then either calls
  `plt.show()` or `plt.close(fig)`. PNG files are written in BOTH modes — the
  deliverable never depends on the display setting.
- New configuration switch in `run_classify.py`: `'viz': {'show_figures':
  False, ...}`. Set it to True to also see the figures in the Spyder Plots
  pane.

**Tests** — both modes run to completion with 8/8 invariant tests passing and
10 PNG files written in each case; results unchanged.
