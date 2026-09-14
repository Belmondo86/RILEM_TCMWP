"""
mwp_data.py — reads the review-form spreadsheet, classifies each article,
writes report.txt and the classification table.
(Same role as biblio_data.py in the DOI_MWP bibliometric study.)

Scope: ONLY information contained in the review forms (no external sources).
Focus: Ultrasonic Testing (UT) and Impact Resonance Testing (IRT).
Version 3.0 — 2026-07-28. Classification rules live in AI_tables/*.csv.
"""

from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple

import pandas as pd

from main import log, s

TABLE_COLS = ["Article ID", "Reference", "MWP technique", "Relevance for TC MWP",
              "Classification category", "Application axis",
              "Test methodology axis", "Data analysis type"]


# ----------------------------------------------------------------------------
# Column resolution + QC
# ----------------------------------------------------------------------------

def get_cols(df: pd.DataFrame) -> Dict:
    cols = list(df.columns)
    starts = lambda p: [x for x in cols if x.startswith(p)]
    c: Dict = {
        "id": "Article ID", "authors": "Authors", "year": "Year", "title": "Title",
        "relevance": starts("Relevance for the laboratory")[0],
        "comparison": starts("Comparison between MWP tests")[0],
        "purpose_rheo": starts("What was the purpose of the rheological")[0],
        "contribution": starts("Key contribution")[0],
        "test_type": starts("C2. What type of test is being reported?"),
        "test_other": starts('If "Other" was selected'),
        "conv_type": starts("What type of test is reported?"),
        "materials": starts("B1. Material Type"),
        "ut_config": starts("Test configuration"),
        "ut_waves": starts("What type(s) of waves were considered?"),
        "irt_boundary": starts("Boundary conditions"),
        "irt_modes": starts("Mode(s) of vibrations studied"),
        "domain": starts("The determination of the mechanical properties was based"),
        "method": starts("What type of method(s) were used to determine"),
        "props": starts("What mechanical properties were determined?"),
    }
    c["geometry"] = [(x, int(re.search(r"Test (\d)", x).group(1)))
                     for x in starts("C3.2 Geometry")]
    return c


def validate_dataset(df: pd.DataFrame, c: Dict) -> None:
    """Quality control: findings go to the journal (source file untouched)."""
    dup = df[c["id"]][df[c["id"]].duplicated(keep=False)]
    if not dup.empty:
        log(f"QC: duplicate Article IDs (multiple reviews): {sorted(set(dup.astype(str)))}")
    miss = df.loc[df[c["relevance"]].isna(), c["id"]].astype(str).tolist()
    if miss:
        log(f"QC: {len(miss)} form(s) without relevance rating: {miss}")
    if df[c["id"]].isna().any():
        log(f"QC: {df[c['id']].isna().sum()} form(s) without Article ID.")
    yrs = pd.to_numeric(df[c["year"]], errors="coerce")
    log(f"QC: year coverage {int(yrs.min())}-{int(yrs.max())}"
        + (f"; non-numeric Year in {int(yrs.isna().sum())} form(s)." if yrs.isna().any() else "."))


# ----------------------------------------------------------------------------
# Classification functions (driven by AI_tables)
# ----------------------------------------------------------------------------

def _keys(T: pd.DataFrame, col: str = "keyword", where=None) -> Tuple[str, ...]:
    d = T if where is None else T[where(T)]
    return tuple(d[col].astype(str))


def detect_techniques(row, c, T) -> Tuple[bool, bool, str]:
    ut_k = _keys(T["technique"], where=lambda t: t.family == "UT")
    irt_k = _keys(T["technique"], where=lambda t: t.family == "IRT")
    ut, irt, notes = False, False, []
    for tcol, ocol in zip(c["test_type"], c["test_other"]):
        t, o = s(row[tcol]), s(row[ocol])
        if "ultrasonic testing" in t:
            ut = True
        elif "impact resonance" in t:
            irt = True
        elif t == "other" and o:
            if any(k in o for k in ut_k):
                ut = True
                notes.append(f"UT-family via 'Other': {o[:60]}")
            elif any(k in o for k in irt_k):
                irt = True
                notes.append(f"IRT-family via 'Other': {o[:60]}")
    return ut, irt, "; ".join(notes)


