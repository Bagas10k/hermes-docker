#!/usr/bin/env python3
"""
context_compactor.py
Deterministic Context Compaction & Prefix Cache Preservation Utility.
Author: Bagas Cihuy & Hermes Agent
"""

import sys
import json
import re
import argparse
from typing import List, Dict, Any, Tuple

def estimate_tokens(text: str) -> int:
    """Fast deterministic whitespace/punctuation token estimation (~1.3 tokens per word)."""
    words = len(re.findall(r'\S+', text))
    chars = len(text)
    return max(1, int((words * 1.25 + chars / 4.0) / 2.0))

def parse_messages(messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Partition messages into:
    1. Static Prefix (System instructions, foundational memory)
    2. Dynamic Middle (Prior turns, repetitive tool outputs, candidate for compaction)
    3. Active Window (Last N turns preserved verbatim for immediate conversational flow)
    """
    if not messages:
        return [], [], []

    # Identify static prefix (system message and initial invariants)
    prefix = []
    rest = []
    
    for i, m in enumerate(messages):
        if m.get("role") == "system" or (i == 0 and m.get("role") == "user" and "system" in m.get("content", "").lower()):
            prefix.append(m)
        else:
            rest.extend(messages[i:])
            break

    # Preserve last 4 messages in active window
    active_window_size = 4
    if len(rest) <= active_window_size:
        return prefix, [], rest
    
    middle = rest[:-active_window_size]
    active = rest[-active_window_size:]
    return prefix, middle, active

def compact_tool_output(content: str, max_chars: int = 400) -> str:
    """Trim repetitive verbose tool output while preserving head, tail, and exit status."""
    if len(content) <= max_chars:
        return content
    
    lines = content.splitlines()
    if len(lines) <= 10:
        head = content[:max_chars // 2]
        tail = content[-max_chars // 2:]
        return f"{head}\n... [OUTPUT COMPACTED: {len(content)} chars -> {max_chars} chars] ...\n{tail}"

    head_lines = lines[:4]
    tail_lines = lines[-4:]
    omitted = len(lines) - 8
    return "\n".join(head_lines) + f"\n... [{omitted} lines pruned by context-compaction-curator] ...\n" + "\n".join(tail_lines)

def distill_history(middle_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract verifiable facts, tool outcomes, and user steering decisions."""
    decisions = []
    completed_actions = []
    artifacts_created = []

    for msg in middle_messages:
        role = msg.get("role")
        content = msg.get("content", "")

        # Detect user directives / constraints
        if role == "user":
            lines = content.splitlines()
            for line in lines:
                s = line.strip()
                if re.match(r'^(jangan|wajib|prioritas|fokus|target|standar|aturan)\b', s, re.IGNORECASE):
                    decisions.append(s)

        # Detect tool results and file artifacts
        if role == "tool" or (role == "assistant" and "tool_calls" in msg):
            if "write_file" in str(msg) or "patch" in str(msg):
                files = re.findall(r'path[\'"]?:\s*[\'"]([^\'"]+)[\'"]', str(msg))
                for f in files:
                    if f not in artifacts_created:
                        artifacts_created.append(f)
            if "completed" in content.lower() or "success" in content.lower():
                completed_actions.append(content[:120].strip().replace("\n", " "))

    summary_note = {
        "role": "system",
        "name": "compacted_context_summary",
        "content": (
            "### COMPACTED CONTEXT DISTILLATION\n"
            f"- Pruned turns: {len(middle_messages)}\n"
            f"- Confirmed Artifacts: {', '.join(artifacts_created) if artifacts_created else 'None'}\n"
            f"- Active Constraints: {'; '.join(decisions[:5]) if decisions else 'Follow base system prompt'}\n"
            f"- Completed Milestones: {'; '.join(completed_actions[-4:]) if completed_actions else 'Task in progress'}\n"
        )
    }
    return summary_note

def run_compaction(input_file: str, output_file: str, max_tokens: int = 8000) -> Dict[str, Any]:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    messages = data if isinstance(data, list) else data.get("messages", [])
    raw_tokens = sum(estimate_tokens(json.dumps(m)) for m in messages)

    prefix, middle, active = parse_messages(messages)

    # Clean individual middle tool outputs first
    for m in middle:
        if m.get("role") == "tool":
            m["content"] = compact_tool_output(m.get("content", ""))

    middle_tokens = sum(estimate_tokens(json.dumps(m)) for m in middle)
    total_est = sum(estimate_tokens(json.dumps(m)) for m in prefix + middle + active)

    # If still exceeding target or middle has >= 4 messages, distill middle to summary
    if total_est > max_tokens or len(middle) >= 6:
        distilled_node = distill_history(middle)
        final_messages = prefix + [distilled_node] + active
    else:
        final_messages = prefix + middle + active

    compacted_tokens = sum(estimate_tokens(json.dumps(m)) for m in final_messages)

    result_payload = {
        "status": "COMPACTED",
        "raw_messages_count": len(messages),
        "final_messages_count": len(final_messages),
        "raw_tokens_est": raw_tokens,
        "compacted_tokens_est": compacted_tokens,
        "tokens_saved_pct": round((1.0 - (compacted_tokens / max(1, raw_tokens))) * 100, 2),
        "prefix_preserved_untouched": True,
        "messages": final_messages
    }

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_payload, f, indent=2)

    return result_payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Context Compactor")
    parser.add_argument("--input", required=True, help="Input JSON messages file")
    parser.add_argument("--output", required=False, default="", help="Output JSON file")
    parser.add_argument("--max-tokens", type=int, default=8000, help="Target context token ceiling")
    args = parser.parse_args()

    res = run_compaction(args.input, args.output, args.max_tokens)
    print(json.dumps({
        "status": res["status"],
        "raw_messages": res["raw_messages_count"],
        "final_messages": res["final_messages_count"],
        "raw_tokens_est": res["raw_tokens_est"],
        "compacted_tokens_est": res["compacted_tokens_est"],
        "saved_pct": f"{res['tokens_saved_pct']}%",
        "prefix_preserved": res["prefix_preserved_untouched"]
    }, indent=2))
