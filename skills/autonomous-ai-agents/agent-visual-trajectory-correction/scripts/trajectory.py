"""Bounded offline decision gate, not an input driver. SPDX-License-Identifier: MIT."""
from dataclasses import dataclass
import math


def number(x):
    return type(x) in (int, float) and math.isfinite(x) and 0 <= x <= 1e12


def token(x):
    return type(x) is str and 0 < len(x) <= 128


@dataclass(frozen=True, slots=True)
class Observation:
    action: str
    context: str
    target: str
    predicate: str
    attempt: int
    seq: int
    captured: float
    outcome: str = 'unknown'  # unknown, pending, absent, complete
    semantic: object = None  # strictly bool or None
    authoritative: bool = False
    visual_changed: bool = False  # deliberately never a success criterion


class Tracker:
    """Single owner, one possibly sent action. Caller must not mutate state.

    RETRY consumes/reserves an attempt immediately. It is not dispatch permission.
    Deadline and max_checks span all attempts. Terminal results are absorbing.
    """
    __slots__ = ('identity', 'idempotent', 'deadline', 'max_age', 'max_attempts',
                 'max_checks', 'checks', 'attempt', 'floor', 'last_seq',
                 'last_capture', 'last_now', 'terminal', 'unresolved')

    def __init__(self, action, context, target, predicate, *, start,
                 idempotent=False, timeout=30, max_age=2,
                 max_attempts=2, max_checks=16):
        if not all(token(x) for x in (action, context, target, predicate)):
            raise ValueError('identity must contain bounded nonempty tokens')
        if type(idempotent) is not bool:
            raise ValueError('idempotent must be explicit bool')
        if not all(number(x) for x in (start, timeout, max_age)) or timeout <= 0 or max_age <= 0 or start + timeout > 1e12:
            raise ValueError('finite monotonic times required')
        if type(max_attempts) is not int or not 1 <= max_attempts <= 8:
            raise ValueError('attempt cap 1..8')
        if type(max_checks) is not int or not 1 <= max_checks <= 1024:
            raise ValueError('check cap 1..1024')
        self.identity = (action, context, target, predicate)
        self.idempotent, self.deadline, self.max_age = idempotent, start + timeout, max_age
        self.max_attempts, self.max_checks = max_attempts, max_checks
        self.checks, self.attempt, self.floor = 0, 1, start
        self.last_seq, self.last_capture, self.last_now = -1, start, start
        self.terminal, self.unresolved = None, True

    def _stop(self):
        self.terminal = 'STOP_RECONCILE' if self.unresolved else 'STOP'
        return self.terminal

    def step(self, obs=None, *, now):
        if self.terminal:
            return self.terminal
        if not number(now) or now < self.last_now:
            return self._stop()
        self.last_now = now
        if now >= self.deadline or self.checks >= self.max_checks:
            return self._stop()
        self.checks += 1
        if obs is None:
            return 'RECONCILE'
        if type(obs) is not Observation:
            return self._stop()
        if (not all(token(x) for x in (obs.action, obs.context, obs.target, obs.predicate))
            or type(obs.attempt) is not int or not 1 <= obs.attempt <= 8
            or type(obs.seq) is not int or not 0 <= obs.seq <= 2**63 - 1
            or not number(obs.captured) or type(obs.outcome) is not str
            or obs.outcome not in ('unknown', 'pending', 'absent', 'complete')
            or (obs.semantic is not None and type(obs.semantic) is not bool)
            or type(obs.authoritative) is not bool or type(obs.visual_changed) is not bool):
            return self._stop()
        if (obs.action, obs.context, obs.target, obs.predicate) != self.identity or obs.attempt != self.attempt:
            return 'RECONCILE'
        if (obs.captured <= self.floor or obs.captured > now
            or now - obs.captured > self.max_age or obs.seq <= self.last_seq
            or obs.captured <= self.last_capture):
            return 'RECONCILE'
        self.last_seq, self.last_capture = obs.seq, obs.captured
        if not obs.authoritative:
            return 'RECONCILE'
        if obs.outcome == 'complete' and obs.semantic is True:
            self.unresolved = False
            self.terminal = 'SUCCESS'
            return self.terminal
        if obs.outcome == 'absent' and obs.semantic is False:
            self.unresolved = False
            if not self.idempotent or self.attempt >= self.max_attempts or self.checks >= self.max_checks:
                return self._stop()
            self.attempt += 1
            self.floor = now
            self.unresolved = True  # reservation may be dispatched by caller
            return 'RETRY'
        self.unresolved = True
        return 'OBSERVE' if obs.outcome == 'pending' and obs.semantic is not True else 'RECONCILE'
