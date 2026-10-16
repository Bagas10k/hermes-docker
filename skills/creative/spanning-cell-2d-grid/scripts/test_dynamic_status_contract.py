"""Parent acceptance regressions: never pass absent geometry or clipped text."""
import copy
import unittest
from pathlib import Path
from clipboard_dynamic_status import audit_dynamic_status_record
from test_clipboard_dynamic_status import make_dynamic


class DynamicStatusContract(unittest.TestCase):
    def rejected(self, r):
        try:
            self.assertFalse(audit_dynamic_status_record(r)['passed'])
        except (ValueError, KeyError, TypeError):
            pass

    def test_missing_status_widths_fail_closed(self):
        r = make_dynamic()
        for p in r['phases'].values():
            p.pop('statusScrollWidth')
            p.pop('statusClientWidth')
        self.rejected(r)

    def test_zero_width_status_rejected(self):
        r = make_dynamic()
        for p in r['phases'].values():
            p.update(statusScrollWidth=0, statusClientWidth=0)
        self.rejected(r)

    def test_short_status_cannot_impersonate_dynamic_fixture(self):
        r = make_dynamic()
        for name in ('initial', 'reset'):
            r['phases'][name]['statusText'] = 'Versi short. 0 cabang lanjutan.'
            r['phases'][name]['measurement']['statusText'] = r['phases'][name]['statusText']
        self.rejected(r)

    def test_measurement_and_phase_status_must_match(self):
        r = make_dynamic()
        r['phases']['pending']['statusText'] = 'incorrect snapshot'
        self.rejected(r)

    def test_breadcrumb_must_not_clip_labels(self):
        from dynamic_status_fixture import fixture
        css = fixture()['html'].split('</style>', 1)[0]
        rule = css.split('.dag-breadcrumb-item{', 1)[1].split('}', 1)[0]
        self.assertNotIn('overflow:hidden', rule)
        self.assertNotIn('text-overflow:ellipsis', rule)

    def test_clipped_text_is_rejected(self):
        for field in ('statusTextFits', 'breadcrumbTextFits'):
            r = make_dynamic()
            r['phases']['reset'][field] = False
            self.rejected(r)

    def test_stale_reservation_is_rejected(self):
        r = make_dynamic()
        r['phases']['pending']['reservationText'] = 'Versi stale.'
        self.rejected(r)

    def test_dynamic_target_requires_exact_breadcrumb(self):
        r = make_dynamic(departure='backward')
        r['phases']['reset']['activeTarget']['dataBreadcrumbNode'] = 'anak-雪'
        self.rejected(r)


if __name__ == '__main__':
    unittest.main()
