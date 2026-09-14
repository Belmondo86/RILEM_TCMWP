"""
=============================================================================
  biblio_data.py  —  Local Bibliometric Data Layer
  -----------------------------------------------------------------------------
  Reads info_DOI_MWP.csv, infers document type and publisher,
  builds the analysis DataFrame — no internet required.

  Lookup tables live in CSV files (AI_tables/).
  Edit them in any spreadsheet app to correct misclassifications.

  Public API
  ----------
  load_tables(tables_dir)              → dict  (6 lookup tables)
  load_dataset(info_csv, tables)       → pd.DataFrame
  save_summary_report(df, output_dir)  → output_dir/report.txt

  Expected CSV files in tables_dir
  ---------------------------------
  table_book_doi.csv         prefix
  table_conf_doi.csv         prefix
  table_conf_keywords.csv    keyword
  table_book_keywords.csv    keyword
  table_publisher_doi.csv    prefix, publisher
  table_publisher_name.csv   keyword, publisher
=============================================================================
"""

import os
import re
import warnings
from collections import Counter

import pandas as pd

from main import CSV_SEP, CSV_ENCODING, clean_doi, author_short_label, ISO2_NAMES

warnings.filterwarnings("ignore")


# =============================================================================
#  SECTION 1 — TABLE LOADER
# =============================================================================

def load_tables(tables_dir: str) -> dict:
    """
    Load the 6 inference lookup tables from CSV files in tables_dir.

    Returns
    -------
    dict with keys:
        book_doi        list[str]
        conf_doi        list[str]
        conf_keywords   list[str]
        book_keywords   list[str]
        publisher_doi   list[tuple[str, str]]   (prefix, publisher)
        publisher_name  list[tuple[str, str]]   (keyword, publisher)

    Raises
    ------
    FileNotFoundError  if any expected CSV file is absent.
    """
    _SCHEMA: dict[str, tuple[str, ...]] = {
        "book_doi"       : ("prefix",),
        "conf_doi"       : ("prefix",),
        "conf_keywords"  : ("keyword",),
        "book_keywords"  : ("keyword",),
        "publisher_doi"  : ("prefix",  "publisher"),
        "publisher_name" : ("keyword", "publisher"),
    }

    tables: dict = {}
    for name, cols in _SCHEMA.items():
        path = os.path.join(tables_dir, f"AI_table_{name}.csv")
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Missing lookup table: {path}\n"
                f"Ensure the AI_tables/ folder is present in the project directory."
            )
        df = pd.read_csv(path, encoding="utf-8")

        if len(cols) == 1:               # single-column tables → list of strings
            col = cols[0]
            values = df[col].dropna().str.strip()
            if name in ("conf_keywords", "book_keywords"):
                values = values.str.lower()
            tables[name] = values.tolist()
        else:                             # two-column tables → list of (a, b) tuples
            a_col, b_col = cols
            a = df[a_col].dropna().str.strip()
            b = df[b_col].dropna().str.strip()
            if name == "publisher_name":
                a = a.str.lower()
            tables[name] = list(zip(a, b))

    return tables


# =============================================================================
#  SECTION 2 — DOCUMENT TYPE INFERENCE
# =============================================================================

def _infer_doc_type(journal: str, doi: str, tables: dict) -> str:
    """
    Classify as 'journal-article', 'proceedings-article', or 'book-chapter'.

    Pass 1 — DOI prefix   (table_book_doi / table_conf_doi)
    Pass 2 — Venue name   (table_book_keywords / table_conf_keywords)
    Pass 3 — Heuristics   (ordinal editions, ACRONYM+year)
    """
    j   = journal.lower().strip()
    doi = doi.lower()

    if any(doi.startswith(p) for p in tables["book_doi"]):
        return "book-chapter"
    if any(doi.startswith(p) for p in tables["conf_doi"]):
        return "proceedings-article"

    if any(k in j for k in tables["book_keywords"]):
        return "book-chapter"
    if any(k in j for k in tables["conf_keywords"]):
        return "proceedings-article"

    if re.search(r"^\d+\s*(st|nd|rd|th)\b", j):      # "39th International …"
        return "proceedings-article"
    if re.search(r"^[A-Z]{2,}\s+\d{4}\b", journal):   # "CICTP 2019"
        return "proceedings-article"

    return "journal-article"


# =============================================================================
#  SECTION 3 — PUBLISHER INFERENCE
# =============================================================================

def _infer_publisher(journal: str, doi: str, tables: dict) -> str:
    """
    Return publisher name from DOI prefix (table_publisher_doi)
    or venue keyword (table_publisher_name). Falls back to 'Other'.
    """
    doi = doi.lower()
    j   = journal.lower()

    for prefix, pub in tables["publisher_doi"]:
        if doi.startswith(prefix):
            return pub

    for keyword, pub in tables["publisher_name"]:
        if keyword in j:
            return pub

    return "Other"


# =============================================================================
#  SECTION 4 — CSV LOADER
# =============================================================================

