"""Test-only handshake worker; parent kills only this isolated subprocess."""
import sys
import history_file
from byte_budget_history import ByteBudgetHistory
from history_recovery import guarded_save


def main():
    path, boundary = sys.argv[1:]
    real_sync, real_replace = history_file.os.fsync, history_file.os.replace
    def pause():
        print('READY', flush=True)
        sys.stdin.readline()
    def sync(fd):
        if boundary == 'before_sync':
            pause()
        return real_sync(fd)
    def replace(src, dst):
        if boundary == 'before_replace':
            pause()
        result = real_replace(src, dst)
        if boundary == 'after_replace':
            pause()
        return result
    history_file.os.fsync = sync
    history_file.os.replace = replace
    guarded_save(ByteBudgetHistory({'A': 'new'}), path)


if __name__ == '__main__':
    main()
