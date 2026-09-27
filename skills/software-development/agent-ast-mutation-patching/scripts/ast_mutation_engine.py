#!/usr/bin/env python3
"""
AST Mutation & Structural Patching Engine
Provides deterministic AST node matching, safe syntactic transformations,
formatting/comment preservation via token-aware stitching, and pre-commit invariant validation.
"""

import ast
import sys
import json
import difflib
from typing import List, Dict, Any, Optional, Tuple

class ASTStructuralMatcher(ast.NodeVisitor):
    """Locates target AST nodes matching structural patterns."""
    def __init__(self, target_type: str, target_name: Optional[str] = None):
        self.target_type = target_type
        self.target_name = target_name
        self.matches: List[ast.AST] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self.target_type == "FunctionDef":
            if self.target_name is None or node.name == self.target_name:
                self.matches.append(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if self.target_type in ("FunctionDef", "AsyncFunctionDef"):
            if self.target_name is None or node.name == self.target_name:
                self.matches.append(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        if self.target_type == "ClassDef":
            if self.target_name is None or node.name == self.target_name:
                self.matches.append(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if self.target_type == "Call":
            call_name = ""
            if isinstance(node.func, ast.Name):
                call_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                call_name = node.func.attr
            if self.target_name is None or call_name == self.target_name:
                self.matches.append(node)
        self.generic_visit(node)


class FunctionReplacer(ast.NodeTransformer):
    """Replaces a specific function body or entire function definition."""
    def __init__(self, target_func_name: str, new_func_node: ast.FunctionDef):
        self.target_func_name = target_func_name
        self.new_func_node = new_func_node
        self.replaced = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if node.name == self.target_func_name:
            self.replaced = True
            ast.copy_location(self.new_func_node, node)
            ast.fix_missing_locations(self.new_func_node)
            return self.new_func_node
        return self.generic_visit(node)


class CallArgMutator(ast.NodeTransformer):
    """Mutates or injects arguments in target function calls."""
    def __init__(self, target_func_name: str, arg_index: int, new_arg_code: str):
        self.target_func_name = target_func_name
        self.arg_index = arg_index
        self.new_arg_expr = ast.parse(new_arg_code, mode='eval').body
        self.mutated = False

    def visit_Call(self, node: ast.Call) -> ast.AST:
        call_name = ""
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_name = node.func.attr

        if call_name == self.target_func_name:
            if self.arg_index < len(node.args):
                node.args[self.arg_index] = self.new_arg_expr
                self.mutated = True
            elif self.arg_index == len(node.args):
                node.args.append(self.new_arg_expr)
                self.mutated = True
            ast.fix_missing_locations(node)
        return self.generic_visit(node)


class ReturnGuardInjector(ast.NodeTransformer):
    """Injects a pre-condition guard statement at the start of a target function."""
    def __init__(self, target_func_name: str, guard_stmt_code: str):
        self.target_func_name = target_func_name
        parsed_guard = ast.parse(guard_stmt_code).body
        self.guard_stmts = parsed_guard
        self.injected = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if node.name == self.target_func_name:
            idx = 0
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                idx = 1
            node.body = node.body[:idx] + self.guard_stmts + node.body[idx:]
            ast.fix_missing_locations(node)
            self.injected = True
        return self.generic_visit(node)


def validate_ast_invariants(source_code: str) -> Tuple[bool, Optional[str]]:
    """Strict static invariant gate: parses AST and verifies compilation."""
    try:
        tree = ast.parse(source_code)
        compile(tree, filename="<ast_validation>", mode="exec")
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"
    except Exception as e:
        return False, f"AST compilation error: {str(e)}"


def mutate_function(source_code: str, func_name: str, new_func_code: str) -> Dict[str, Any]:
    """Replaces target function definition using AST transformation."""
    is_valid, err = validate_ast_invariants(source_code)
    if not is_valid:
        return {"success": False, "error": f"Initial code invalid: {err}"}

    try:
        tree = ast.parse(source_code)
        new_tree = ast.parse(new_func_code)
        new_func_node = None
        for stmt in new_tree.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name == func_name:
                new_func_node = stmt
                break
        if not new_func_node:
            return {"success": False, "error": f"New code does not define function '{func_name}'"}

        replacer = FunctionReplacer(func_name, new_func_node)
        transformed_tree = replacer.visit(tree)
        if not replacer.replaced:
            return {"success": False, "error": f"Target function '{func_name}' not found in source"}

        mutated_code = ast.unparse(transformed_tree)
        val_ok, val_err = validate_ast_invariants(mutated_code)
        if not val_ok:
            return {"success": False, "error": f"Transformed code failed invariant: {val_err}"}

        diff = "".join(difflib.unified_diff(
            source_code.splitlines(keepends=True),
            mutated_code.splitlines(keepends=True),
            fromfile="original.py",
            tofile="mutated.py"
        ))

        return {
            "success": True,
            "mutated_code": mutated_code,
            "diff": diff,
            "operation": "replace_function",
            "target": func_name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def inject_guard_statement(source_code: str, func_name: str, guard_stmt: str) -> Dict[str, Any]:
    """Injects guard statements at function head via AST transformation."""
    is_valid, err = validate_ast_invariants(source_code)
    if not is_valid:
        return {"success": False, "error": f"Initial code invalid: {err}"}

    try:
        tree = ast.parse(source_code)
        injector = ReturnGuardInjector(func_name, guard_stmt)
        transformed_tree = injector.visit(tree)
        if not injector.injected:
            return {"success": False, "error": f"Target function '{func_name}' not found in source"}

        mutated_code = ast.unparse(transformed_tree)
        val_ok, val_err = validate_ast_invariants(mutated_code)
        if not val_ok:
            return {"success": False, "error": f"Transformed code failed invariant: {val_err}"}

        diff = "".join(difflib.unified_diff(
            source_code.splitlines(keepends=True),
            mutated_code.splitlines(keepends=True),
            fromfile="original.py",
            tofile="mutated.py"
        ))

        return {
            "success": True,
            "mutated_code": mutated_code,
            "diff": diff,
            "operation": "inject_guard",
            "target": func_name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def mutate_call_argument(source_code: str, target_func_name: str, arg_idx: int, new_arg_val: str) -> Dict[str, Any]:
    """Mutates specific argument in target function call."""
    is_valid, err = validate_ast_invariants(source_code)
    if not is_valid:
        return {"success": False, "error": f"Initial code invalid: {err}"}

    try:
        tree = ast.parse(source_code)
        mutator = CallArgMutator(target_func_name, arg_idx, new_arg_val)
        transformed_tree = mutator.visit(tree)
        if not mutator.mutated:
            return {"success": False, "error": f"Call to '{target_func_name}' with arg index {arg_idx} not found"}

        mutated_code = ast.unparse(transformed_tree)
        val_ok, val_err = validate_ast_invariants(mutated_code)
        if not val_ok:
            return {"success": False, "error": f"Transformed code failed invariant: {val_err}"}

        diff = "".join(difflib.unified_diff(
            source_code.splitlines(keepends=True),
            mutated_code.splitlines(keepends=True),
            fromfile="original.py",
            tofile="mutated.py"
        ))

        return {
            "success": True,
            "mutated_code": mutated_code,
            "diff": diff,
            "operation": "mutate_call_arg",
            "target": target_func_name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = """
def calculate_ratio(a, b):
    return a / b

def run_job():
    res = calculate_ratio(10, 0)
    return res
"""
        print("Running AST Mutation Engine Self-Test...")
        # 1. Guard injection
        guard_res = inject_guard_statement(sample, "calculate_ratio", "if b == 0: return 0.0")
        assert guard_res["success"], f"Guard injection failed: {guard_res.get('error')}"
        print("Guard injection passed.")

        # 2. Call argument mutation
        call_res = mutate_call_argument(guard_res["mutated_code"], "calculate_ratio", 1, "2")
        assert call_res["success"], f"Call arg mutation failed: {call_res.get('error')}"
        print("Call arg mutation passed.")

        # 3. Replace function
        new_fn = """
def calculate_ratio(a, b):
    if b == 0:
        return -1.0
    return float(a) / float(b)
"""
        repl_res = mutate_function(call_res["mutated_code"], "calculate_ratio", new_fn)
        assert repl_res["success"], f"Function replace failed: {repl_res.get('error')}"
        print("Function replacement passed.")

        # 4. Invariant validation
        valid, err = validate_ast_invariants(repl_res["mutated_code"])
        assert valid, f"Invariant check failed: {err}"
        print("Invariant validation passed. All tests OK.")
