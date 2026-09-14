# Corrections & Audit — Bibliometric Pipeline
> Rapport unique. Chaque section = une session de corrections avec date/heure.

---

## Session 1 — Refactorisation initiale

### O-01 · Fusion `draw_network` dans `main.py`
Élimination de 6 appels `nx.draw_networkx_*` dupliqués entre `biblio_viz.py`
et `biblio_viz_API.py`. Une seule fonction `draw_network(G, ax, title, top_n,
label_min_degree, label_fontsize)` dans `main.py`.

### O-02 · Suppression `SAVE_TO_FILE` / `save_or_show`
Toujours sauvegarde fichier. `save_figure(fig, filename, output_dir, dpi)` dans
`main.py`. `matplotlib.use("Agg")` inconditionnel dans les run scripts.

### O-03 · Factorisation `_network_from_pairs` dans `biblio_viz_API.py`
Les 3 fonctions réseau API (institution coauthor, author cocitation, institution
cocitation) partagent un helper interne qui construit le graphe et délègue au
`draw_network` de `main.py`.

### O-04 · Police relative `_fs(delta)`
Toutes les tailles de police dans les viz utilisent
`plt.rcParams["font.size"] + delta` au lieu de valeurs hardcodées.

### O-05 · `resolve_output_dir(base)` dans `main.py`
Gestion intelligente des dossiers de sortie :
- Dossier absent → création silencieuse.
- Dossier existant → invite l'utilisateur `[1] Overwrite  [2] biblio_output_1`.

---

## Session 2 — Imports inutilisés & API dépréciée
*Corrections C-01 à C-03*

### C-01 · `import re` inutilisé — `biblio_API.py`
`re` n'est plus utilisé dans ce module après déplacement de `clean_doi`
vers `main.py`.
```python
# Supprimé
import re
```

### C-02 · `author_short_label` importé mais non utilisé — `biblio_API.py`
```python
# Avant
from main import CSV_SEP, CSV_ENCODING, clean_doi, author_short_label
# Après
from main import CSV_SEP, CSV_ENCODING, clean_doi
```

### C-03 · `plt.cm.get_cmap` déprécié — `biblio_viz_API.py`
Déprécié depuis Matplotlib 3.7, supprimé en 3.11.
```python
# Avant
colors = plt.cm.get_cmap(cmap)(np.linspace(...))
# Après
colors = matplotlib.colormaps[cmap](np.linspace(...))
```

---

## Session 3 — Rapport texte + zéro print dans les bibliothèques
*2026-06-12 13:30*

### C-04 · `print_summary_report` → `save_summary_report` — `biblio_data.py`
Le rapport de synthèse est maintenant écrit dans `output_dir/report.txt`.
Plus aucun `print` dans les bibliothèques.

**Fichier** : `biblio_data.py`
```python
# Avant
def print_summary_report(df):
    print("BIBLIOMETRIC REPORT")
    ...

# Après
def save_summary_report(df, output_dir):
    """Write corpus summary to output_dir/report.txt."""
    ...
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
```

### C-05 · Suppressions prints dans les bibliothèques — `biblio_data.py`, `biblio_API.py`, `biblio_viz_API.py`
Tous les `print` remplacés par :
- **Exceptions** pour les erreurs fatales (`FileNotFoundError`, `ConnectionError`, `ValueError`).
- **Silence** pour les messages de progression.

```python
# biblio_data.py — avant
print("  ERROR: file not found")
return None

# biblio_data.py — après
raise FileNotFoundError(f"File not found: {info_csv}")
```

### C-06 · `biblio_API.py` — `if failed:` vide après suppression du print
La suppression du print a laissé un bloc `if` vide → `IndentationError`.
```python
# Avant (cassé)
if failed:

if not records:

# Après
if not records:
```

### C-07 · `biblio_data.py` — `f.write("\\n".join(...))` avec `\\n` littéral
Lors de la génération par heredoc, les `\n` ont été doublés en `\\n`.
Corrigé par remplacement ligne-à-ligne.

---

## Session 4 — Noms de pays ISO-2 et rapport API
*2026-06-12 13:46*