def technique_label(ut: bool, irt: bool) -> str:
    return {(1, 1): "UT + IRT", (1, 0): "UT only",
            (0, 1): "IRT only", (0, 0): "Neither UT nor IRT"}[(ut, irt)]


def mwp_test_numbers(row, c, T) -> Set[int]:
    fam_k = _keys(T["technique"])
    nums: Set[int] = set()
    for i, (tcol, ocol) in enumerate(zip(c["test_type"], c["test_other"]), 1):
        t, o = s(row[tcol]), s(row[ocol])
        if ("ultrasonic testing" in t or "impact resonance" in t
                or (t == "other" and any(k in o for k in fam_k))):
            nums.add(i)
    return nums


def detect_conventional(row, c, T) -> bool:
    fam_k, conv_k = _keys(T["technique"]), _keys(T["conventional"])
    for tcol, ocol in zip(c["test_type"], c["test_other"]):
        t, o = s(row[tcol]), s(row[ocol])
        if "complex modulus" in t:
            return True
        if t == "other" and o and not any(k in o for k in fam_k):
            if any(k in o for k in conv_k):
                return True
    return any(s(row[col]) for col in c["conv_type"])


def classify_category(row, c, T, has_conv: bool) -> str:
    comp = s(row[c["comparison"]])
    if has_conv and any(k in comp for k in _keys(T["comparison"])):
        return "Comparative study (MWP vs conventional)"
    if has_conv:
        return "MWP + conventional tests (no formal comparison)"
    return "Standalone MWP study"


def classify_application(row, c, T) -> str:
    text = " ".join(s(row[x]) for x in
                    c["props"] + [c["purpose_rheo"], c["contribution"]])
    scores = []
    for (fam, short), g in T["application"].groupby(["family", "short_label"]):
        n = sum(text.count(k) for k in g["keyword"].astype(str))
        if n:
            scores.append((n, fam, short))
    scores.sort(reverse=True)
    if not scores:
        return "Other / not specified in form"
    if len(scores) > 1 and scores[1][0] >= max(2, 0.5 * scores[0][0]):
        return f"{scores[0][1]} (+ {scores[1][2]})"
    return scores[0][1]


def classify_methodology(row, c, ut: bool, irt: bool) -> str:
    parts: List[str] = []
    if ut:
        cfg = " ".join(s(row[x]) for x in c["ut_config"])
        m = ("UT through-transmission" if "through-transmission" in cfg else
             "UT pulse-echo" if "pulse-echo" in cfg else
             "UT surface-wave" if "surface" in cfg else
             "UT (configuration not reported)")
        waves = " ".join(s(row[x]) for x in c["ut_waves"])
        wl = [w for w, ok in (
            ("P", "compression" in waves or bool(re.search(r"\bp[- ]?wave", waves))),
            ("S", "shear" in waves or "both" in waves),
            ("R", "rayleigh" in waves or "surface" in waves)) if ok]
        parts.append(m + (f" ({'/'.join(wl)}-waves)" if wl else ""))
    if irt:
        bnd = " ".join(s(row[x]) for x in c["irt_boundary"])
        modes = " ".join(s(row[x]) for x in c["irt_modes"])
        m = "IRT free-free resonance" if "free-free" in bnd else "IRT resonance"
        ml = [k.capitalize() for k in ("longitudinal", "flexural", "torsional")
              if k in modes]
        parts.append(m + (f" ({'/'.join(ml)})" if ml else ""))
    return " + ".join(parts) if parts else "No UT/IRT methodology reported"


