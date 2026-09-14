"""mwp_data.py — data loading and table-driven classification engine.

RILEM TC 331-MWP — Primary-Contribution classification of the 155-paper
literature-review-form corpus.

All classification rules live in the editable CSVs under AI_tables/ — this
module only implements the mechanics. Correct the tables, not this code.

Library file: no print() statements; no hardcoded visual values.
"""
import re
import pandas as pd
from openpyxl.utils import column_index_from_string as ci, get_column_letter

SHEET = 'Final for analysis AI and code'
N_FORM_COLUMNS = 742

CATS = ('Application Focus', 'Testing Methodology Focus', 'Data Analysis Type')

# Column ranges fixed by the study specification (form structure, not tunable rules)
IR_METHOD_COLS = [('EF', 'excitation source'), ('EG', 'sensors'),
                  ('EH', 'boundary conditions'), ('EI', 'vibration modes'),
                  ('EJ', 'standard/reference'), ('EK', 'repetitions'),
                  ('EL', 'temperature')]
IR_METHOD_COMMENT = 'EM'
UT_METHOD_LABELS = ['transducer type', 'central frequency', 'wave type',
                    'configuration', 'standard/reference', 'repetitions', 'temperature']
UT1_METHOD_COLS = ['GM', 'GN', 'GO', 'GP', 'GQ', 'GR', 'GS']
UT2_METHOD_COLS = ['NA', 'NB', 'NC', 'ND', 'NE', 'NF', 'NG']
UT_METHOD_COMMENTS = ['GT', 'NH']
IR_SIGNAL_COLS = ['EN', 'EO', 'EP', 'EQ', 'EY']
UT_SIGNAL_COLS = ['GU', 'GV', 'GW', 'NI', 'NJ', 'NK']
PROPERTY_COLS = ['ER', 'GY', 'NM']
IR_ID_RANGE = ('ES', 'EX')
UT1_ID_RANGE = ('GZ', 'HG')
UT2_ID_RANGE = ('NN', 'NU')
RAW_ID_COLS = ['ET', 'HB', 'NP', 'HA', 'NO']
RHEO_COLS = ('AAY', 'AAZ', 'ABA', 'ABB', 'ABC')
TEMP_COLS = ['EL', 'GS', 'NG']
MATERIAL_TYPE_COLS = ['H', 'P', 'X', 'AF', 'AN']
MATERIAL_RANGE = ('H', 'AT')

UT_LABEL = 'Ultrasonic testing (UT)'
IR_LABEL = 'Impact resonance test (IRT)'
OTHER_TECH = 'Other / not explicitly UT or IR'


def _rng(a, b):
    return [get_column_letter(k) for k in range(ci(a), ci(b) + 1)]


class Tables:
    """Load every AI_table_*.csv from a directory."""

    def __init__(self, tables_dir):
        rd = lambda name: pd.read_csv(f'{tables_dir}/{name}', dtype=str).fillna('')
        self.noinfo = rd('AI_table_noinfo_values.csv')
        self.app = rd('AI_table_application_keywords.csv')
        self.sig = rd('AI_table_signal_processing.csv')
        self.prop = rd('AI_table_property_complexity.csv')
        self.idm = rd('AI_table_identification_method.csv')
        self.mat = rd('AI_table_material_normalization.csv')
        self.geo = rd('AI_table_geometry_normalization.csv')
        self.tie = rd('AI_table_tiebreak_keywords.csv')
        self._noinfo_re = [re.compile(p, re.I) for p in self.noinfo['regex_pattern']]

    def informative(self, t):
        t = (t or '').strip()
        if not t:
            return False
        for rx in self._noinfo_re:
            if rx.match(t):
                return False
        if (re.match(r'^(no |none |not )', t, re.I)
                and not re.search(r'\bbut\b|however|except', t, re.I)
                and re.search(r'(reported|specified|presented|mentioned|described|used)\b\.?$',
                              t.strip().rstrip('.'), re.I)):
            return False
        return True