### B-01 · Pays affichés comme codes ISO-2 dans le rapport API — `biblio_data.py`
Le rapport API affichait `CN   46` au lieu de `China             46`.
**Cause** : reverse lookup de `_COUNTRY_TO_ISO2` (qui contient des abbréviations
comme `"USA"→"US"`, `"UK"→"GB"`) donnait des résultats incorrects.

**Correction** : ajout d'un dict `ISO2_NAMES` autoritaire dans `main.py` (65 pays),
partagé entre `save_summary_report` et `plot_world_map`.

```python
# main.py — nouveau dict
ISO2_NAMES: dict[str, str] = {
    "CN": "China",  "US": "United States",  "FR": "France", ...
}

# biblio_data.py — utilisation
from main import ISO2_NAMES
name = ISO2_NAMES.get(cc, cc)
lines.append(f"    · {name:<28} {n}")
```

### B-02 · Fallback bar chart pays — `biblio_viz_API.py`
M�me cause que B-01. Le fallback (quand geopandas absent) utilisait aussi
le reverse lookup incorrect.

```python
# Avant
iso2_name = {v: k for k, v in _COUNTRY_TO_ISO2.items()}

# Après
from main import ISO2_NAMES
iso2_name = ISO2_NAMES
```

### Q-01 · Colonnes DataFrame non documentées — `biblio_viz.py`
Les fonctions de `biblio_viz.py` accèdent à `journal`, `type`, `n_authors`
sans vérification. Ces colonnes n'existent que dans le DataFrame local.
**Résolution** : ajout d'une note dans le docstring du module (pas de guards
pour garder le code simple — les deux pipelines n'échangent pas leurs DataFrames).

---

## Résultats des tests — Session 4
*2026-06-12 13:46*

```
  ✓  syntax:main.py
  ✓  syntax:biblio_data.py
  ✓  syntax:biblio_API.py
  ✓  syntax:biblio_viz.py
  ✓  syntax:biblio_viz_API.py
  ✓  syntax:run_local.py
  ✓  syntax:run_API.py
  ✓  run_local             17 PNGs, report.txt=✓
  ✓  run_API_demo          6 PNGs,  report.txt=✓
  ✓  no_prints_in_libraries   clean
  ✓  api_country_names        China=✓  United States=✓
  ✓  local_report             1099 chars, sections=✓
  ✓  api_report               1192 chars, sections=✓

  13/13 passed
```

---

## État des fichiers — version finale

| Fichier | Lignes | Rôle |
|---------|--------|------|
| `main.py` | 265 | Utilitaires partagés : `clean_doi`, `author_short_label`, `ISO2_NAMES`, `resolve_output_dir`, `apply_plot_style`, `save_figure`, `draw_network` |
| `biblio_data.py` | ~340 | Lecture CSV locale, inférence type/éditeur, `save_summary_report` |
| `biblio_API.py` | ~430 | CrossRef fetch, affiliations, mode démo curatif |
| `biblio_viz.py` | ~195 | 8 graphiques locaux (journal, Bradford, réseau co-auteur…) |
| `biblio_viz_API.py` | ~180 | 4 graphiques API (réseaux institutions/auteurs, carte mondiale) |
| `run_local.py` | ~140 | Runner local — config + 8 panneaux + report.txt |
| `run_API.py` | ~160 | Runner API — config + 4 figures + dashboard + report.txt |

---

## Comment modifier les programmes

### Changer les couleurs
Dans `run_local.py` ou `run_API.py`, section `# ── Visual style` :
```python
PALETTE = {
    "primary"   : "#4472C4",   # barres principales, nœuds forts
    "secondary" : "#2E86AB",   # barres secondaires, nœuds moyens
    "accent"    : "#F4A261",   # lignes de tendance, highlights
    "light"     : "#D6E8F5",   # nœuds faibles, fonds
    "dark"      : "#0D1B2A",   # texte, labels
    "muted"     : "#8FA7C0",   # grilles, arêtes
    "bg"        : "#F7F9FC",   # fond des figures
}
```

### Ajouter un graphique
1. Écrire `plot_mon_graphique(df, ax, ...)` dans `biblio_viz.py` (ou `biblio_viz_API.py`)
2. Ajouter dans `run_local.py` (section STEP 2) :
```python
fig, ax = plt.subplots(figsize=(10, 6))
bviz.plot_mon_graphique(df, ax, ...)
fig.tight_layout()
main.save_figure(fig, "mon_graphique.png", OUTPUT_DIR, DPI)
```

