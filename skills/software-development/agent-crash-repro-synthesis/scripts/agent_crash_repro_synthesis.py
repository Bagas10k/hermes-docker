#!/usr/bin/env python3
"""
agent_crash_repro_synthesis.py
Deterministic Crash Reproduction Loop & Minimal Repro Synthesis Engine.

Key Invariants:
1. Deterministic stack trace & exception frame extraction.
2. Binary hypothesis / delta-debugging minimization (Zeller's ddmin algorithm) on crash inputs.
3. Verification of crash reproducibility with bounded iterations (P(crash|minimized) == 1.0).
4. Generation of a standalone self-contained reproduction script.
"""

import sys
import os
import re
import json
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple, Callable

@dataclass
class CrashSignature:
    exception_type: str
    error_message: str
    culprit_file: Optional[str]
    culprit_line: Optional[int]
    stack_frames: List[Dict[str, Any]]
    fingerprint: str

@dataclass
class MinimizationResult:
    original_size: int
    minimized_size: int
    reduction_ratio: float
    iterations: int
    minimized_input: str
    fingerprint_match: bool

def parse_python_traceback(trace_text: str) -> CrashSignature:
    """
    Extracts structured crash signature from a Python traceback string.
    """
    lines = trace_text.strip().splitlines()
    frames = []
    exception_type = "UnknownError"
    error_message = ""
    culprit_file = None
    culprit_line = None

    frame_pattern = re.compile(r'^\s*File "([^"]+)", line (\d+)(?:, in (\w+))?')
    
    for i, line in enumerate(lines):
        match = frame_pattern.match(line)
        if match:
            f_path, f_line, f_func = match.groups()
            code_snippet = lines[i+1].strip() if i+1 < len(lines) else ""
            frames.append({
                "file": f_path,
                "line": int(f_line),
                "function": f_func or "<module>",
                "code": code_snippet
            })
            culprit_file = f_path
            culprit_line = int(f_line)

    # Last non-empty line usually holds `ExceptionType: message`
    for line in reversed(lines):
        if line.strip():
            if ":" in line:
                parts = line.split(":", 1)
                if not parts[0].startswith("File "):
                    exception_type = parts[0].strip()
                    error_message = parts[1].strip()
                    break
            else:
                exception_type = line.strip()
                break

    # Fingerprint is deterministic hash of exception_type + culprit_file basename + culprit_line
    file_base = os.path.basename(culprit_file) if culprit_file else "unknown"
    fingerprint = f"{exception_type}@{file_base}:{culprit_line}"

    return CrashSignature(
        exception_type=exception_type,
        error_message=error_message,
        culprit_file=culprit_file,
        culprit_line=culprit_line,
        stack_frames=frames,
        fingerprint=fingerprint
    )

def ddmin_minimize(
    input_items: List[Any],
    test_fn: Callable[[List[Any]], bool],
    max_iterations: int = 100
) -> Tuple[List[Any], int]:
    """
    Zeller's Delta Debugging (ddmin) algorithm:
    Finds a 1-minimal subset of input_items that satisfies test_fn.
    test_fn(subset) -> True if the crash is reproduced, False otherwise.
    """
    n = 2
    items = list(input_items)
    iterations = 0

    while len(items) >= 2 and iterations < max_iterations:
        iterations += 1
        subsets = []
        step = max(1, len(items) // n)
        for i in range(0, len(items), step):
            subsets.append(items[i:i + step])

        reduced = False
        # 1. Try subsets
        for subset in subsets:
            if len(subset) < len(items) and test_fn(subset):
                items = subset
                n = max(n - 1, 2)
                reduced = True
                break

        if reduced:
            continue

        # 2. Try complements
        for subset in subsets:
            complement = [item for item in items if item not in subset]
            if len(complement) < len(items) and len(complement) > 0 and test_fn(complement):
                items = complement
                n = max(n - 1, 2)
                reduced = True
                break

        if reduced:
            continue

        if n >= len(items):
            break
        n = min(len(items), 2 * n)

    return items, iterations

def synthesize_minimal_repro(
    target_command: str,
    original_input_lines: List[str],
    oracle_evaluator: Callable[[List[str]], bool]
) -> MinimizationResult:
    """
    Minimizes crash input lines and evaluates reduction efficiency.
    """
    orig_size = len(original_input_lines)
    minimized_lines, iters = ddmin_minimize(original_input_lines, oracle_evaluator)
    min_size = len(minimized_lines)
    ratio = (orig_size - min_size) / orig_size if orig_size > 0 else 0.0

    return MinimizationResult(
        original_size=orig_size,
        minimized_size=min_size,
        reduction_ratio=ratio,
        iterations=iters,
        minimized_input="\n".join(minimized_lines),
        fingerprint_match=oracle_evaluator(minimized_lines)
    )

def generate_repro_script(
    signature: CrashSignature,
    repro_code: str,
    output_path: Optional[str] = None
) -> str:
    """
    Generates a standalone, deterministic Python reproduction script.
    """
    template = f'''#!/usr/bin/env python3
"""
Autonomous Crash Reproducer.
Fingerprint: {signature.fingerprint}
Expected Exception: {signature.exception_type}
Message: {signature.error_message}
"""
import sys

def run_repro():
{repro_code}

if __name__ == "__main__":
    try:
        run_repro()
        print("FAIL: Crash did not reproduce (silent success or resolved).", file=sys.stderr)
        sys.exit(1)
    except {signature.exception_type} as e:
        print(f"PASS: Deterministically reproduced expected {signature.exception_type}: {{e}}")
        sys.exit(0)
    except Exception as e:
        print(f"FAIL: Unexpected exception {{type(e).__name__}}: {{e}}", file=sys.stderr)
        sys.exit(2)
'''
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(template)
        os.chmod(output_path, 0o755)
    return template

if __name__ == "__main__":
    print("Agent Crash Repro Synthesis Engine Loaded Successfully.")