def classify_analysis(row, c) -> str:
    dom_txt = " ".join(s(row[x]) for x in c["domain"])
    has_t, has_f = bool(re.search(r"\btime\b", dom_txt)), "frequency" in dom_txt
    dom = ("Time + frequency domain" if has_t and has_f else
           "Frequency domain" if has_f else
           "Time domain" if has_t else "Domain not reported")
    met_txt = " ".join(s(row[x]) for x in c["method"])
    if "analytical" in met_txt or "closed-form" in met_txt:
        met = "analytical (closed-form)"
    elif any(k in met_txt for k in ("numerical", "fem", "inverse")):
        met = "numerical inverse (FEM/other)"
    elif any(k in met_txt for k in ("empirical", "regression", "correlation")):
        met = "empirical / regression"
    elif "qualitative" in met_txt:
        met = "qualitative"
    else:
        met = "method not reported"
    return f"{dom}; {met}"


def article_materials(row, c, T) -> List[str]:
    out = set()
    for x in c["materials"]:
        v = s(row[x])
        if not v:
            continue
        hit = None
        for _, r in T["material"].iterrows():
            if str(r["keyword"]) in v:
                hit = r["label"]
                break
        out.add(hit or "Other / not specified")
    return sorted(out) if out else ["Other / not specified"]


def normalize_geometry(v, T) -> List[str]:
    v = s(v)
    if not v:
        return []
    out = {r["label"] for _, r in T["geometry"].iterrows() if str(r["keyword"]) in v}
    return sorted(out) if out else ["Other / not specified"]


def article_geometries(row, c, T, mwp_tests: Set[int]) -> List[str]:
    geos: Set[str] = set()
    for col, tno in c["geometry"]:
        if tno in mwp_tests:
            geos.update(normalize_geometry(row[col], T))
    return sorted(geos)


# ----------------------------------------------------------------------------
# Dataset construction
# ----------------------------------------------------------------------------

def load_dataset(src_xlsx: str, T) -> pd.DataFrame:
    """Read the form export, classify each form, merge duplicate reviews.
    Returns the article-level DataFrame (1 row = 1 unique article)."""
    log(f"load_dataset(): reading {src_xlsx}")
    df = pd.read_excel(src_xlsx, sheet_name=0)
    c = get_cols(df)
    log(f"load_dataset(): {len(df)} review forms, {df[c['id']].nunique()} unique "
        f"Article IDs, {df.shape[1]} form fields.")
    validate_dataset(df, c)

    recs = []
    for _, row in df.iterrows():
        ut, irt, note = detect_techniques(row, c, T)
        conv = detect_conventional(row, c, T)
        recs.append({
            "Article ID": str(row[c["id"]]).strip(),
            "Reference": f"{row[c['authors']]} ({row[c['year']]})",
            "Year": row[c["year"]],
            "MWP technique": technique_label(ut, irt),
            "Relevance for TC MWP": (str(row[c["relevance"]]).strip()
                                     if pd.notna(row[c["relevance"]])
                                     else "Not reported"),
            "Classification category": classify_category(row, c, T, conv),
            "Application axis": classify_application(row, c, T),
            "Test methodology axis": classify_methodology(row, c, ut, irt),
            "Data analysis type": classify_analysis(row, c),
            "_materials": article_materials(row, c, T),
            "_geometries": article_geometries(row, c, T, mwp_test_numbers(row, c, T)),
            "_note": note,
        })
    forms = pd.DataFrame(recs)

    def merge(g: pd.DataFrame) -> pd.Series:
        r = g.iloc[0].copy()
        if len(g) > 1:
            for col in TABLE_COLS[2:]:
                if col == "Relevance for TC MWP":
                    continue
                vals = sorted(set(g[col]))
                r[col] = vals[0] if len(vals) == 1 else " | ".join(vals)
            rel = sorted(set(g["Relevance for TC MWP"]))
            r["Relevance for TC MWP"] = (rel[0] if len(rel) == 1 else
                                         "/".join(rel) + " (2 reviews, discordant)")
            r["_materials"] = sorted({m for lst in g["_materials"] for m in lst})
            r["_geometries"] = sorted({m for lst in g["_geometries"] for m in lst})
            log(f"load_dataset(): merged {len(g)} reviews for {r['Article ID']} "
                f"(relevance: {rel}).")
        return r

    arts = pd.DataFrame([merge(g) for _, g in forms.groupby("Article ID", sort=True)])
    arts["_sort"] = arts["Article ID"].str.extract(r"(\d+)").astype(int)
    arts = arts.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    log(f"load_dataset(): article-level dataset n = {len(arts)}.")
    return arts