### Passer en mode live (CrossRef)
Dans `run_API.py` :
```python
DEMO_MODE = False
EMAIL     = "prenom.nom@institution.fr"
```

---

## Session 5 — Refactorisation biblio_data.py
*2026-06-12 13:58*

### C-08 · 3 sections vides supprimées — `biblio_data.py`
Sections 1, 2, 3 (DOI Cleaning, Label Builder, Author Short Label)
étaient vides depuis le déplacement de ces fonctions dans `main.py`.
Lignes L32–43 supprimées.

### C-09 · `import os` déplacé au niveau module — `biblio_data.py`
`import os` était caché à l'intérieur de `load_dataset()`.
Déplacé en tête de fichier avec les autres imports.

### C-10 · Alias `Counter` redondants supprimés — `save_summary_report`
`Ctr`, `Ctr2`, `Ctr3` importés localement alors que `Counter` était déjà
importé au niveau module.
```python
# Avant — 3 imports locaux redondants
from collections import Counter as Ctr
...
from collections import Counter as Ctr2
...
from collections import Counter as Ctr3

# Après — Counter module-level, expressions directes
top_authors = Counter(
    author_short_label(a) for auths in df["authors"] for a in auths
).most_common(5)
```

### C-11 · `from main import author_short_label` dupliqué supprimé
Importé au niveau module ET à l'intérieur de `save_summary_report`.
Import local retiré.

### C-12 · Docstring `load_dataset` corrigée
Mention de la colonne `label` (supprimée depuis plusieurs sessions) retirée.

### O-06 · `_infer_doc_type` — patterns littéraux : `re.search` → `str.startswith`
Les patterns DOI sont des préfixes fixes ; `re.search` était superflu.
Remplacement par des tuples de constantes + `any(doi.startswith(p) …)`.
Plus lisible, légèrement plus rapide.

```python
# Avant
if re.search(r"10\.1007/978-|10\.1007/3-", doi):
    return "book-chapter"
if re.search(r"10\.1051/e3sconf", doi):
    return "proceedings-article"

# Après
_BOOK_DOI = ("10.1007/978-", "10.1007/3-", "10.1201/")
_CONF_DOI = ("10.1051/e3sconf", "10.1088/1757-899", ...)

if any(doi.startswith(p) for p in _BOOK_DOI):
    return "book-chapter"
if any(doi.startswith(p) for p in _CONF_DOI):
    return "proceedings-article"
```

### O-07 · `_infer_publisher` — restructuré en tables de correspondance
Chaîne de `if re.search(...)` remplacée par deux listes de tuples :
`_PUBLISHER_DOI` (prefix → publisher) et `_PUBLISHER_NAME` (keywords → publisher).
Ajout d'un nouveau publisher facilite la maintenance.

```python
# Avant — 15 if/elif séquentiels
if re.search(r"10\.1007/978-|10\.1007/3-|10\.1007/s", doi):
    return "Springer"
if re.search(r"10\.1016/", doi):
    return "Elsevier"
...

# Après — boucle sur une table
_PUBLISHER_DOI = [
    ("10.1007/", "Springer"),
    ("10.1016/", "Elsevier"),
    ...
]
for prefix, pub in _PUBLISHER_DOI:
    if doi.startswith(prefix):
        return pub
```

### O-08 · Renumérotation des sections — `biblio_data.py`
Sections renumérotées 1–5 (suppression des 3 sections vides et du saut 7→9).

---

## Résultats des tests — Session 5
*2026-06-12 13:58*

```
  ✓  syntax:main.py
  ✓  syntax:biblio_data.py
  ✓  syntax:biblio_API.py
  ✓  syntax:biblio_viz.py
  ✓  syntax:biblio_viz_API.py
  ✓  syntax:run_local.py
  ✓  syntax:run_API.py
  ✓  run_local             17 PNGs, report=✓
  ✓  run_API_demo          6 PNGs,  report=✓
  ✓  _infer_doc_type       all 7 cases pass
  ✓  _infer_publisher      all 6 cases pass
  ✓  no_prints             clean
  ✓  local_report          1099 chars, names=✓
  ✓  api_report            1192 chars, names=✓

  14/14 passed
```

