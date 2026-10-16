"""Parent acceptance: evidence must fail closed, not just match final labels."""
import copy
import unittest
from pathlib import Path
import json
from clipboard_status_ownership import audit_ownership_record


class OwnershipContract(unittest.TestCase):
    def record(self, scenario='pendingCheckoutSuccess'):
        data = json.loads((Path(__file__).parent.parent / 'references/uiux-074-browser.json').read_text())
        return copy.deepcopy(next(r for r in data['records'] if r['scenario'] == scenario))

    def reject(self, r):
        try:
            self.assertFalse(audit_ownership_record(r)['passed'])
        except (ValueError, KeyError, TypeError):
            pass

    def test_absent_events_rejected(self):
        r = self.record(); r.pop('eventTrace'); self.reject(r)

    def test_empty_mutations_rejected(self):
        r = self.record(); r['mutationTrace'] = []; self.reject(r)

    def test_current_button_focus_steal_return_rejected(self):
        r = self.record()
        r['eventTrace'].append({'seq': 999, 'phase': 'settled', 'type': 'focusin', 'target': {'tag': 'button', 'isCopyBtn': True}, 'relatedTarget': None, 'observedTime': r['phases']['settled']['checkpointTime']})
        self.reject(r)

    def test_disposal_must_disable(self):
        r = self.record('pendingDispose'); r['phases']['settled']['buttonDisabled'] = False; self.reject(r)

    def test_text_not_clipped(self):
        r = self.record(); r['phases']['settled']['statusTextFits'] = False; self.reject(r)

    def test_status_geometry_stable_after_checkout(self):
        r = self.record(); r['phases']['settled']['statusHeight'] += 30; self.reject(r)

    def test_no_new_stale_timer(self):
        r = self.record(); r['timers'].append({'delay':1500, 'registeredAt':10, 'calls':0}); self.reject(r)

    def test_cancelled_deadline_must_be_observed(self):
        r = self.record('settledCheckoutReset')
        r['phases']['completed']['checkpointTime'] = r['timers'][0]['registeredAt'] + 20
        self.reject(r)

    def test_nan_timer_rejected(self):
        r = self.record('pipelinedRequest'); r['timers'][0]['firedAt'] = float('nan'); self.reject(r)

    def test_pipelined_transient_old_idle_rejected(self):
        r = self.record('pipelinedRequest')
        r['mutationTrace'].append({'seq':999, 'phase':'settled', 'targetId':'status', 'newText':r['phases']['initial']['statusText'], 'observedTime':r['phases']['settled']['checkpointTime']})
        self.reject(r)

    def test_baseline_records_pass(self):
        from clipboard_status_ownership import SCENARIOS
        for sc in SCENARIOS:
            self.assertTrue(audit_ownership_record(self.record(sc))['passed'])

    def test_trace_suffix_missing_rejected(self):
        r = self.record(); r['eventTrace'].pop(); self.reject(r)

    def test_current_node_must_replace_old(self):
        r = self.record(); r['phases']['settled']['sameInitialButton'] = True; self.reject(r)

    def test_runtime_font_matches_scale(self):
        r = self.record(); r['phases']['settled']['fontScaleVerified'] = False; self.reject(r)

    def test_transient_button_state_rejected(self):
        r = self.record()
        r['buttonTrace'].append({'phase':'settled','seq':len(r['buttonTrace'])+1,
            'observedTime':r['phases']['settled']['checkpointTime'], 'field':'text','value':'Tersalin!'})
        r['phases']['settled']['buttonSeq'] += 1
        r['phases']['completed']['buttonSeq'] += 1
        self.reject(r)


if __name__ == '__main__':
    unittest.main()
