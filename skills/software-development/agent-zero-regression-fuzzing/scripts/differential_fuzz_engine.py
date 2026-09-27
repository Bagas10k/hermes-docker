#!/usr/bin/env python3
"""
Zero-Regression Differential Fuzzing & Invariant Verification Gate Engine
Author: Bagas Cihuy & Hermes Agent
License: MIT

Provides:
1. Property-based generator for edge inputs (boundary ints, nested structures, malformed types, nulls, long strings).
2. Differential execution harness: compares f_old(x) vs f_new(x) across generated corpus.
3. Invariant verification engine: evaluates post-condition invariants (e.g. non-null, monotonic, bounded latency, type safety).
4. Regression classification: differentiates intended semantic change vs unintended behavioral drift.
"""

import sys
import time
import math
import json
import inspect
import traceback
import random
from typing import Callable, Any, List, Dict, Tuple, Optional

class DifferentialFuzzEngine:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def generate_primitive_corpus(self) -> List[Any]:
        """Generates standard boundary edge cases for fuzzing."""
        return [
            0, 1, -1, 2**31 - 1, -2**31, 2**63 - 1, -2**63,
            0.0, -0.0, 1e-9, -1e-9, float('inf'), float('-inf'), float('nan'),
            "", " ", "\n", "\t", "\x00", "A" * 1024, "✨", "<script>", "'; DROP TABLE--",
            True, False, None,
            [], [0], [None], [[]], list(range(100)),
            {}, {"": None}, {"k": "v"}, {"a": [1, 2, 3]},
            (), (1,),
            set(), {0, 1}
        ]

    def generate_typed_inputs(self, sig: inspect.Signature, count: int = 50) -> List[Tuple[Any, ...]]:
        """Synthesizes parameter tuples matching function signature with boundary mutations."""
        params = list(sig.parameters.values())
        corpus = []

        # 1. Base default values if available
        base_args = []
        for p in params:
            if p.default is not inspect.Parameter.empty:
                base_args.append(p.default)
            else:
                base_args.append(0)
        corpus.append(tuple(base_args))

        primitives = self.generate_primitive_corpus()

        # 2. Targeted perturbations
        for _ in range(count):
            row = []
            for p in params:
                annotation = p.annotation
                if annotation == int:
                    pool = [0, 1, -1, 10, 100, -50, 2**16, -2**16]
                    val = self.rng.choice(pool)
                elif annotation == float:
                    pool = [0.0, -1.0, 1.0, 3.14159, 1e-5, 1e6]
                    val = self.rng.choice(pool)
                elif annotation == str:
                    pool = ["", "test", "alpha_beta", "path/to/file", "null", "NaN", "   "]
                    val = self.rng.choice(pool)
                elif annotation == list or annotation == List:
                    pool = [[], [1], [1, 2, 3], [-1, 0, 1]]
                    val = self.rng.choice(pool)
                elif annotation == dict or annotation == Dict:
                    pool = [{}, {"key": "val"}, {"count": 1}]
                    val = self.rng.choice(pool)
                elif annotation == bool:
                    val = self.rng.choice([True, False])
                else:
                    val = self.rng.choice(primitives[:20])
                row.append(val)
            corpus.append(tuple(row))

        return corpus

    def run_differential(
        self,
        f_old: Callable,
        f_new: Callable,
        corpus: List[Tuple[Any, ...]],
        target_invariant: Optional[Callable[[Any, Any], bool]] = None,
        expected_patch_scope: Optional[Callable[[Tuple[Any, ...]], bool]] = None
    ) -> Dict[str, Any]:
        """
        Executes f_old and f_new against corpus.
        expected_patch_scope: filter function returning True for inputs where behavior IS INTENDED to differ (e.g. bug fix input).
        target_invariant: post-condition invariant g(input, output_new) -> bool that must hold for 100% of inputs.
        """
        results = {
            "total_tested": len(corpus),
            "identical_outputs": 0,
            "intentional_divergences": 0,
            "regressions": [],
            "invariant_violations": [],
            "performance_delta": {
                "old_total_ns": 0,
                "new_total_ns": 0,
                "speedup_ratio": 1.0
            },
            "status": "PASS"
        }

        for args in corpus:
            # Run old
            old_err = None
            old_res = None
            t0 = time.perf_counter_ns()
            try:
                old_res = f_old(*args)
            except Exception as e:
                old_err = type(e).__name__
            t1 = time.perf_counter_ns()
            results["performance_delta"]["old_total_ns"] += (t1 - t0)

            # Run new
            new_err = None
            new_res = None
            t2 = time.perf_counter_ns()
            try:
                new_res = f_new(*args)
            except Exception as e:
                new_err = type(e).__name__
            t3 = time.perf_counter_ns()
            results["performance_delta"]["new_total_ns"] += (t3 - t2)

            # Check invariant on new
            if target_invariant is not None:
                try:
                    inv_passed = target_invariant(args, (new_res, new_err))
                    if not inv_passed:
                        results["invariant_violations"].append({
                            "input": repr(args),
                            "new_output": repr(new_res),
                            "new_error": new_err,
                            "reason": "Target invariant violation"
                        })
                except Exception as ie:
                    results["invariant_violations"].append({
                        "input": repr(args),
                        "new_output": repr(new_res),
                        "new_error": new_err,
                        "reason": f"Invariant check crashed: {type(ie).__name__}: {ie}"
                    })

            # Compare outputs
            same_outcome = False
            if old_err is not None and new_err is not None:
                same_outcome = (old_err == new_err)
            elif old_err is None and new_err is None:
                if isinstance(old_res, float) and isinstance(new_res, float):
                    if math.isnan(old_res) and math.isnan(new_res):
                        same_outcome = True
                    else:
                        same_outcome = math.isclose(old_res, new_res, rel_tol=1e-7, abs_tol=1e-9)
                else:
                    same_outcome = (old_res == new_res)

            if same_outcome:
                results["identical_outputs"] += 1
            else:
                is_intended = False
                if expected_patch_scope is not None:
                    try:
                        is_intended = expected_patch_scope(args)
                    except Exception:
                        is_intended = False

                if is_intended:
                    results["intentional_divergences"] += 1
                else:
                    results["regressions"].append({
                        "input": repr(args),
                        "old_output": repr(old_res),
                        "old_error": old_err,
                        "new_output": repr(new_res),
                        "new_error": new_err
                    })

        old_ns = max(1, results["performance_delta"]["old_total_ns"])
        new_ns = max(1, results["performance_delta"]["new_total_ns"])
        results["performance_delta"]["speedup_ratio"] = round(old_ns / new_ns, 3)

        if results["regressions"] or results["invariant_violations"]:
            results["status"] = "FAIL"

        return results