---

## Session 6 — Tests complets pipeline local
*2026-06-13 07:54*

### C-13 · Test `no_prints_in_libraries` — exclusion `main.py`
`main.py` contient des `print` **intentionnels** :
- `resolve_output_dir` : interaction utilisateur (`[1] Overwrite / [2] New folder`)
- `save_figure` : confirmation `✓ path`

Ces prints sont de l'UI, pas des effets de bord de bibliothèque.
Le test est restreint à `biblio_data.py` et `biblio_viz.py`.

### C-14 · Test `run_local:png_count` — dossier temporaire propre
L'ancien test utilisait `biblio_output/` en mode *overwrite*, qui conservait
les 9 vieux PNG des sessions précédentes (versions antérieures du runner).
Correction : exécution dans un `tempfile.mkdtemp()` vierge → exactement 8 PNG produits.

### C-15 · Flowchart `flowchart_local.png` — source fournie
Le diagramme est généré par **Python 3 + Matplotlib** (`FancyBboxPatch`,
`ax.annotate`). Aucun logiciel tiers requis.
Source archivée dans `flowchart_source.py`.

---

## Résultats des tests — Session 6
*2026-06-13 07:54*

```
  ✓  syntax:main.py
  ✓  syntax:biblio_data.py
  ✓  syntax:biblio_viz.py
  ✓  syntax:run_local.py
  ✓  no_prints_in_libraries          clean  (main.py exclu — UI intentionnel)
  ✓  no_unused_imports               clean
  ✓  run_local:execution             8 PNGs, report=✓  (dossier temporaire)
  ✓  run_local:png_count             expected 8, got 8
  ✓  run_local:correct_names         panel_top_journals, panel_bradford_law, …
  ✓  report_content                  all pass
  ✓  _infer_doc_type:11              all pass
  ✓  _infer_publisher:8              all pass
  ✓  author_short_label:8            all pass
  ✓  clean_doi:7                     all pass
  ✓  ISO2_NAMES:required             66 entries

  15/15 passed
```

---

## Session 7 — Tables d'inférence externalisées en CSV
*2026-06-13 08:12*

### O-09 · Tables de correspondance → fichiers CSV éditables par l'utilisateur

**Problème :** les tables de classification (préfixes DOI, mots-clés, éditeurs)
étaient hardcodées dans `biblio_data.py` comme tuples Python.
Elles ont été générées par l'IA et doivent pouvoir être vérifiées et corrigées
sans toucher au code Python.

**Solution :** chaque table devient un fichier CSV dans un dossier `biblio_tables/`.

| Fichier CSV | Colonnes | Rôle |
|-------------|----------|------|
| `table_book_doi.csv` | `prefix, comment` | Préfixes DOI → `book-chapter` |
| `table_conf_doi.csv` | `prefix, comment` | Préfixes DOI → `proceedings-article` |
| `table_conf_keywords.csv` | `keyword, comment` | Mots-clés venue → proceedings |
| `table_book_keywords.csv` | `keyword, comment` | Mots-clés venue → book chapter |
| `table_publisher_doi.csv` | `prefix, publisher, comment` | Préfixe DOI → éditeur |
| `table_publisher_name.csv` | `keyword, publisher, comment` | Mot-clé venue → éditeur |

**Comportement :**
- **Premier lancement** : `load_tables()` crée les CSV avec les valeurs par défaut IA.
- **Lancements suivants** : les CSV sont lus tels quels.
- **Correction utilisateur** : ouvrir le CSV dans Excel, corriger, sauvegarder → la correction est prise en compte dès le prochain `python run_local.py`.

```python
# run_local.py
TABLES_DIR = "biblio_tables"
tables = bdata.load_tables(TABLES_DIR)
df = bdata.load_dataset(info_csv=INFO_CSV, tables=tables)
```

### C-16 · Signatures `_infer_doc_type` et `_infer_publisher` mises à jour

Les deux fonctions d'inférence acceptent maintenant le dict `tables` en paramètre.
Plus aucune constante hardcodée à l'intérieur :

