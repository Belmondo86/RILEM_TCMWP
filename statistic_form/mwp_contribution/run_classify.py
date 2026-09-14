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
import os
import sys
import tempfile

import main

HERE = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    # ---------------- paths ----------------
    'input_xlsx': os.path.join(HERE,
                               'TC_RILEM_Form_TX_AKLB_FULL_VERSION.xlsx'),
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


def run(cfg):
    res, tests, log = main.run_pipeline(cfg)
    failed = [t for t in tests if not t[1]]
    print('\n'.join(log))
    if failed:
        print(f'\n{len(failed)} TEST(S) FAILED — see run_log.txt')
        return 1
    print('\nAll tests passed.')
    return 0


if __name__ == '__main__':
    cfg = dict(CONFIG)
    if '--test' in sys.argv:
        cfg['output_dir'] = tempfile.mkdtemp(prefix='mwp_contribution_test_')
        print(f"TEST MODE — isolated output in {cfg['output_dir']}")
    sys.exit(run(cfg))
