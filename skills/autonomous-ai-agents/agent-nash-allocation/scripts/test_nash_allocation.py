"""Deterministic executable specification for GAME-002."""
import importlib.util
import math
import unittest


class GameTests(unittest.TestCase):
    def test_frozen_rewards_payoffs_and_exact_potential(self):
        self.assertIsNotNone(importlib.util.find_spec('nash_allocation'),
                             'game implementation is missing')
        from nash_allocation import Game
        rewards, costs = [12, 8], [[1, 2], [3, 4]]
        game = Game(rewards, [math.log(2), 0], costs, epoch=1)
        rewards[0] = 999
        costs[0][0] = 999
        self.assertAlmostEqual(game.rewards[0], 6)
        self.assertEqual(game.payoffs((0, 0)), (2, 0))
        self.assertAlmostEqual(game.potential((0, 0)), 5)
        before, after = (0, 0), (1, 0)
        self.assertAlmostEqual(game.potential(after) - game.potential(before),
                               game.payoffs(after)[0] - game.payoffs(before)[0])

    def test_bounded_validation_and_underflow(self):
        from nash_allocation import Game
        for bad in (float('nan'), float('inf'), -float('inf'), -1, 1e101, True):
            for args in (([bad], [0], [[0]], 0), ([1], [bad], [[0]], 0),
                         ([1], [0], [[bad]], 0), ([1], [0], [[0]], bad)):
                with self.subTest(args=args), self.assertRaises(ValueError):
                    Game(*args)
        for args in (([], [], []), ([1], [], []), ([1], [0], [[]]),
                     ([1]*1025, [0]*1025, []), ([1], [0], [[0]]*1025)):
            with self.assertRaises(ValueError):
                Game(*args)
        game = Game([1e100], [1e100], [[0]], 1e100)
        self.assertEqual(game.rewards, (0,))
        for actions in ((), (0, 0), (-1,), (1,), (True,), (0.0,)):
            for method in (game.payoffs, game.potential):
                with self.assertRaises(ValueError):
                    method(actions)
        empty = Game([1], [0], [])
        self.assertEqual(empty.payoffs(()), ())
        self.assertEqual(empty.potential(()), 0)

    def test_exhaustive_regret_and_sequential_equilibria(self):
        import itertools
        from nash_allocation import Game
        self.assertTrue(hasattr(Game, 'solve'), 'bounded solver missing')
        for n in range(4):
            for rewards in itertools.product((0, 2, 5), repeat=2):
                costs = [[i % 2, (i+1) % 2] for i in range(n)]
                game = Game(rewards, [0.1, 0.3], costs, epoch=2)
                for actions in itertools.product(range(2), repeat=n):
                    gains = [0.0]
                    for i in range(n):
                        for r in range(2):
                            moved = list(actions)
                            moved[i] = r
                            gain = game.payoffs(moved)[i] - game.payoffs(actions)[i]
                            gains.append(gain)
                            self.assertAlmostEqual(game.potential(moved)-game.potential(actions), gain)
                    self.assertAlmostEqual(game.max_regret(actions), max(gains))
                    result = game.solve(actions, max_updates=100, tolerance=1e-12)
                    self.assertTrue(result.converged)
                    self.assertLessEqual(game.max_regret(result.actions), 1e-12)
                    self.assertEqual(result, game.solve(actions, max_updates=100, tolerance=1e-12))
        game = Game([6, 6], [0, 0], [[0, 0]]*3)
        self.assertEqual(game.solve((0, 0, 0)).actions, (1, 0, 0))
        tied = Game([2, 2], [0, 0], [[0, 0]])
        self.assertEqual(tied.solve((1,)).updates, 0)

    def test_caps_certificates_epoch_and_invalid_solver_config(self):
        from nash_allocation import Game
        game = Game([0, 12], [0, 0], [[0, 0]]*3)
        for cap in (0, 1, 2):
            result = game.solve((0, 0, 0), max_updates=cap, tolerance=0)
            self.assertEqual(result.updates, cap)
            self.assertFalse(result.converged)
            self.assertGreater(result.max_regret, 0)
        self.assertTrue(game.solve(max_updates=3).converged)
        self.assertTrue(game.solve(max_updates=0, tolerance=12).converged)
        self.assertTrue(Game([1], [0], []).solve(max_updates=0).converged)
        early = Game([10, 2], [1, 0], [[0, 0]], epoch=0)
        late = Game([10, 2], [1, 0], [[0, 0]], epoch=10)
        self.assertEqual(early.solve().actions, (0,))
        self.assertEqual(late.solve().actions, (1,))
        self.assertEqual(early.solve().epoch, 0)
        for bad in (-1, 0.5, True, float('nan'), float('inf'), 1000001):
            with self.assertRaises(ValueError):
                game.solve(max_updates=bad)
        for bad in (-1, True, float('nan'), float('inf'), 1e101):
            with self.assertRaises(ValueError):
                game.solve(tolerance=bad)
        for method in (game.solve, game.max_regret):
            with self.assertRaises(ValueError):
                method((0,))


