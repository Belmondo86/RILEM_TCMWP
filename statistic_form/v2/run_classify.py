"""run_classify.py — THE ONLY FILE YOU NEED TO RUN.

RILEM TC 331-MWP — Primary-Contribution classification of the 155-paper
literature-review-form corpus.

Usage:
    python run_classify.py            # full run -> classification_output/
    python run_classify.py --test     # isolated test run in a temp directory

To correct a classification: edit the AI_tables/*.csv files (open them in
Excel), then rerun this script. Never edit the library files for rule changes.

ALL configuration lives below — paths, scoring thresholds, colours, fonts,
figure sizes. Nothing visual is hardcoded in the libraries.
"""
import glob
import os
import sys
import tempfile

import main

try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # interactive console / some IDE cells
    HERE = os.path.abspath(os.getcwd())
if not os.path.isdir(os.path.join(HERE, 'AI_tables')) and \
        os.path.isdir(os.path.join(os.getcwd(), 'AI_tables')):
    HERE = os.path.abspath(os.getcwd())

CONFIG = {
    # ---------------- paths ----------------
    # Leave as None to auto-locate the form (searches this folder, its parent,
    # and ./input). Or set an explicit path, or pass one on the command line:
    #     python run_classify.py "C:/path/to/TC_RILEM_Form_....xlsx"
    'input_xlsx': None,
    'tables_dir': os.path.join(HERE, 'AI_tables'),
    'output_dir': os.path.join(HERE, 'classification_output'),
    'figures_dirname': 'figures',
    'workbook_name': 'TC331_MWP_155papers_classification.xlsx',
    'results_csv': 'classification_results.csv',
    'log_name': 'run_log.txt',

    # ---------------- scoring thresholds ----------------
    'scoring': {
        # Application: number of evidence items needed for scores 2 and 3
        'app_bins': {'score2': 2, 'score3': 4},
        # Methodology: number of informative parameter fields for scores 2 / 3
        'meth_bins': {'score2': 3, 'score3': 6},
        # Signal processing: how many *basic* techniques equal an advanced one
        'sigproc_basic_for_2': 3,
        # Secondary contribution reported only when 2nd-highest score >= this
        'secondary_min_score': 2,
        # Reviewer Support = 2 needs ABK+ABL informative and >= this many words
        'reviewer_strong_words': 20,
    },

    # ---------------- workbook appearance ----------------
    'xlsx': {
        'font': 'Arial',
        'font_size': 10,
        'border_color': 'BFBFBF',
        'warning_color': 'C00000',
        'readme_width': 140,
        'summary_widths': [52, 12, 12, 110],
        'dist_widths': [38, 12, 12],
        'noutirt_widths': [9, 22, 7, 44, 34, 12, 40, 40],
        'fills': {                      # header colours per spec section 15
            'blue':   'BDD7EE',   # Application
            'green':  'C6E0B4',   # Methodology
            'red':    'F4B0A9',   # Data Analysis
            'lred':   'FBE2DE',   # DA sub-components
            'purple': 'D9C7E9',   # Rheological modelling
            'orange': 'F8CBAD',   # Reviewer assessment (tie-break only)
            'grey':   'D9D9D9',   # neutral / identification columns
        },
    },

    # ---------------- figure appearance ----------------
    'viz': {
        # False (default) = figures are only written as PNG files.
        # True = they are ALSO displayed (Spyder Plots pane, or a window).
        # Files are written either way.
        'show_figures': False,
        'dpi': 150,
        'base_fontsize': 10,
        'annot_fontsize': 9,
        'axis_headroom': 1.22,
        'bar_width': 7.5,
        'bar_height': 5,
        'barh_width': 9,
        'barh_row_height': 0.5,
        'barh_min_height': 2.6,
        'colors': {
            'blue':   '#2E75B6',
            'green':  '#70AD47',
            'red':    '#C0504D',
            'purple': '#8064A2',
            'orange': '#ED7D31',
            'grey':   '#7F7F7F',
        },
    },
}


INPUT_PATTERNS = ('TC_RILEM_Form*.xlsx', '*RILEM*Form*.xlsx', '*.xlsx')


def check_dependencies():
    """Report missing packages in plain language instead of an ImportError."""
    missing = []
    for mod, pipname in [('pandas', 'pandas'), ('openpyxl', 'openpyxl'),
                         ('matplotlib', 'matplotlib')]:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pipname)
    if missing:
        print('ERROR — missing Python package(s): ' + ', '.join(missing))
        print('Install them with:\n    pip install ' + ' '.join(missing))
        return False
    return True


def locate_input(explicit):
    """Find the form workbook. Returns a path, or None with guidance printed."""
    if explicit:
        if os.path.isfile(explicit):
            return explicit
        print(f'ERROR — the input file was not found:\n    {explicit}')
        return None
    search_dirs = [HERE, os.path.dirname(HERE), os.path.join(HERE, 'input')]
    for pattern in INPUT_PATTERNS:
        for d in search_dirs:
            hits = sorted(glob.glob(os.path.join(d, pattern)))
            hits = [h for h in hits
                    if not os.path.basename(h).startswith('~$')
                    and 'classification' not in os.path.basename(h).lower()]
            if hits:
                return hits[0]
    print('ERROR — could not find the review-form workbook.')
    print('Looked for TC_RILEM_Form*.xlsx in:')
    for d in search_dirs:
        print('    ' + os.path.abspath(d))
    print('Fix: put the .xlsx next to run_classify.py, or run:\n'
          '    python run_classify.py "C:/path/to/your_form.xlsx"')
    return None


def run(cfg):
    try:
        res, tests, log = main.run_pipeline(cfg)
    except ValueError as e:
        if 'Worksheet' in str(e) or 'sheet' in str(e).lower():
            print(f'ERROR — worksheet not found in {cfg["input_xlsx"]}')
            print('This module reads ONLY the sheet named exactly:\n'
                  '    Final for analysis AI and code')
            print('Check the tab name (trailing spaces and accents matter).')
            return 1
        raise
    except PermissionError:
        print('ERROR — cannot write the output file.')
        print('The workbook is probably still open in Excel. Close it and rerun.')
        return 1
    failed = [t for t in tests if not t[1]]
    print('\n'.join(log))
    if failed:
        print(f'\n{len(failed)} TEST(S) FAILED — see run_log.txt')
        return 1
    print('\nAll tests passed.')
    return 0


if __name__ == '__main__':
    if not check_dependencies():
        sys.exit(1)
    cfg = dict(CONFIG)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    path = locate_input(args[0] if args else cfg['input_xlsx'])
    if path is None:
        sys.exit(1)
    cfg['input_xlsx'] = path
    print(f'Input: {os.path.abspath(path)}')
    if not os.path.isdir(cfg['tables_dir']):
        print(f"ERROR — AI_tables folder not found at {cfg['tables_dir']}")
        print('Run the script from inside the mwp_contribution folder:\n'
              '    cd mwp_contribution\n    python run_classify.py')
        sys.exit(1)
    if '--test' in sys.argv:
        cfg['output_dir'] = tempfile.mkdtemp(prefix='mwp_contribution_test_')
        print(f"TEST MODE — isolated output in {cfg['output_dir']}")
    sys.exit(run(cfg))