def run_self_test():
    """Unit tests for the Zero-Regression Differential Fuzzing Engine."""
    engine = DifferentialFuzzEngine(seed=1337)
    test_results = []

    # Test 1: Identical functions should have 0 regressions and PASS
    def old_calc(x: int, y: int) -> int:
        return x + y

    def new_calc(x: int, y: int) -> int:
        return x + y

    sig = inspect.signature(old_calc)
    corpus = engine.generate_typed_inputs(sig, count=40)
    res1 = engine.run_differential(old_calc, new_calc, corpus)
    assert res1["status"] == "PASS"
    assert len(res1["regressions"]) == 0
    test_results.append("Test 1 (Identical function equivalence): PASSED")

    # Test 2: Unintended regression detected (FAIL)
    def broken_calc(x: int, y: int) -> int:
        if x == 10:
            return -999  # regression
        return x + y

    res2 = engine.run_differential(old_calc, broken_calc, corpus)
    assert res2["status"] == "FAIL"
    assert len(res2["regressions"]) > 0
    test_results.append(f"Test 2 (Unintended regression caught: {len(res2['regressions'])} cases): PASSED")

    # Test 3: Intentional bug fix with expected_patch_scope (PASS)
    def old_div(x: int, y: int) -> float:
        return x / y  # crashes on y=0

    def new_div(x: int, y: int) -> float:
        if y == 0:
            return 0.0
        return x / y

    div_corpus = [(10, 2), (20, 5), (5, 0), (0, 0), (100, 10)]
    # Scope where behavior divergence is intended: y == 0
    scope = lambda args: args[1] == 0
    # Invariant: never raise ZeroDivisionError
    inv = lambda args, outcome: outcome[1] != "ZeroDivisionError"

    res3 = engine.run_differential(old_div, new_div, div_corpus, target_invariant=inv, expected_patch_scope=scope)
    assert res3["status"] == "PASS"
    assert res3["intentional_divergences"] == 2  # (5, 0) and (0, 0)
    assert len(res3["regressions"]) == 0
    test_results.append("Test 3 (Intentional bug fix with scope & invariant): PASSED")

    # Test 4: Invariant violation caught
    # Invariant: result must always be non-negative
    non_negative_inv = lambda args, outcome: outcome[0] is not None and outcome[0] >= 0

    def bad_calc(x: int, y: int) -> int:
        return x - y  # can be negative

    res4 = engine.run_differential(old_calc, bad_calc, [(5, 10), (1, 100)], target_invariant=non_negative_inv)
    assert res4["status"] == "FAIL"
    assert len(res4["invariant_violations"]) > 0
    test_results.append("Test 4 (Invariant violation gate): PASSED")

    print(json.dumps({
        "all_passed": True,
        "details": test_results
    }, indent=2))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_self_test()
    else:
        print("Usage: python3 differential_fuzz_engine.py --test")
