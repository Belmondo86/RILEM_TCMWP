"""mwp_viz.py — generation of the 10 required figures.

Library file: no print() statements; all output saved to files.
Every colour, size and DPI comes from the VIZ config dict in run_classify.py —
nothing visual is hardcoded here.
"""
import os
import matplotlib

# The Agg (file-only) backend is the module default, per the repository
# convention that libraries write to files and never open windows. It is
# selected in make_all_figures() when viz['show_figures'] is False, so that
# an IDE's inline backend can be kept when the user opts in.
import matplotlib.pyplot as plt


def _pooled(series_of_lists):
    counts = {}
    for lst in series_of_lists:
        for v in lst:
            counts[v] = counts.get(v, 0) + 1
    return sorted(counts.items(), key=lambda kv: -kv[1])


def _split_types(series, drop):
    out = []
    for v in series:
        out.append([x.strip() for x in str(v).split(',')
                    if x.strip() and x.strip() not in drop])
    return out


def _finish(fig, path, viz):
    """Save the figure, then either display it or release it."""
    fig.savefig(path)
    if viz.get('show_figures'):
        plt.show()
    else:
        plt.close(fig)


def _barh(pairs, title, path, color, n_total, viz):
    cats = [p[0] for p in pairs][::-1]
    vals = [p[1] for p in pairs][::-1]
    fig, ax = plt.subplots(figsize=(viz['barh_width'],
                                    max(viz['barh_min_height'],
                                        viz['barh_row_height'] * len(cats) + 1)))
    ax.barh(cats, vals, color=color)
    for y, v in enumerate(vals):
        ax.text(v + 0.6, y, f'{v} ({v / n_total * 100:.1f}%)',
                va='center', fontsize=viz['annot_fontsize'])
    ax.set_xlabel(f'Number of papers (n = {n_total})')
    ax.set_title(title)
    ax.set_xlim(0, max(vals) * viz['axis_headroom'])
    fig.tight_layout()
    _finish(fig, path, viz)


def _bar(pairs, title, ylabel, path, colors, denom, viz):
    fig, ax = plt.subplots(figsize=(viz['bar_width'], viz['bar_height']))
    ax.bar([p[0] for p in pairs], [p[1] for p in pairs], color=colors)
    for x, (_, v) in enumerate(pairs):
        ax.text(x, v + 1, f'{v} ({v / denom * 100:.1f}%)', ha='center')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_ylim(0, max(v for _, v in pairs) * viz['axis_headroom'])
    fig.tight_layout()
    _finish(fig, path, viz)


def make_all_figures(res, fig_dir, viz):
    """Generate figures fig01..fig10 into fig_dir. Returns list of file paths."""
    os.makedirs(fig_dir, exist_ok=True)
    if not viz.get('show_figures'):
        matplotlib.use('Agg', force=True)   # file-only; opens no window
    plt.rcParams.update({'font.size': viz['base_fontsize'], 'figure.dpi': viz['dpi']})
    C = viz['colors']
    N = len(res)
    paths = []

    def fp(name):
        p = os.path.join(fig_dir, name)
        paths.append(p)
        return p

    # fig01 — UT only / IRT only / both (excluding Other from the denominator)
    tech = res['MWP Technique'].value_counts()
    utb = [('UT only', int(tech.get('UT', 0))),
           ('IRT only', int(tech.get('IR', 0))),
           ('Both (UT + IRT)', int(tech.get('IR/UT', 0)))]
    denom = sum(v for _, v in utb)
    excl = int(tech.get('Other / not explicitly UT or IR', 0))
    _bar(utb,
         'MWP technique: UT only vs IRT only vs both\n'
         f'({excl} papers without explicit UT/IRT excluded from the denominator)',
         f'Number of papers (denominator = {denom})',
         fp('fig01_technique_UT_IRT.png'),
         [C['blue'], C['green'], C['purple']], denom, viz)

    # fig02 — relevance
    order = ['High', 'Medium', 'Low', 'Not reported']
    rel = [(k, int((res['TC MWP Relevance'] == k).sum())) for k in order]
    _bar(rel, 'TC MWP relevance distribution (column ABJ)',
         f'Number of papers (n = {N})', fp('fig02_relevance.png'),
         [C['green'], C['orange'], C['red'], C['grey']], N, viz)

    # fig03 — primary contribution
    cats = ['Application Focus', 'Testing Methodology Focus', 'Data Analysis Type']
    pr = [(c, int((res['Primary'] == c).sum())) for c in cats]
    _bar(pr, f'Primary Contribution distribution (sums to {N})',
         f'Number of papers (n = {N})', fp('fig03_primary_contribution.png'),
         [C['blue'], C['green'], C['red']], N, viz)

    # fig04 / fig05 — materials, geometries
    _barh(_pooled(res['Materials']),
          'Material types (columns H:AT; non-exclusive)',
          fp('fig04_materials.png'), C['blue'], N, viz)
    _barh(_pooled(res['Geometries']),
          'Specimen geometries (all Geometry columns; non-exclusive)',
          fp('fig05_geometries.png'), C['green'], N, viz)

    # fig06 / fig07 — properties, identification methods
    props = _split_types(res['Property Types'],
                         ('Not reported', 'Other output (see raw)'))
    _barh(_pooled(props),
          'Properties / outputs obtained from UT/IRT (non-exclusive)',
          fp('fig06_properties.png'), C['red'], N, viz)
    ids = _split_types(res['Id Methods'], ('Not described', 'Domain reported only'))
    _barh(_pooled(ids), 'Property identification methods (non-exclusive)',
          fp('fig07_identification_methods.png'), C['purple'], N, viz)

    # fig08..fig10 — score distributions
    for num, (title, colname, color) in enumerate(
            [('Application Contribution Scores', 'App Score', C['blue']),
             ('Methodology Contribution Scores', 'Meth Score', C['green']),
             ('Data Analysis Contribution Scores', 'DA Score', C['red'])], start=8):
        pairs = [(str(s), int((res[colname] == s).sum())) for s in range(4)]
        _bar(pairs, f'Distribution of {title}',
             f'Number of papers (n = {N})',
             fp(f'fig{num:02d}_{colname.split()[0].lower()}_scores.png'),
             color, N, viz)
    return paths


if __name__ == '__main__':
    raise SystemExit(
        'mwp_viz.py is a library file and cannot be run directly.\n'
        'Run the entry point instead:\n'
        '    python run_classify.py\n'
        'In Spyder: open run_classify.py, then press F5 (Run file).'
    )
