"""Linux per-process ceilings and parent-death lifecycle containment."""
import ctypes
import os
import resource
import signal
import sys

ADDRESS_BYTES = 1024 * 1024 * 1024
CPU_SECONDS = 45
FILE_BYTES = 32 * 1024 * 1024
OPEN_FILES = 128
PR_SET_PDEATHSIG = 1


def set_pdeathsig(sig=signal.SIGKILL):
    """Request delivery of a signal to this process when its parent dies.

    Uses Linux prctl(PR_SET_PDEATHSIG).
    Returns True if successfully configured, False on non-Linux or error.
    """
    if sys.platform != 'linux':
        return False
    try:
        libc = ctypes.CDLL(None)
        if not hasattr(libc, 'prctl'):
            return False
        return libc.prctl(PR_SET_PDEATHSIG, int(sig), 0, 0, 0) == 0
    except Exception:
        return False


def apply_limits(address_bytes=ADDRESS_BYTES, cpu_seconds=CPU_SECONDS,
                 file_bytes=FILE_BYTES, open_files=OPEN_FILES,
                 enable_pdeathsig=True):
    limits = ((resource.RLIMIT_AS, address_bytes),
              (resource.RLIMIT_CPU, cpu_seconds),
              (resource.RLIMIT_FSIZE, file_bytes),
              (resource.RLIMIT_NOFILE, open_files),
              (resource.RLIMIT_CORE, 0))
    for _, value in limits:
        if type(value) is not int or value < 0:
            raise ValueError('limits must be nonnegative integers')
    for kind, requested in limits:
        soft, hard = resource.getrlimit(kind)
        candidates = [requested] + [n for n in (soft, hard) if n != resource.RLIM_INFINITY]
        ceiling = min(candidates)
        resource.setrlimit(kind, (ceiling, ceiling))
    if enable_pdeathsig:
        set_pdeathsig(signal.SIGKILL)


if __name__ == '__main__':
    try:
        apply_limits()
        import runpy
        runpy.run_path(sys.argv.pop(1), run_name='__invoice_worker__')
    except Exception as exc:
        print(f'error: {type(exc).__name__}: worker resource/execution failure', file=sys.stderr)
        raise SystemExit(1)
