"""UIUX-073: Fixture with long revision ID and unbroken token for dynamic status reservation testing."""
import json
from branch_history import BranchHistory
from history_browser import render

LONG_REVISION_ID = 'feat/virtualized-2d-grid-with-asymmetric-spans-and-history-c98f820b784913c98b671a5392812d4a7536901234567890abcdef'
LOCALIZED_BRANCH_ID = 'cabang-rekonsiliasi-jejak-audit-terdistribusi-skala-2026'


def fixture():
    history = BranchHistory({'A1': 'awal'})
    history.commit('alpha', 'root', {'A1': 'pertama'})
    history.commit(LONG_REVISION_ID, 'alpha', {'B1': 'unbroken-long-id'})
    history.commit(LOCALIZED_BRANCH_ID, 'root', {'A1': 'kedua'})
    history.checkout(LONG_REVISION_ID)
    return {
        'html': render(history),
        'initial': {'id': LONG_REVISION_ID, 'text': f'root > alpha > {LONG_REVISION_ID}'},
        'recovery': {'id': LOCALIZED_BRANCH_ID, 'text': f'root > {LOCALIZED_BRANCH_ID}'},
        'long_id': LONG_REVISION_ID,
        'keyboard': {
            'activation_keys': ['Enter', 'Space'],
            'copy_button_selector': '.dag-breadcrumb-copy-btn',
            'status_selector': '#status',
            'expected_status_success': 'Silsilah rute berhasil disalin ke clipboard',
            'expected_status_failure': 'Gagal menyalin silsilah rute ke clipboard',
        },
    }


if __name__ == '__main__':
    print(json.dumps(fixture(), ensure_ascii=True))
