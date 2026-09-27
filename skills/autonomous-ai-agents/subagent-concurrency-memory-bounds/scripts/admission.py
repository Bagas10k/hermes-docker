"""Trusted in-process reservation planner; no process/kernel operations."""
from collections import deque
from dataclasses import dataclass
from threading import RLock
import re

POLICY_CAP = 9_000_000_000


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('integer outside policy range')
    return value


@dataclass(frozen=True)
class Ticket:
    serial: int
    worker: str
    reservation: int


class Ledger:
    def __init__(self, *, budget, overhead, safety, concurrency, backlog):
        integer(budget, 1, POLICY_CAP)
        integer(overhead, 0, budget)
        integer(safety, 0, budget)
        integer(concurrency, 1, 1024)
        integer(backlog, 1, 10000)
        if overhead + safety >= budget:
            raise ValueError('no worker capacity')
        self.capacity = budget - overhead - safety
        self.target = concurrency
        self.backlog = backlog
        self._queue = deque()
        self._active = {}
        self._serial = 0
        self._lock = RLock()
        self._closed = False
        self._stopping = set()
        self._maximum = concurrency

    def submit(self, worker, reservation):
        with self._lock:
            if self._closed:
                raise ValueError('intake closed')
            if type(worker) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', worker):
                raise ValueError('invalid literal worker ID')
            integer(reservation, 1, self.capacity)
            if len(self._queue) >= self.backlog:
                raise ValueError('backpressure: backlog full')
            if any(w == worker for w, _ in self._queue) or any(t.worker == worker for t in self._active.values()):
                raise ValueError('duplicate live ID')
            self._queue.append((worker, reservation))

    def dispatch(self):
        with self._lock:
            tickets = []
            while self._queue and len(self._active) < self.target:
                worker, reservation = self._queue[0]
                if sum(t.reservation for t in self._active.values()) + reservation > self.capacity:
                    break
                self._queue.popleft()
                self._serial += 1
                ticket = Ticket(self._serial, worker, reservation)
                self._active[ticket.serial] = ticket
                tickets.append(ticket)
            return tickets

    def set_target(self, target):
        with self._lock:
            integer(target, 0, self._maximum)
            self.target = target

    def _ticket(self, ticket):
        if not isinstance(ticket, Ticket) or self._active.get(ticket.serial) is not ticket:
            raise ValueError('unknown or stale ticket')

    def mark_stopping(self, ticket):
        with self._lock:
            self._ticket(ticket)
            self._stopping.add(ticket.serial)

    def release(self, ticket, *, reaped, empty):
        with self._lock:
            self._ticket(ticket)
            if type(reaped) is not bool or type(empty) is not bool:
                raise ValueError('exit evidence must be boolean')
            if reaped is not True or empty is not True:
                return False
            del self._active[ticket.serial]
            self._stopping.discard(ticket.serial)
            return True

    def shutdown(self):
        with self._lock:
            self._closed = True
            self._queue.clear()
            self._stopping.update(self._active)
            return list(self._active.values())

    def snapshot(self):
        with self._lock:
            return {'reserved': sum(t.reservation for t in self._active.values()),
                    'active': len(self._active), 'queued': len(self._queue)}


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true', required=True)
    parser.add_argument('--budget', type=int, default=100)
    args = parser.parse_args()
    try:
        ledger = Ledger(budget=args.budget, overhead=10, safety=10, concurrency=2, backlog=2)
        ledger.submit('a', 30)
        ledger.submit('b', 30)
        tickets = ledger.dispatch()
        before = ledger.snapshot()
        ledger.shutdown()
        for ticket in tickets:
            ledger.release(ticket, reaped=True, empty=True)
        print(json.dumps({'model_only': True, 'exit_evidence': 'synthetic', 'before': before, 'after': ledger.snapshot()}))
        return 0
    except ValueError as exc:
        print(json.dumps({'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
