"""Isolated native clipboard fixture; reuse the actual history preview unchanged."""
import json
from branch_history import BranchHistory
from history_browser import render


def fixture():
    history = BranchHistory({'A1': 'awal'})
    history.commit('alpha', 'root', {'A1': 'pertama'})
    history.commit('anak-雪', 'alpha', {'B1': 'unicode'})
    history.commit('beta & <baru>', 'root', {'A1': 'kedua'})
    history.checkout('anak-雪')
    return {
        'html': render(history),
        'initial': {'id': 'anak-雪', 'text': 'root > alpha > anak-雪'},
        'recovery': {'id': 'beta & <baru>', 'text': 'root > beta & <baru>'},
    }


if __name__ == '__main__':
    print(json.dumps(fixture(), ensure_ascii=True))