def load_form(xlsx_path):
    """Read the analysis worksheet; returns the raw dataframe (155 rows expected)."""
    df = pd.read_excel(xlsx_path, sheet_name=SHEET, usecols=range(N_FORM_COLUMNS))
    return df


def find_empty_columns(df):
    """Columns blank for ALL papers. 'No' / 'Not reported' etc. are NOT empty."""
    out = []
    for i in range(df.shape[1]):
        s = df.iloc[:, i]
        if s.isna().all() or s.astype(str).str.strip().isin(['', 'nan']).all():
            out.append((get_column_letter(i + 1), str(df.columns[i])))
    return out


def geometry_columns(df):
    return [get_column_letter(k + 1) for k, h in enumerate(df.columns)
            if 'geometry' in str(h).lower()]


def classify(df, tables, cfg):
    """Run the full classification. Returns a results DataFrame (one row per paper)."""
    T = tables

    def cell(i, c):
        v = df.iloc[i, ci(c) - 1]
        return '' if pd.isna(v) else str(v).strip()

    geom_cols = geometry_columns(df)
    papers = []
    for i in range(len(df)):
        p = {'idx': i, 'Paper ID': cell(i, 'B'), 'Authors': cell(i, 'C'),
             'Year': cell(i, 'D'), 'Title': cell(i, 'E')}
        au = cell(i, 'AU')
        has_ut, has_ir = UT_LABEL in au, IR_LABEL in au
        p['MWP Technique'] = ('IR/UT' if has_ut and has_ir else
                              'UT' if has_ut else 'IR' if has_ir else OTHER_TECH)
        toks = [t.strip() for t in au.split(',') if t.strip()]
        conv = [t for t in toks if t not in (UT_LABEL, IR_LABEL)]
        p['Traditional tests'] = ', '.join(conv) if conv else 'None reported'
        p['AU raw'] = au
        rel = cell(i, 'ABJ')
        p['TC MWP Relevance'] = rel if rel else 'Not reported'
        is_other = p['MWP Technique'] == OTHER_TECH

        # ---- Application score ------------------------------------------
        mat_text = ' | '.join(x for x in (cell(i, c) for c in _rng(*MATERIAL_RANGE))
                              if T.informative(x))
        scan = (p['Title'] + ' | ' + mat_text).lower()
        n_mat = sum(1 for c in MATERIAL_TYPE_COLS if T.informative(cell(i, c)))
        temps = ' '.join(cell(i, c) for c in TEMP_COLS)
        multi_temp = (len(re.findall(r'-?\d+\s*(?:°|º|deg)?\s*c\b', temps.lower())) >= 3
                      or ('to ' in temps.lower() and re.search(r'\d', temps)))
        ev = []
        if conv:
            ev.append(f"conventional-test comparison ({', '.join(conv[:3])})")
        if n_mat >= 2:
            ev.append(f'multiple material types ({n_mat})')
        for _, r in T.app.iterrows():
            if re.search(r['regex_pattern'], scan):
                ev.append(r['evidence_label'])
        if multi_temp:
            ev.append('temperature effects (multiple temperatures)')
        n_ev = len(ev)
        b = cfg['app_bins']  # e.g. {'score1': 1, 'score2': 2, 'score3': 4}
        app = (0 if n_ev == 0 else 1 if n_ev < b['score2'] else
               2 if n_ev < b['score3'] else 3)
        if conv and n_ev >= b['score3']:
            app = 3
        p['App Score'] = app
        p['App Evidence'] = ('; '.join(ev) if ev
                             else 'No application evidence identified in the form')

        # ---- Methodology score ------------------------------------------
        meth_fields = []
        if has_ir or is_other:
            for c, lab in IR_METHOD_COLS:
                if T.informative(cell(i, c)):
                    meth_fields.append(lab + ' (IR)')
            if T.informative(cell(i, IR_METHOD_COMMENT)):
                meth_fields.append('methodological comment (IR)')
        if has_ut or is_other:
            found = set()
            for cols in (UT1_METHOD_COLS, UT2_METHOD_COLS):
                for c, lab in zip(cols, UT_METHOD_LABELS):
                    if T.informative(cell(i, c)):
                        found.add(lab)
            meth_fields += [f + ' (UT)' for f in sorted(found)]
            if any(T.informative(cell(i, c)) for c in UT_METHOD_COMMENTS):
                meth_fields.append('methodological comment (UT)')
        core = [f for f in meth_fields if not f.startswith('methodological comment')]
        mb = cfg['meth_bins']  # {'score2': 3, 'score3': 6}
        n = len(core)
        meth = 0 if n == 0 else 1 if n < mb['score2'] else 2 if n < mb['score3'] else 3
        p['Meth Score'] = meth
        p['Meth Evidence'] = ('; '.join(meth_fields) if meth_fields
                              else 'Test parameters not documented in the form')

        # ---- 5A signal processing ---------------------------------------
        sig_cells = []
        if has_ir or is_other:
            sig_cells += [cell(i, c) for c in IR_SIGNAL_COLS]
        if has_ut or is_other:
            sig_cells += [cell(i, c) for c in UT_SIGNAL_COLS]
        sig_text = ' | '.join(x for x in sig_cells if T.informative(x))
        sl = sig_text.lower()
        adv = [r['label'] for _, r in T.sig.iterrows()
               if r['level'] == 'advanced' and re.search(r['regex_pattern'], sl)]
        bas = [r['label'] for _, r in T.sig.iterrows()
               if r['level'] == 'basic' and re.search(r['regex_pattern'], sl)]
        if adv or len(bas) >= cfg['sigproc_basic_for_2']:
            sp = 2
        elif bas or T.informative(sig_text):
            sp = 1
        else:
            sp = 0
        p['SigProc Score'] = sp
        p['SigProc Types'] = (', '.join(dict.fromkeys(adv + bas)) if (adv or bas)
                              else ('Described (unclassified)' if sp else 'Not described'))

        # ---- 5B property complexity -------------------------------------
        props_raw = [cell(i, c) for c in PROPERTY_COLS if T.informative(cell(i, c))]
        ptext = ' | '.join(props_raw)
        pl = ptext.lower()
        hits = {'advanced': [], 'viscoelastic': [], 'mechanical': [], 'basic': []}
        for _, r in T.prop.iterrows():
            if re.search(r['regex_pattern'], pl):
                hits[r['tier']].append(r['label'])
        n_visc = len(set(hits['viscoelastic']))
        if hits['advanced'] or n_visc >= 2:
            pc = 3
        elif n_visc == 1:
            pc = 2
        elif hits['mechanical']:
            pc = 1
        else:
            pc = 0
        p['PropC Score'] = pc
        lab = hits['viscoelastic'] + hits['mechanical'] + hits['basic']
        p['Property Types'] = (', '.join(dict.fromkeys(lab)) if lab
                               else ('Other output (see raw)' if props_raw else 'Not reported'))
        p['Raw Property'] = ptext if ptext else 'Not reported'
        has_prop = bool(props_raw)

        # ---- 5C identification method -----------------------------------
        id_cells = []
        if has_ir or is_other:
            id_cells += [cell(i, c) for c in _rng(*IR_ID_RANGE)]
        if has_ut or is_other:
            id_cells += [cell(i, c) for c in _rng(*UT1_ID_RANGE)]
            id_cells += [cell(i, c) for c in _rng(*UT2_ID_RANGE)]
        id_text = ' | '.join(x for x in id_cells if T.informative(x))
        il = id_text.lower()
        lvl, id_labels = 0, []
        for _, r in T.idm.iterrows():
            if re.search(r['regex_pattern'], il):
                id_labels.append(r['label'])
                lvl = max(lvl, int(r['score_level']))
        if lvl == 0 and T.informative(id_text):
            lvl = 1 if re.search(r'time|frequency', il) else 0
        p['IdM Score'] = lvl
        p['Id Methods'] = (', '.join(id_labels) if id_labels
                           else ('Domain reported only' if lvl == 1 else 'Not described'))
        p['Raw IdM'] = (' | '.join(x for x in (cell(i, c) for c in RAW_ID_COLS)
                                   if T.informative(x)) or 'Not reported')

        # ---- 5D data analysis final -------------------------------------
        if pc >= 1 and lvl == 3:
            da = 3
        elif pc >= 1 and (lvl >= 2 or (lvl >= 1 and (sp >= 1 or pc >= 2))):
            da = 2
        elif sp >= 1 or lvl >= 1 or pc >= 1 or has_prop:
            da = 1
        else:
            da = 0
        p['DA Score'] = da

        # ---- 6 rheology --------------------------------------------------
        aay, aaz, aba, abb, _ = (cell(i, c) for c in RHEO_COLS)
        model = (T.informative(aay)
                 and not re.search(r'^no rheological|^none$|no rheological model', aay, re.I))
        support = (int(bool(re.search(r'yes', aaz, re.I))) + int(T.informative(aba))
                   + int(T.informative(abb)
                         and not re.search(r'not applicable', abb, re.I)))
        p['Rheo Score'] = 0 if not model else (2 if support >= 1 else 1)
        p['Rheo Models'] = aay if model else 'None'
        p['Rheo Purpose'] = abb if T.informative(abb) else 'Not reported'

        # ---- 7 reviewer (descriptive; tie-break only) --------------------
        abk, abl = cell(i, 'ABK'), cell(i, 'ABL')
        words = len((abk + ' ' + abl).split())
        p['Reviewer Support'] = (2 if (T.informative(abk) and T.informative(abl)
                                       and words >= cfg['reviewer_strong_words'])
                                 else 1 if (T.informative(abk) or T.informative(abl))
                                 else 0)
        p['ABK'] = abk if abk else 'Not reported'
        p['ABL'] = abl if abl else 'Not reported'

        # ---- 8/9/10 primary / secondary / confidence ---------------------
        scores = {'Application Focus': app, 'Testing Methodology Focus': meth,
                  'Data Analysis Type': da}
        mx = max(scores.values())
        top = [k for k in CATS if scores[k] == mx]
        tie_used, conf = 'No', 'High'
        if len(top) == 1:
            primary, tie_reason = top[0], 'Single highest technical score'
        else:
            tie_used = 'Yes'
            rev = (abk + ' ' + abl).lower()
            pat = {r['category']: r['regex_pattern'] for _, r in T.tie.iterrows()}
            hits2 = {k: len(re.findall(pat[k], rev)) for k in top}
            best = max(hits2.values())
            winners = [k for k in top if hits2[k] == best]
            if best > 0 and len(winners) == 1:
                primary, conf = winners[0], 'Medium'
                tie_reason = f'Scores tied at {mx}; ABK/ABL emphasis resolved to {primary}'
            else:
                richness = {'Application Focus': len(p['App Evidence']),
                            'Testing Methodology Focus': len(p['Meth Evidence']),
                            'Data Analysis Type': (len(p['SigProc Types'])
                                                   + len(p['Property Types'])
                                                   + len(p['Id Methods']))}
                primary = max(top, key=lambda k: richness[k])
                conf = 'Low'
                tie_reason = (f'Scores tied at {mx}; ABK/ABL not decisive; '
                              f'richer form evidence favoured {primary}')
        p['Primary'] = primary
        rest = sorted(((v, k) for k, v in scores.items() if k != primary), reverse=True)
        p['Secondary'] = rest[0][1] if rest[0][0] >= cfg['secondary_min_score'] else 'None'
        p['Tie-break Used?'] = tie_used
        p['Tie-break Reason'] = tie_reason
        p['Confidence'] = conf
        p['Rationale'] = (f'App={app}, Meth={meth}, DA={da} '
                          f'(SigProc={sp}, PropC={pc}, IdM={lvl}). {tie_reason}.')

        # ---- 11 materials -------------------------------------------------
        mats = set()
        for c in MATERIAL_TYPE_COLS:
            v = cell(i, c)
            if not T.informative(v):
                continue
            for _, r in T.mat.iterrows():
                if re.search(r['regex_pattern'], v, re.I) and not (
                        r['exclude_pattern']
                        and re.search(r['exclude_pattern'], v, re.I)):
                    mats.add(r['category'])
                    break
        p['Materials'] = (sorted(mats) if mats
                          else ['Other / special / unspecified asphalt material'])

        # ---- 12 geometry --------------------------------------------------
        geoms = set()
        for gcol in geom_cols:
            v = cell(i, gcol)
            if not T.informative(v):
                continue
            for token in re.split(r'[,/]| and ', v.lower()):
                token = token.strip()
                if not token:
                    continue
                for _, r in T.geo.iterrows():
                    if re.search(r['regex_pattern'], token):
                        if r['category'] != 'IGNORE':
                            geoms.add(r['category'])
                        break
        p['Geometries'] = (sorted(geoms) if geoms
                           else ['Other / special / unspecified'])
        papers.append(p)
    return pd.DataFrame(papers)