```python
# Avant
def _infer_doc_type(journal, doi):
    if any(doi.startswith(p) for p in _BOOK_DOI):  # constante interne

# Après
def _infer_doc_type(journal, doi, tables):
    if any(doi.startswith(p) for p in tables["book_doi"]):  # depuis CSV
```

### C-17 · Flowchart mis à jour

Le flowchart inclut maintenant le bloc orange **"User-editable lookup tables (CSV)"**
qui montre que les 6 CSV alimentent `_infer_doc_type` et `_infer_publisher`
via `load_tables()`.

---

## Résultats des tests — Session 7
*2026-06-13 08:12*

```
  ✓  syntax:main.py
  ✓  syntax:biblio_data.py
  ✓  syntax:biblio_viz.py
  ✓  syntax:run_local.py
  ✓  load_tables:creates_csvs           6 CSV créés au premier lancement
  ✓  load_tables:has_all_keys           6 clés retournées
  ✓  load_tables:no_overwrite           CSV inchangés au 2e lancement
  ✓  load_tables:user_edit_propagates   modification CSV → propagée à l'inférence
  ✓  _infer_doc_type:with_tables        all pass
  ✓  _infer_publisher:with_tables       all pass
  ✓  run_local:full_execution           8 PNGs, tables créées
  ✓  no_prints_in_libraries             clean

  12/12 passed
```

---

## Session 8 — Suppression des `_DEFAULT_*` dans biblio_data.py
*2026-06-13 08:20*

### C-18 · Génération des CSV + suppression des valeurs par défaut

Les 6 fichiers CSV ont d'abord été générés à partir des `_DEFAULT_*`
présents en session 7, puis ces constantes ont été **supprimées de `biblio_data.py`**.

`biblio_data.py` passe de **486 → 299 lignes** (-38 %).

Les CSV dans `biblio_tables/` deviennent la **seule source de vérité** :

```
biblio_tables/
├── table_book_doi.csv         3 entrées
├── table_conf_doi.csv         9 entrées
├── table_conf_keywords.csv   17 entrées
├── table_book_keywords.csv    7 entrées
├── table_publisher_doi.csv   15 entrées
└── table_publisher_name.csv  23 entrées
```

### C-19 · `load_tables` — comportement modifié

```python
# Avant (session 7) : créait les CSV si absents
if not os.path.isfile(path):
    default_df.to_csv(path, ...)

# Après (session 8) : lève FileNotFoundError si absent
if not os.path.isfile(path):
    raise FileNotFoundError(f"Missing lookup table: {path}")
```

`biblio_data.py` est maintenant un module pur (logique + I/O) sans données.
Les données de classification sont dans les CSV, versionnables et éditables
indépendamment du code.

---

## Résultats des tests — Session 8
*2026-06-13 08:20*

```
  ✓  syntax:main.py
  ✓  syntax:biblio_data.py
  ✓  syntax:biblio_viz.py
  ✓  syntax:run_local.py
  ✓  no_defaults_in_code              clean — aucune table hardcodée
  ✓  no_prints_in_libraries           clean
  ✓  load_tables:all_keys             book_doi:3 conf_doi:9 conf_kw:17
                                       book_kw:7 pub_doi:15 pub_name:23
  ✓  load_tables:raises_on_missing    FileNotFoundError si CSV absent
  ✓  user_edit_propagates             modification CSV → propagée
  ✓  _infer_doc_type:11               all pass
  ✓  _infer_publisher:8               all pass
  ✓  run_local:8_PNGs                 8 PNGs, report=✓
  ✓  line_count<350                   299 lignes

  13/13 passed
```

---

## Session 9 — Corrections CSV + refactorisation draw_network
*2026-06-13 08:31*

### C-20 · 3 entrées incorrectes supprimées de `table_conf_doi.csv`

| Préfixe supprimé | Raison |
|---|---|
| `10.1063/` | AIP Advances (journal) a le même préfixe → faux positifs. Les articles AIP Conference Proceedings sont captés par le mot-clé `"aip conf"` dans `table_conf_keywords.csv` |
| `10.1007/s11709` | Frontiers of Structural and Civil Engineering = **journal** Springer, pas des proceedings |
| `10.2749/` | Structural Engineering International = **journal** IABSE, pas des proceedings |