# ----------------------------------------------------------------------------
# Statistics + report
# ----------------------------------------------------------------------------

def compute_stats(arts: pd.DataFrame) -> dict:
    n = len(arts)
    tech = arts["MWP technique"].value_counts()
    order = [x for x in ("UT only", "IRT only", "UT + IRT", "Neither UT nor IRT")
             if x in tech.index]
    tech = tech[order]
    mat = pd.Series([m for lst in arts["_materials"] for m in lst]).value_counts()
    rel = arts["Relevance for TC MWP"].value_counts()
    rorder = [x for x in ("High", "Medium", "Low") if x in rel.index]
    rel = rel[rorder + [x for x in rel.index if x not in rorder]]
    geo_arts = arts[arts["_geometries"].map(len) > 0]
    geo = pd.Series([g for lst in geo_arts["_geometries"] for g in lst]).value_counts()
    st = {"n": n, "n_geo": len(geo_arts), "technique": tech, "materials": mat,
          "relevance": rel, "geometry": geo}
    for name in ("technique", "relevance"):
        log(f"compute_stats(): {name}: " +
            ", ".join(f"{k}: {v} ({100*v/n:.1f}%)" for k, v in st[name].items()))
    log("compute_stats(): materials (% of articles, multi-label): " +
        ", ".join(f"{k}: {100*v/n:.1f}%" for k, v in mat.items()))
    log(f"compute_stats(): geometries over n = {len(geo_arts)} (multi-label): " +
        ", ".join(f"{k}: {100*v/len(geo_arts):.1f}%" for k, v in geo.items()))
    return st


def save_summary_report(arts: pd.DataFrame, st: dict, path: str) -> None:
    n, ng = st["n"], st["n_geo"]
    years = pd.to_numeric(arts["Year"], errors="coerce")
    L = ["RILEM TC MWP — UT / IRT literature review forms: summary report",
         "=" * 64,
         f"Articles (unique): {n}   |   Coverage: {int(years.min())}-{int(years.max())}",
         "Source: review forms only (no original articles, no external sources).",
         "",
         "MWP TECHNIQUE (unit: article)"]
    L += [f"  {k:<22} {v:>3}  ({100*v/n:5.1f}%)" for k, v in st["technique"].items()]
    L += ["", f"RELEVANCE FOR TC MWP (unit: article)"]
    L += [f"  {k:<38} {v:>3}  ({100*v/n:5.1f}%)" for k, v in st["relevance"].items()]
    L += ["", f"MATERIAL TYPES (multi-label, % of {n} articles, sum > 100%)"]
    L += [f"  {k:<38} {v:>3}  ({100*v/n:5.1f}%)" for k, v in st["materials"].items()]
    L += ["", f"SPECIMEN GEOMETRIES in UT/IRT blocks (multi-label, % of {ng} articles)"]
    L += [f"  {k:<38} {v:>3}  ({100*v/ng:5.1f}%)" for k, v in st["geometry"].items()]
    L += ["", "CLASSIFICATION CATEGORY"]
    cat = arts["Classification category"].value_counts()
    L += [f"  {k:<55} {v:>3}" for k, v in cat.items()]
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")
    log(f"save_summary_report(): {path}")
