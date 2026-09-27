
import tempfile
import shutil
import unittest
from pathlib import Path
from transactional_patch_manager import TransactionalPatchManager

class TestTransactionalPatching(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.app_file = self.test_dir / "app.py"
        self.app_file.write_text("def run():\n    return 42\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_successful_two_phase_commit(self):
        mgr = TransactionalPatchManager(str(self.test_dir))
        mgr.create_shadow_copy(["app.py"])
        
        # Apply patch in shadow
        mgr.apply_patch("app.py", lambda c: c.replace("return 42", "return 100"))
        
        # Verify in shadow
        check = mgr.verify_shadow_health('python3 -c "import app; assert app.run() == 100"')
        self.assertTrue(check["success"])
        
        # Commit to live
        c_res = mgr.commit(post_verify_cmd='python3 -c "import app; assert app.run() == 100"')
        self.assertTrue(c_res["success"])
        self.assertEqual(self.app_file.read_text(), "def run():\n    return 100\n")

    def test_failed_shadow_aborts_without_live_mutation(self):
        mgr = TransactionalPatchManager(str(self.test_dir))
        mgr.create_shadow_copy(["app.py"])
        
        # Apply buggy patch
        mgr.apply_patch("app.py", lambda c: c.replace("return 42", "return 0/0"))
        
        # Verify in shadow
        check = mgr.verify_shadow_health('python3 -c "import app; app.run()"')
        self.assertFalse(check["success"])
        
        # Rollback
        mgr.rollback()
        # Ensure live file remains completely untouched
        self.assertEqual(self.app_file.read_text(), "def run():\n    return 42\n")

    def test_live_post_verify_failure_triggers_instant_rollback(self):
        mgr = TransactionalPatchManager(str(self.test_dir))
        mgr.create_shadow_copy(["app.py"])
        mgr.apply_patch("app.py", lambda c: c.replace("return 42", "return 999"))
        
        # Health check in shadow passes
        check = mgr.verify_shadow_health('python3 -c "import app; assert app.run() == 999"')
        self.assertTrue(check["success"])
        
        # Post-verify in live fails deliberately
        c_res = mgr.commit(post_verify_cmd='python3 -c "exit(1)"')
        self.assertFalse(c_res["success"])
        self.assertTrue(c_res.get("rolled_back", False))
        # Ensure target file was restored to original
        self.assertEqual(self.app_file.read_text(), "def run():\n    return 42\n")

if __name__ == "__main__":
    unittest.main()