`table_conf_doi.csv` : 9 → **6 entrées**.

### C-21 · Cas spécial AIP Advances supprimé de `_infer_doc_type`

Avec `10.1063/` retiré du CSV, le cas spécial n'est plus nécessaire :

```python
# Avant — code de contournement en Python
if any(doi.startswith(p) for p in tables["conf_doi"]):
    if "10.1063/" in doi and "advances" in j:   # AIP Advances is a journal
        return "journal-article"
    return "proceedings-article"

# Après — logique pure, sans cas spécial
if any(doi.startswith(p) for p in tables["conf_doi"]):
    return "proceedings-article"
```

La distinction AIP Advances / AIP Conference Proceedings est maintenant
entièrement gérée par les CSV (préfixe vs mot-clé), sans exception hardcodée.

### O-10 · `draw_network` — refactorisation en 3 blocs nommés

`draw_network()` dans `main.py` restructurée avec des commentaires de bloc
pour une meilleure lisibilité. La logique est identique :

```python
# ── Keep only top_n most-connected nodes ─────
...
# ── Edges ────────────────────────────────────
nx.draw_networkx_edges(...)
# ── Nodes ────────────────────────────────────
nx.draw_networkx_nodes(...)
# ── Labels (only above threshold degree) ─────
nx.draw_networkx_labels(...)
```

---

## Résultats des tests — Session 9
*2026-06-13 08:31*

```
  ✓  syntax:main.py
  ✓  syntax:biblio_data.py
  ✓  syntax:biblio_viz.py
  ✓  syntax:run_local.py
  ✓  no_aip_special_case           clean
  ✓  conf_doi:6_entries            ['10.1051/e3sconf', '10.1088/1757-899',
                                    '10.1088/1742-6596', '10.1117/12.',
                                    '10.4028/', '10.1061/9780784']
  ✓  _infer_doc_type:13            13/13 pass  (dont AIP + Frontiers + SEB)
  ✓  _infer_publisher:8            all pass
  ✓  run_local:full                8 PNGs, report=✓
  ✓  no_unused_imports             clean
  ✓  no_prints_libs                clean

  11/11 passed
```

---

## Session 10 — Renommage AI_table + livraison GitHub
*2026-06-13 08:40*

### C-22 · Renommage `table_*.csv` → `AI_table_*.csv`

Le préfixe `AI_` signale que ces tables ont été générées par l'IA
et doivent être vérifiées par l'utilisateur.

| Ancien nom | Nouveau nom |
|---|---|
| `biblio_tables/table_book_doi.csv` | `AI_tables/AI_table_book_doi.csv` |
| `biblio_tables/table_conf_doi.csv` | `AI_tables/AI_table_conf_doi.csv` |
| `biblio_tables/table_conf_keywords.csv` | `AI_tables/AI_table_conf_keywords.csv` |
| `biblio_tables/table_book_keywords.csv` | `AI_tables/AI_table_book_keywords.csv` |
| `biblio_tables/table_publisher_doi.csv` | `AI_tables/AI_table_publisher_doi.csv` |
| `biblio_tables/table_publisher_name.csv` | `AI_tables/AI_table_publisher_name.csv` |

### C-23 · `biblio_data.py` — référence mise à jour

```python
# Avant
path = os.path.join(tables_dir, f"table_{name}.csv")

# Après
path = os.path.join(tables_dir, f"AI_table_{name}.csv")
```

### C-24 · `run_local.py` — `TABLES_DIR` mis à jour

```python
# Avant
TABLES_DIR = "biblio_tables"

# Après
TABLES_DIR = "AI_tables"     # AI-generated lookup CSVs
```

### O-11 · Flowchart amélioré

