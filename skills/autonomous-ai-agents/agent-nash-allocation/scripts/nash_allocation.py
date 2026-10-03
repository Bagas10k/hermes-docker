"""Finite singleton congestion game; no auction or truthfulness claim.

At a frozen epoch t, u_i(a)=R_a(t)/n_a-c_ia and
Phi(a)=sum_r R_r(t)*H(n_r)-sum_i c_i,a_i is an exact potential.
"""
import math
from collections import deque
from dataclasses import dataclass

MAX_VALUE = 1e100
MAX_SIZE = 1024


def _number(value):
    if type(value) not in (int, float) or not 0 <= value <= MAX_VALUE:
        raise ValueError('expected finite nonnegative number <= 1e100')
    return float(value)


def _sequence(value, limit=MAX_SIZE):
    if not isinstance(value, (list, tuple)) or len(value) > limit:
        raise ValueError('expected bounded list or tuple')
    return tuple(value)


@dataclass(frozen=True)
class SolveResult:
    actions: tuple
    updates: int
    max_regret: float
    converged: bool
    potential: float
    epoch: float


@dataclass(frozen=True, init=False)
class Game:
    rewards: tuple
    costs: tuple
    epoch: float

    def __init__(self, rewards, decays, costs, epoch=0):
        rewards, decays, costs = map(_sequence, (rewards, decays, costs))
        if not rewards or len(rewards) != len(decays):
            raise ValueError('require matching nonempty resources and decays')
        rewards = tuple(map(_number, rewards))
        decays = tuple(map(_number, decays))
        costs = tuple(tuple(map(_number, _sequence(row))) for row in costs)
        if any(len(row) != len(rewards) for row in costs):
            raise ValueError('cost matrix must have one column per resource')
        epoch = _number(epoch)
        object.__setattr__(self, 'epoch', epoch)
        object.__setattr__(self, 'rewards', tuple(r * math.exp(-d * epoch)
                                               for r, d in zip(rewards, decays)))
        object.__setattr__(self, 'costs', tuple(tuple(row) for row in costs))

    def _actions(self, actions):
        actions = _sequence(actions)
        if len(actions) != len(self.costs) or any(
                type(r) is not int or not 0 <= r < len(self.rewards) for r in actions):
            raise ValueError('one valid integer resource per agent required')
        return actions

    def payoffs(self, actions):
        actions = self._actions(actions)
        counts = [actions.count(r) for r in range(len(self.rewards))]
        return tuple(self.rewards[r] / counts[r] - self.costs[i][r]
                     for i, r in enumerate(actions))

    def max_regret(self, actions):
        """Independent complete unilateral-deviation certificate (float arithmetic)."""
        actions = self._actions(actions)
        current = self.payoffs(actions)
        counts = [actions.count(r) for r in range(len(self.rewards))]
        return max((self.rewards[r] / (counts[r] + (r != actions[i]))
                    - self.costs[i][r] - current[i]
                    for i in range(len(actions)) for r in range(len(self.rewards))), default=0.0)

    def solve(self, actions=None, max_updates=10000, tolerance=1e-12):
        """Cyclic agent order; smallest resource index breaks improving ties.

        Epoch/rewards never change. Only strict payoff gains move an agent.
        Update cap does not imply equilibrium: certify final regret separately.
        """
        if type(max_updates) is not int or not 0 <= max_updates <= 1000000:
            raise ValueError('max_updates must be an integer in [0, 1000000]')
        tolerance = _number(tolerance)
        actions = list(self._actions((0,) * len(self.costs) if actions is None else actions))
        counts = [actions.count(r) for r in range(len(self.rewards))]
        updates = 0
        while updates < max_updates:
            changed = False
            for i, old in enumerate(actions):
                values = [self.rewards[r] / (counts[r] + (r != old)) - self.costs[i][r]
                          for r in range(len(self.rewards))]
                best = max(range(len(values)), key=values.__getitem__)
                if values[best] > values[old]:
                    counts[old] -= 1
                    counts[best] += 1
                    actions[i] = best
                    updates += 1
                    changed = True
                    if updates >= max_updates:
                        break
            if not changed:
                break
        actions = tuple(actions)
        regret = self.max_regret(actions)
        return SolveResult(actions, updates, regret, regret <= tolerance,
                           self.potential(actions), self.epoch)

    def potential(self, actions):
        actions = self._actions(actions)
        return math.fsum(self.rewards[r] * math.fsum(1 / j for j in range(1, actions.count(r) + 1))
                         for r in range(len(self.rewards))) - math.fsum(
                             self.costs[i][r] for i, r in enumerate(actions))


class ReserveScheduler:
    """Separate FIFO reserve, not an auction policy.

    Admitted rank q (one-based) waits at most K*q ticks with persistent
    consecutive ticks and one completed quantum per dequeued job.
    Arrivals join the tail; non-reserved ticks return None for caller auctions.
    """

    def __init__(self, k, capacity=1024):
        for value in (k, capacity):
            if type(value) is not int or not 1 <= value <= 1000000:
                raise ValueError('k and capacity must be integers in [1, 1000000]')
        self._k = k
        self._capacity = capacity
        self._queue = deque()
        self._members = set()
        self._next_tick = 0

    @property
    def waiting(self):
        return tuple(self._queue)

    def admit(self, job_id):
        """Return admitted, duplicate, or full; never evict an admitted job.

        Deduplication covers waiting IDs only; served IDs may be readmitted.
        """
        if not isinstance(job_id, str) or not 1 <= len(job_id) <= 256:
            raise ValueError('job ID must be a nonempty string of at most 256 characters')
        if job_id in self._members:
            return 'duplicate'
        if len(self._queue) >= self._capacity:
            return 'full'
        self._queue.append(job_id)
        self._members.add(job_id)
        return 'admitted'

    def tick(self, tick):
        """Require consecutive integer ticks starting at zero; reject replay/skips."""
        if type(tick) is not int or tick != self._next_tick:
            raise ValueError('ticks must be consecutive integers starting at zero')
        self._next_tick += 1
        if tick % self._k == 0 and self._queue:
            job = self._queue.popleft()
            self._members.remove(job)
            return job
        return None


def main():
    """Print deterministic standalone demonstration; no external state changes."""
    import argparse
    import json
    from dataclasses import asdict
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true', help='run deterministic JSON demo (default)')
    parser.parse_args()
    game = Game([12, 8], [0.2, 0.1], [[1, 0], [0, 1], [0.5, 0.5]], epoch=2)
    reserve = ReserveScheduler(3, capacity=8)
    reserve.admit('oldest')
    reserve.admit('next')
    print(json.dumps({'solution': asdict(game.solve()),
                      'rewards': game.rewards,
                      'reserve': [reserve.tick(t) for t in range(7)]},
                     allow_nan=False, sort_keys=True))


if __name__ == '__main__':
    main()

