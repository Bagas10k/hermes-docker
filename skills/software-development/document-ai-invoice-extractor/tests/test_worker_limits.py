"""Real isolated resource-limit probes; no limits applied to test runner."""
import pathlib
import subprocess
import sys
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / 'scripts'


class ResourceTests(unittest.TestCase):
    def probe(self, code):
        result = subprocess.run([sys.executable, '-c',
            'import sys; sys.path.insert(0, ' + repr(str(SCRIPTS)) + '); '
            'from worker_limits import apply_limits\n' + code],
            capture_output=True, text=True, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_allocation_denied(self):
        self.assertEqual(self.probe('apply_limits(address_bytes=64*1024*1024);\n'
            'try: x=bytearray(128*1024*1024)\n'
            'except MemoryError: print("denied")\n'
            'else: raise AssertionError("allocation admitted")'), 'denied')

    def test_normal_allocation(self):
        self.assertEqual(self.probe('apply_limits(); x=bytearray(1024*1024); print(len(x))'), '1048576')

    def test_file_size_denied(self):
        self.assertEqual(self.probe('import tempfile,signal; signal.signal(signal.SIGXFSZ, signal.SIG_IGN); '
            'f=tempfile.TemporaryFile(); apply_limits(file_bytes=1024);\n'
            'try: f.write(b"x"*8192); f.flush()\n'
            'except OSError as e: print(e.errno)\n'
            'else: raise AssertionError("write admitted")'), '27')

    def test_fd_limit_denied(self):
        self.assertEqual(self.probe('apply_limits(open_files=16); files=[];\n'
            'try:\n for i in range(40): files.append(open("/dev/null"))\n'
            'except OSError as e: print(e.errno)\n'
            'else: raise AssertionError("fds admitted")'), '24')

    def test_existing_ceiling_not_relaxed(self):
        self.assertEqual(self.probe('import resource; resource.setrlimit(resource.RLIMIT_NOFILE,(32,64)); '
            'apply_limits(); print(resource.getrlimit(resource.RLIMIT_NOFILE))'), '(32, 32)')

    def test_cpu_and_core_configured(self):
        self.assertEqual(self.probe('import resource; apply_limits(); '
            'print(resource.getrlimit(resource.RLIMIT_CPU),resource.getrlimit(resource.RLIMIT_CORE))'), '(45, 45) (0, 0)')

    def test_invalid_configuration(self):
        self.assertEqual(self.probe('try: apply_limits(address_bytes=True)\n'
            'except ValueError: print("rejected")'), 'rejected')


if __name__ == '__main__':
    unittest.main()
