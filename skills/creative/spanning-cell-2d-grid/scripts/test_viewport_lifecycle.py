import unittest
from viewport_lifecycle import ViewportLifecycle


class LifecycleTests(unittest.TestCase):
    def test_idle_resize_is_admitted(self):
        s = ViewportLifecycle()
        self.assertFalse(s.active)
        self.assertTrue(s.resize())

    def test_detach_cancels(self):
        s = ViewportLifecycle()
        self.assertTrue(s.start())
        s.detach()
        self.assertFalse(s.active)
        self.assertFalse(s.resize())
        self.assertFalse(s.start())

    def test_reconnect_needs_new_start(self):
        s = ViewportLifecycle()
        s.start()
        s.detach()
        s.reconnect()
        self.assertFalse(s.active)
        self.assertTrue(s.start())

    def test_dispose_is_terminal(self):
        s = ViewportLifecycle()
        s.start()
        s.dispose()
        s.reconnect()
        self.assertFalse(s.start())
        self.assertFalse(s.resize())
        self.assertFalse(s.observer_connected)

    def test_dispose_idempotent(self):
        s = ViewportLifecycle()
        s.dispose()
        before = vars(s).copy()
        s.dispose()
        self.assertEqual(before, vars(s))

    # UIUX-036 Tests: Repeated mount accounting and reentrant selection disposal
    def test_repeated_mount_listener_accounting(self):
        events = [('el', 'pointerdown'), ('el', 'pointermove'), ('el', 'pointerup'),
                  ('el', 'pointercancel'), ('el', 'lostpointercapture'),
                  ('doc', 'visibilitychange'), ('win', 'blur'), ('win', 'resize')]
        # Simulate 10 sequential mount and unmount cycles
        for cycle in range(10):
            s = ViewportLifecycle()
            for target, ev in events:
                self.assertTrue(s.attach_listener(target, ev))
            self.assertEqual(s.listener_count(), len(events))
            # Disposal must zero out all listeners without leaks
            s.dispose()
            self.assertEqual(s.listener_count(), 0)
            self.assertFalse(s.attach_listener('el', 'pointerdown'))

    def test_reentrant_selection_callback_disposal(self):
        s = ViewportLifecycle()
        self.assertTrue(s.start())
        self.assertEqual(s.pending_raf, 1)
        self.assertTrue(s.active)
        # Reentrant dispose during selection callback
        res = s.trigger_callback_and_dispose()
        self.assertTrue(res)
        self.assertTrue(s.disposed)
        self.assertFalse(s.active)
        self.assertEqual(s.pending_raf, 0)
        self.assertFalse(s.in_callback)
        # Subsequent operations reject cleanly
        self.assertFalse(s.start())
        self.assertFalse(s.resize())

    def test_pending_raf_zero_after_detach_and_dispose(self):
        s = ViewportLifecycle()
        s.start()
        self.assertEqual(s.pending_raf, 1)
        s.detach()
        self.assertEqual(s.pending_raf, 0)
        s.reconnect()
        s.start()
        self.assertEqual(s.pending_raf, 1)
        s.dispose()
        self.assertEqual(s.pending_raf, 0)

    def test_reentrant_disposal_on_inactive_or_disposed(self):
        s = ViewportLifecycle()
        self.assertFalse(s.trigger_callback_and_dispose())
        s.dispose()
        self.assertFalse(s.trigger_callback_and_dispose())

    def test_listener_partial_removal(self):
        s = ViewportLifecycle()
        s.attach_listener('el', 'pointerdown')
        s.attach_listener('el', 'pointerdown')
        self.assertEqual(s.listener_count(), 2)
        s.remove_listener('el', 'pointerdown')
        self.assertEqual(s.listener_count(), 1)
        s.remove_listener('el', 'pointerdown')
        self.assertEqual(s.listener_count(), 0)
        self.assertFalse(s.remove_listener('el', 'pointerdown'))


if __name__ == '__main__':
    unittest.main()
