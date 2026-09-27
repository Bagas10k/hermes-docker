#!/usr/bin/env python3
"""
Edge SLM Tool-Calling Engine & Validator
Deterministic schema validation, GBNF grammar generation, and fail-closed barriers for 1.5B-3B SLMs.
"""

import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

class SLMToolEngine:
    def __init__(self, allowed_tools: Optional[List[str]] = None):
        self.allowed_tools = set(allowed_tools or ["terminal", "read_file", "search_files", "write_file", "calculator"])

    def validate_tool_call(self, raw_call: str, schema_dict: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Validates raw model output against JSON structure and schema bounds fail-closed.
        """
        # Step 1: Parse JSON
        try:
            parsed = json.loads(raw_call.strip())
        except Exception as e:
            return False, None, f"JSON_PARSE_ERROR: {str(e)}"

        if not isinstance(parsed, dict):
            return False, None, "PAYLOAD_NOT_OBJECT: Expected top-level JSON dictionary."

        # Step 2: Validate tool name
        tool_name = parsed.get("tool") or parsed.get("name")
        if not tool_name:
            return False, None, "MISSING_TOOL_IDENTIFIER: 'tool' or 'name' field is required."

        if tool_name not in self.allowed_tools:
            return False, None, f"UNAUTHORIZED_TOOL: '{tool_name}' is not in allowed set."

        # Step 3: Validate arguments container
        args = parsed.get("parameters") or parsed.get("arguments") or parsed.get("args")
        if not isinstance(args, dict):
            return False, None, "INVALID_ARGUMENTS_FORMAT: 'parameters' must be a JSON object."

        # Step 4: Validate required parameters against schema
        expected_schema = schema_dict.get(tool_name, {})
        required_fields = expected_schema.get("required", [])
        for field in required_fields:
            if field not in args:
                return False, None, f"MISSING_REQUIRED_FIELD: '{field}' is required for tool '{tool_name}'."

        # Step 5: Type checking & boundary constraints
        properties = expected_schema.get("properties", {})
        for key, val in args.items():
            if key in properties:
                prop_type = properties[key].get("type")
                if prop_type == "string" and not isinstance(val, str):
                    return False, None, f"TYPE_MISMATCH: '{key}' must be string, got {type(val).__name__}."
                elif prop_type == "integer" and (not isinstance(val, int) or isinstance(val, bool)):
                    return False, None, f"TYPE_MISMATCH: '{key}' must be integer, got {type(val).__name__}."
                elif prop_type == "number" and not isinstance(val, (int, float)):
                    return False, None, f"TYPE_MISMATCH: '{key}' must be number, got {type(val).__name__}."
                elif prop_type == "boolean" and not isinstance(val, bool):
                    return False, None, f"TYPE_MISMATCH: '{key}' must be boolean, got {type(val).__name__}."
                elif prop_type == "array" and not isinstance(val, list):
                    return False, None, f"TYPE_MISMATCH: '{key}' must be list, got {type(val).__name__}."

        normalized = {
            "tool": tool_name,
            "parameters": args
        }
        return True, normalized, "VALIDATION_SUCCESS"

    def generate_gbnf_rule_for_tools(self, tool_schemas: Dict[str, Any]) -> str:
        """
        Generates deterministic GBNF grammar string for local llama.cpp / llama-server.
        """
        lines = [
            'root ::= "{" ws "\\"tool\\"" ws ":" ws tool-choice "," ws "\\"parameters\\"" ws ":" ws params-choice ws "}"',
            'ws ::= [ \\t\\n\\r]*',
            'string ::= "\\"" [^"\\\\]* "\\""',
            'number ::= ("-"? [0-9]+ ("." [0-9]+)?)',
            'boolean ::= ("true" | "false")'
        ]

        tool_names = list(tool_schemas.keys())
        tool_choice_parts = [f'"\\"{t}\\""' for t in tool_names]
        lines.append(f'tool-choice ::= ({" | ".join(tool_choice_parts)})')

        param_branches = []
        for t_name, s_data in tool_schemas.items():
            branch_rule = f'params-{t_name}'
            props = s_data.get("properties", {})
            reqs = s_data.get("required", [])

            prop_rules = []
            for p_name, p_spec in props.items():
                p_type = p_spec.get("type", "string")
                rule_val = p_type if p_type in ["string", "number", "boolean"] else "string"
                prop_rules.append(f'"\\"{p_name}\\"" ws ":" ws {rule_val}')

            joined_props = ' ("," ws)? '.join(prop_rules) if prop_rules else '""'
            lines.append(f'{branch_rule} ::= "{{" ws {joined_props} ws "}}"')
            param_branches.append(f'({branch_rule})')

        lines.append(f'params-choice ::= ({" | ".join(param_branches)})')
        return "\n".join(lines)


def run_unit_tests():
    print("[TEST] Running Edge SLM Tool-Calling Engine Verification Suite...")
    schemas = {
        "read_file": {
            "type": "object",
            "required": ["path"],
            "properties": {
                "path": {"type": "string"},
                "offset": {"type": "integer"}
            }
        },
        "calculator": {
            "type": "object",
            "required": ["expression"],
            "properties": {
                "expression": {"type": "string"}
            }
        }
    }

    engine = SLMToolEngine(allowed_tools=["read_file", "calculator"])

    # Test 1: Valid payload
    valid_raw = '{"tool": "read_file", "parameters": {"path": "/etc/hosts", "offset": 1}}'
    ok, norm, msg = engine.validate_tool_call(valid_raw, schemas)
    assert ok, f"Test 1 failed: {msg}"
    assert norm["tool"] == "read_file"
    print("  [PASS] Test 1: Valid tool call accepted and normalized.")

    # Test 2: Unauthorized tool name
    unauth_raw = '{"tool": "delete_database", "parameters": {"db": "prod"}}'
    ok, norm, msg = engine.validate_tool_call(unauth_raw, schemas)
    assert not ok and "UNAUTHORIZED_TOOL" in msg
    print("  [PASS] Test 2: Unauthorized tool blocked fail-closed.")

    # Test 3: Type mismatch (offset should be integer, not string)
    mismatch_raw = '{"tool": "read_file", "parameters": {"path": "/etc/hosts", "offset": "invalid"}}'
    ok, norm, msg = engine.validate_tool_call(mismatch_raw, schemas)
    assert not ok and "TYPE_MISMATCH" in msg
    print("  [PASS] Test 3: Parameter type mismatch caught fail-closed.")

    # Test 4: Missing required field
    missing_req = '{"tool": "read_file", "parameters": {"offset": 10}}'
    ok, norm, msg = engine.validate_tool_call(missing_req, schemas)
    assert not ok and "MISSING_REQUIRED_FIELD" in msg
    print("  [PASS] Test 4: Missing required field rejected.")

    # Test 5: GBNF Grammar Generation
    gbnf = engine.generate_gbnf_rule_for_tools(schemas)
    assert "root ::=" in gbnf
    assert 'tool-choice ::= ("\\"read_file\\"" | "\\"calculator\\"")' in gbnf
    print("  [PASS] Test 5: Deterministic GBNF grammar synthesis validated.")

    print("\n[SUCCESS] All 5 Edge SLM Tool-Calling invariants strictly verified.")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = run_unit_tests()
        sys.exit(0 if success else 1)
    else:
        print("Usage: slm_tool_engine.py --test")
        sys.exit(0)