def _load_info_csv(filepath: str) -> dict[str, dict]:
    """
    Read metadata CSV → dict keyed by normalised DOI.
    Rows with missing/invalid DOI get a synthetic key __no_doi_<idx>.
    """
    df = pd.read_csv(filepath, sep=CSV_SEP, encoding=CSV_ENCODING)
    lookup: dict[str, dict] = {}
    for idx, row in df.iterrows():
        doi         = clean_doi(str(row.get("DOI", ""))) or f"__no_doi_{idx}"
        authors_str = str(row.get("Authors","")) if pd.notna(row.get("Authors")) else ""
        year        = row.get("Year")
        lookup[doi] = {
            "doi"    : doi,
            "authors": [a.strip() for a in authors_str.split(" and ") if a.strip()],
            "year"   : int(year) if pd.notna(year) else None,
            "journal": str(row.get("Journal / Conference",""))
                       if pd.notna(row.get("Journal / Conference")) else "",
            "title"  : str(row.get("Title",""))
                       if pd.notna(row.get("Title")) else "",
        }
    return lookup


# =============================================================================
#  SECTION 5 — DATASET BUILDER
# =============================================================================

def _build_from_info(info_lookup: dict, tables: dict) -> pd.DataFrame:
    """Assemble DataFrame; type and publisher inferred from lookup tables."""
    records = []
    for doi, info in info_lookup.items():
        journal = info["journal"]
        records.append({
            "doi"         : doi,
            "year"        : info["year"],
            "journal"     : journal,
            "publisher"   : _infer_publisher(journal, doi, tables),
            "type"        : _infer_doc_type(journal, doi, tables),
            "cited_by"    : 0,
            "references_n": 0,
            "authors"     : info["authors"],
            "n_authors"   : len(info["authors"]),
            "title"       : info["title"],
        })
    return pd.DataFrame(records)


# =============================================================================
#  SECTION 6 — PUBLIC API
# =============================================================================

def load_dataset(info_csv: str, tables: dict) -> pd.DataFrame:
    """
    Build the analysis DataFrame from the metadata CSV.

    Parameters
    ----------
    info_csv : path to info_DOI_MWP.csv
    tables   : dict returned by load_tables()

    Returns
    -------
    pd.DataFrame  columns: doi, year, journal, publisher, type,
                           cited_by, references_n, authors, n_authors, title

    Raises
    ------
    FileNotFoundError  if info_csv does not exist
    ValueError         if the resulting DataFrame is empty
    """
    if not os.path.isfile(info_csv):
        raise FileNotFoundError(f"File not found: {info_csv}")

    df = _build_from_info(_load_info_csv(info_csv), tables)

    if df.empty:
        raise ValueError("Empty dataset — check CSV format.")

    return df


def save_summary_report(df: pd.DataFrame, output_dir: str) -> None:
    """Write corpus summary to output_dir/report.txt."""
    top_authors = Counter(
        author_short_label(a) for auths in df["authors"] for a in auths
    ).most_common(5)

    sep   = "=" * 58
    lines = [sep, "  BIBLIOMETRIC REPORT", sep,
             f"  Articles analysed           : {len(df)}"]

    if df["year"].notna().any():
        lines.append(f"  Coverage period             : "
                     f"{int(df['year'].min())} – {int(df['year'].max())}")

    if "journal" in df.columns:
        lines.append(f"  Distinct journals / venues  : {df['journal'].nunique()}")

    if "type" in df.columns:
        labels = {"journal-article":     "Journal articles",
                  "proceedings-article": "Conference papers",
                  "book-chapter":        "Book chapters"}
        lines.append("  Document types              :")
        for dtype, cnt in df["type"].value_counts().items():
            lines.append(f"    · {labels.get(dtype, dtype):<25} {cnt}")

    if df["cited_by"].sum() > 0:
        lines += [f"  Total citations             : {df['cited_by'].sum():,}",
                  f"  Median citations / article  : {df['cited_by'].median():.1f}"]

    mean_a = (df["n_authors"].mean() if "n_authors" in df.columns
              else df["authors"].apply(len).mean())
    lines.append(f"  Mean authors / article      : {mean_a:.2f}")
    lines.append(f"  Articles with valid DOI     : "
                 f"{df['doi'].str.startswith('10.').sum()}")

    if "countries" in df.columns:
        c_count: Counter = Counter(c for cl in df["countries"] for c in cl)
        lines += ["", "  Top 5 countries :"]
        for cc, n in c_count.most_common(5):
            lines.append(f"    · {ISO2_NAMES.get(cc, cc):<28} {n}")

    if "institutions" in df.columns:
        i_count: Counter = Counter(ins for il in df["institutions"] for ins in il)
        lines += ["", "  Top 5 institutions :"]
        for name, n in i_count.most_common(5):
            lines.append(f"    · {name[:48]:<48} {n}")
    elif "journal" in df.columns:
        lines += ["", "  Top 5 journals / conferences :"]
        for venue, cnt in df["journal"].value_counts().head(5).items():
            lines.append(f"    · {venue[:50]:<50}  {cnt}")

    lines += ["", "  Top 5 authors (by article count) :"]
    for name, cnt in top_authors:
        lines.append(f"    · {name:<30}  {cnt}")
    lines.append(sep)

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