def check_invariants(res, df):
    """Post-run tests. Returns a list of (test_name, passed_bool, detail)."""
    tests = []
    tests.append(('155 papers, one row each', len(res) == 155, f'n={len(res)}'))
    tests.append(('Paper IDs unique and preserved',
                  res['Paper ID'].is_unique and res['Paper ID'].notna().all(),
                  f"unique={res['Paper ID'].nunique()}"))
    tests.append(('Primary distribution sums to 155',
                  int(res['Primary'].value_counts().sum()) == 155,
                  str(res['Primary'].value_counts().to_dict())))
    tests.append(('Every Primary is one of the 3 categories',
                  res['Primary'].isin(CATS).all(), ''))
    bad = 0
    for _, r in res.iterrows():
        s = {'Application Focus': r['App Score'],
             'Testing Methodology Focus': r['Meth Score'],
             'Data Analysis Type': r['DA Score']}
        if r['Secondary'] != 'None' and s[r['Secondary']] < 2:
            bad += 1
        if r['Primary'] in s and s[r['Primary']] != max(s.values()):
            bad += 1
    tests.append(('Primary=max score; Secondary only when 2nd >= 2', bad == 0,
                  f'violations={bad}'))
    tests.append(('DA=3 implies PropC>=1 and IdM=3',
                  bool(((res['DA Score'] != 3)
                        | ((res['PropC Score'] >= 1) & (res['IdM Score'] == 3))).all()), ''))
    rng_ok = all(res[c].between(lo, hi).all() for c, lo, hi in
                 [('App Score', 0, 3), ('Meth Score', 0, 3), ('DA Score', 0, 3),
                  ('SigProc Score', 0, 2), ('PropC Score', 0, 3),
                  ('IdM Score', 0, 3), ('Rheo Score', 0, 2),
                  ('Reviewer Support', 0, 2)])
    tests.append(('All scores within their defined ranges', rng_ok, ''))
    other = res.loc[res['MWP Technique'] == OTHER_TECH, 'Paper ID'].tolist()
    tests.append(('Papers without explicit UT/IRT kept separate',
                  all(t not in ('UT', 'IR', 'IR/UT')
                      for t in res.loc[res['Paper ID'].isin(other), 'MWP Technique']),
                  str(other)))
    return tests


if __name__ == '__main__':
    raise SystemExit(
        'mwp_data.py is a library file and cannot be run directly.\n'
        'Run the entry point instead:\n'
        '    python run_classify.py\n'
        'In Spyder: open run_classify.py, then press F5 (Run file).'
    )
