"""Read-only capability probe and admission-contract tests; never loads BPF."""
import argparse
import json
import pathlib
import platform
import shutil
import unittest

GATES = ('bpf_active', 'btf', 'attached', 'scope_verified', 'policy_verified', 'canary_denied')

def admit(evidence):
    return all(evidence.get(key) is True for key in GATES)

def mac_decision(prior, enrolled, policy_present, allowed):
    if prior != 0:
        return prior
    if not enrolled:
        return 0  # Host policy scope, NOT worker admission.
    return 0 if policy_present and allowed else -1

def probe():
    try:
        lsm = pathlib.Path('/sys/kernel/security/lsm').read_text().strip().split(',')
        error = None
    except OSError as exc:
        lsm, error = [], type(exc).__name__
    evidence = {'bpf_active': 'bpf' in lsm,
                'btf': pathlib.Path('/sys/kernel/btf/vmlinux').is_file()}
    return {'kernel': platform.release(), 'active_lsms': lsm, 'read_error': error,
            'tools': {x: shutil.which(x) for x in ('clang', 'bpftool')},
            'evidence': evidence, 'admitted': admit(evidence),
            'kernel_enforcement_tested': False,
            'missing_evidence': [k for k in GATES if evidence.get(k) is not True]}

class Tests(unittest.TestCase):
    def test_complete(self):
        self.assertTrue(admit(dict.fromkeys(GATES, True)))
    def test_each_missing(self):
        for key in GATES:
            with self.subTest(key=key):
                data = dict.fromkeys(GATES, True)
                del data[key]
                self.assertFalse(admit(data))
    def test_each_false(self):
        for key in GATES:
            with self.subTest(key=key):
                data = dict.fromkeys(GATES, True)
                data[key] = False
                self.assertFalse(admit(data))
    def test_truthy_is_not_evidence(self):
        self.assertFalse(admit(dict.fromkeys(GATES, 'true')))
    def test_preserve_prior(self):
        self.assertEqual(mac_decision(-13, True, True, True), -13)
    def test_enrolled_missing_policy(self):
        self.assertEqual(mac_decision(0, True, False, True), -1)
    def test_explicit_deny(self):
        self.assertEqual(mac_decision(0, True, True, False), -1)
    def test_explicit_allow(self):
        self.assertEqual(mac_decision(0, True, True, True), 0)
    def test_host_scope_not_admission(self):
        self.assertEqual(mac_decision(0, False, False, False), 0)
        self.assertFalse(admit({}))
    def test_detach_revokes_admission(self):
        data = dict.fromkeys(GATES, True)
        data['attached'] = False
        self.assertFalse(admit(data))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    if args.test:
        unittest.main(argv=['admission_probe'], verbosity=2)
    else:
        print(json.dumps(probe(), indent=2))
        raise SystemExit(2)