- Panneau orange **AI_tables/** avec les 6 fichiers CSV et leur nombre de lignes
- Annotation ✏ "Open in Excel to correct AI classifications"
- Flèches orange montrant que les tables alimentent `_infer_doc_type` et `_infer_publisher`
- Bloc run_local.py plus visible (panneau bleu à gauche)
- Légende mise à jour

---

## Résultats des tests — Session 10
*2026-06-13 08:40*

```
  ✓  syntax:main.py
  ✓  syntax:biblio_data.py
  ✓  syntax:biblio_viz.py
  ✓  syntax:run_local.py
  ✓  AI_tables:filenames             6 fichiers AI_table_*.csv
  ✓  no_old_table_refs               clean
  ✓  load_tables:6_keys              book_doi:3 conf_doi:6 conf_kw:17
                                      book_kw:7 pub_doi:15 pub_name:23
  ✓  load_tables:raises_on_missing   FileNotFoundError ✓
  ✓  _infer_doc_type:13              13/13
  ✓  _infer_publisher:8              all pass
  ✓  run_local:8_PNGs                8 PNGs, report=✓
  ✓  no_prints                       clean

  12/12 passed
```

---

## Session 11 — Flowchart Graphviz + README non-expert
*2026-06-13 08:50*

### O-12 · Flowchart régénéré avec Graphviz (DOT)

**Logiciel :** [Graphviz](https://graphviz.org) — `dot` version 2.43
**Source :** `flowchart_local.dot`
**Commande de génération :** `dot -Tpng -Gdpi=150 flowchart_local.dot -o flowchart_local.png`

Avantages par rapport à Python/Matplotlib :
- Placement automatique des nœuds et arêtes (`rankdir=TB`)
- Flèches orthogonales (`splines=ortho`) — propres et alignées
- Sous-graphes avec bordure (`cluster_ai`, `cluster_viz`)
- Source texte lisible et versionnable (`.dot`)
- Aucune coordonnée manuelle à calculer

Améliorations visuelles :
- Panneau orange AI_tables/ avec les 6 CSV individuels et leur nombre de lignes
- Annotation ✏ "Edit in Excel to correct AI classifications"
- Flèches couleur distincte par type (orange = tables, violet = helpers)
- Nœuds de sortie en forme de note (`shape=note`)
- run_local.py visible comme orchestrateur

### O-13 · README réécrit pour les non-experts

Structure révisée :
- Ouverture : explication en une phrase de ce que fait le programme
- Section "What you get" : description humaine de chaque figure produite
- Section "What you need" : pré-requis en langage simple + explication pip
- Section "How to install" : structure de dossier illustrée
- Section "How to run" : une commande + explication du dialogue de dossier
- Section "How to configure" : commentaires dans les exemples de code
- Section "How to correct the AI classifications" :
  - Explication du rôle des AI_tables
  - ⚠ Avertissement clair "ces tables ont été générées par une IA"
  - Workflow de correction en 4 étapes
  - Exemple concret (AIP Advances)
- Section "File descriptions" : tableau avec colonne "Should you edit it?"
- Section pipeline : diagramme Mermaid + explication en prose simple
- Section méthodologie : explication du workflow IA en langage courant

---

## Résultats des tests — Session 11
*2026-06-13 08:50*

```
  ✓  flowchart_local.dot    syntaxe DOT valide, PNG généré sans erreur
  ✓  README.md              282 lignes, sections clés présentes
  ✓  Mermaid diagram        intégré dans README (rendu natif GitHub)
```

---

## Session 12 — Tests finaux + livraison GitHub complète
*2026-06-23 11:20*

### C-25 · Licence mise à jour dans README.md

```
# Avant
MIT — free to use, modify and share, with attribution.

# Après
RILEM TC MWP — free to use for all members of the TC group.
```

### C-26 · Relecture README

Vérifications automatiques : liens internes, blocs de code fermés, doubles espaces.
Aucun problème détecté.

---

## Résultats des tests — Session 12
*2026-06-23 11:20*

```
  ✓  syntax:main.py
  ✓  syntax:biblio_data.py
  ✓  syntax:biblio_viz.py
  ✓  syntax:run_local.py
  ✓  no_prints                    clean
  ✓  no_unused_imports            clean
  ✓  AI_tables:schema_clean       all valid
  ✓  load_tables:ok               6 tables loaded
  ✓  _infer_doc_type:13           13/13 pass
  ✓  _infer_publisher:8           all pass
  ✓  author_short_label:8         all pass
  ✓  clean_doi:6                  all pass
  ✓  run_local:full               8 PNGs + report.txt ✓
  ✓  readme:sections              all sections present
  ✓  graphviz_dot:valid           renders OK

  15/15 passed
```
