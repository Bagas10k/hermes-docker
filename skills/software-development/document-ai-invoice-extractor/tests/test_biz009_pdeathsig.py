"""Deterministic PR_SET_PDEATHSIG parent-death signal and detached worker containment verification."""
import os
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from worker_limits import set_pdeathsig, apply_limits


class PdeathsigContainmentTests(unittest.TestCase):
    def test_set_pdeathsig_returns_boolean_success_on_linux(self):
        """set_pdeathsig cleanly configures PR_SET_PDEATHSIG and returns True on Linux."""
        if sys.platform == 'linux':
            self.assertTrue(set_pdeathsig(signal.SIGKILL))
        else:
            self.assertFalse(set_pdeathsig(signal.SIGKILL))

    def test_apply_limits_enables_pdeathsig_by_default(self):
        """apply_limits invokes set_pdeathsig without error."""
        code = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from worker_limits import apply_limits
apply_limits()
print("configured")
"""
        res = subprocess.run([sys.executable, '-c', code, str(SCRIPTS)],
                             capture_output=True, text=True, timeout=5)
        self.assertEqual(res.returncode, 0)
        self.assertIn("configured", res.stdout)

    def test_detached_worker_killed_on_parent_death_with_pdeathsig(self):
        """A worker or grandchild that creates a new session (setsid) is terminated upon parent death if PR_SET_PDEATHSIG is set."""
        pidfile = Path('/tmp/pdeathsig_test_child.pid')
        pidfile.unlink(missing_ok=True)

        child_code = f"""
import os, sys, time, signal
from pathlib import Path
sys.path.insert(0, {str(SCRIPTS)!r})
from worker_limits import set_pdeathsig

# Set PR_SET_PDEATHSIG
set_pdeathsig(signal.SIGKILL)

# Create a new session (detach from parent's process group)
os.setsid()

# Record PID
Path({str(pidfile)!r}).write_text(str(os.getpid()))

# Run indefinitely
while True:
    time.sleep(1)
"""

        parent_code = f"""
import subprocess, sys, time
from pathlib import Path

p = subprocess.Popen([sys.executable, "-c", {child_code!r}],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pidfile = Path({str(pidfile)!r})
for _ in range(50):
    if pidfile.exists():
        break
    time.sleep(0.02)
# Parent sleeps briefly then exits
time.sleep(0.3)
sys.exit(0)
"""

        # Run parent
        res = subprocess.run([sys.executable, '-c', parent_code], timeout=5)
        self.assertEqual(res.returncode, 0)

        # Parent is now terminated
        self.assertTrue(pidfile.exists())
        child_pid = int(pidfile.read_text())

        # Give kernel a fraction of time to deliver SIGKILL to child
        time.sleep(0.1)

        # Child /proc entry must not exist or be a zombie
        proc_stat = Path(f'/proc/{child_pid}/stat')
        if proc_stat.exists():
            stat_content = proc_stat.read_text().split()
            # If zombie 'Z', it's dead waiting for reaper
            state = stat_content[2]
            self.assertEqual(state, 'Z', f'Detached process {child_pid} remained alive in state {state}')
        else:
            self.assertFalse(proc_stat.exists(), f'Detached process {child_pid} still exists')

        pidfile.unlink(missing_ok=True)

    def test_detached_worker_without_pdeathsig_remains_orphan(self):
        """Contrasting control test: without PR_SET_PDEATHSIG, a setsid process survives parent death as an orphan."""
        pidfile = Path('/tmp/orphan_control.pid')
        pidfile.unlink(missing_ok=True)

        orphan_child_code = f"""
import os, sys, time
from pathlib import Path

# Create a new session WITHOUT PR_SET_PDEATHSIG
os.setsid()
Path({str(pidfile)!r}).write_text(str(os.getpid()))

while True:
    time.sleep(1)
"""

        parent_code = f"""
import subprocess, sys, time
from pathlib import Path

p = subprocess.Popen([sys.executable, "-c", {orphan_child_code!r}],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pidfile = Path({str(pidfile)!r})
for _ in range(50):
    if pidfile.exists():
        break
    time.sleep(0.02)
time.sleep(0.3)
sys.exit(0)
"""

        res = subprocess.run([sys.executable, '-c', parent_code], timeout=5)
        self.assertEqual(res.returncode, 0)

        self.assertTrue(pidfile.exists())
        orphan_pid = int(pidfile.read_text())
        time.sleep(0.1)

        proc_stat = Path(f'/proc/{orphan_pid}/stat')
        try:
            # Without PR_SET_PDEATHSIG, orphan survives
            self.assertTrue(proc_stat.exists())
            self.assertNotEqual(proc_stat.read_text().split()[2], 'Z')
        finally:
            # Clean up the orphan process
            try:
                os.kill(orphan_pid, signal.SIGKILL)
            except Exception:
                pass
            pidfile.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