class ReserveTests(unittest.TestCase):
    def test_fifo_bound_under_continuous_arrivals(self):
        import nash_allocation as module
        self.assertTrue(hasattr(module, 'ReserveScheduler'), 'reserve scheduler missing')
        for k in (1, 2, 7):
            scheduler = module.ReserveScheduler(k, capacity=32)
            self.assertEqual(scheduler.admit('zero'), 'admitted')
            self.assertEqual(scheduler.tick(0), 'zero')
            originals = ['old-' + str(i) for i in range(5)]
            for job in originals:
                scheduler.admit(job)
            served = {}
            for tick in range(1, k * 5 + 1):
                scheduler.admit('high-' + str(tick))
                job = scheduler.tick(tick)
                if tick % k:
                    self.assertIsNone(job)
                elif job is not None:
                    served[job] = tick
            for rank, job in enumerate(originals, 1):
                self.assertLessEqual(served[job], k * rank)

    def test_dedup_full_and_tick_validation(self):
        from nash_allocation import ReserveScheduler
        s = ReserveScheduler(2, capacity=2)
        self.assertEqual(s.admit('a'), 'admitted')
        self.assertEqual(s.admit('b'), 'admitted')
        self.assertEqual(s.admit('a'), 'duplicate')
        self.assertEqual(s.admit('c'), 'full')
        self.assertEqual(s.waiting, ('a', 'b'))
        self.assertEqual(s.tick(0), 'a')
        self.assertEqual(s.admit('a'), 'admitted')
        self.assertIsNone(s.tick(1))
        self.assertEqual(s.tick(2), 'b')
        for tick in (2, 1, 4, -1, True, 3.0, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                s.tick(tick)
        self.assertIsNone(s.tick(3))
        self.assertEqual(s.tick(4), 'a')
        self.assertIsNone(s.tick(5))
        self.assertIsNone(s.tick(6))
        for bad in (0, -1, True, 1.5, float('nan'), float('inf'), 1000001):
            with self.assertRaises(ValueError):
                ReserveScheduler(bad)
            with self.assertRaises(ValueError):
                ReserveScheduler(1, capacity=bad)
        for bad in ('', 'x'*257, None, 1, []):
            with self.assertRaises(ValueError):
                s.admit(bad)


class DemoTests(unittest.TestCase):
    def test_cli_json_demo(self):
        import json
        import pathlib
        import subprocess
        import sys
        proc = subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name('nash_allocation.py')), '--demo'],
                              text=True, capture_output=True, check=True)
        self.assertTrue(proc.stdout.strip(), 'CLI demo missing')
        data = json.loads(proc.stdout)
        self.assertTrue(data['solution']['converged'])
        self.assertLessEqual(data['solution']['max_regret'], 1e-12)
        self.assertEqual(data['reserve'], ['oldest', None, None, 'next', None, None, None])
        self.assertEqual(proc.stderr, '')


if __name__ == '__main__':
    unittest.main()
