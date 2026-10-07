import unittest
from minimap_lifecycle import MinimapLifecycle


class MinimapLifecycleTests(unittest.TestCase):
    def test_live_callback_and_minimap_only_scope(self):
        calls = []
        gate = MinimapLifecycle(lambda: calls.append("disconnect/remove"))
        self.assertTrue(gate.run(calls.append, "resize"))
        self.assertTrue(gate.dispose())
        calls.append("history remains live")
        self.assertEqual(calls, ["resize", "disconnect/remove", "history remains live"])

    def test_queued_callback_and_double_dispose(self):
        calls = []
        gate = MinimapLifecycle(lambda: calls.append("cleanup"))
        queued = lambda: gate.run(calls.append, "stale")
        self.assertTrue(gate.dispose())
        self.assertFalse(queued())
        self.assertFalse(gate.dispose())
        self.assertEqual(calls, ["cleanup"])

    def test_cleanup_reentry_is_already_closed(self):
        calls = []
        def cleanup():
            calls.extend([gate.run(lambda: self.fail("stale work")), gate.dispose()])
        gate = MinimapLifecycle(cleanup)
        self.assertTrue(gate.dispose())
        self.assertEqual(calls, [False, False])
