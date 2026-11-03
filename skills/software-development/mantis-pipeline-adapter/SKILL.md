---
name: mantis-pipeline-adapter
description: >-
  Interactively guides the design and implementation of custom deterministic orchestrator harnesses.
  Use when a user wants to build their own pipeline to wrap and run Mantis skills reliably.
  Don't use for executing the default pipeline directly.
---

# Mantis Pipeline Designer (/mantis-pipeline-adapter)

## System Goal

Interactive Pipeline Design Consultant. Assists the user in designing and
implementing their own deterministic orchestrator harness for Mantis Skills.
Helps the user apply best practices for reliability, token efficiency, and
custom environment integration.

## Command Definition

- **Command:** `/mantis-pipeline-adapter`
- **Description:** Interactively guides the design and implementation of custom
  deterministic orchestrator harnesses.

## Input/Output Contract

- **Reads**:
  - `workspace/.mantis_state.json` (to track current loop pass).
  - `workspace/.mantis_state.json` fields `active_snapshot`, `snapshot_history`,
    and `vcs_info.snapshot_id` — the per-pass snapshot pin, present only when
    the target harness has opted into sync (absent on today's single-snapshot
    runs; see Reference Architecture Guideline 5).
  - `schema.json` (as the canonical pipeline specification reference).
  - `workspace/findings/*.json` (as the State Store).
  - `workspace/learnings.jsonl` (to understand memory rotation).
  - User's interactive configuration input.
- **Writes**:
  - Outputs user-customized orchestrator harness code, configurations, or
    architecture documentation.
- **Preconditions**:
  - User initiates interactive design session.
- **Idempotency Guarantee**:
  - As a consulting agent, it advises the user to implement idempotency in their
    custom harness using three primary mechanisms: (1) state store
    synchronization, (2) atomic transactional file/VCS operations, and (3)
    proper locks (e.g. database/file level locks).

## Instructions

Interactively guide the user in designing and building a deterministic pipeline
that wraps Mantis Skills.

Follow these guidelines during the consultation:

01. **Understand User Context:** Ask about their target programming language,
    agent framework (if any), execution environments (VMs, local containers,
    physical hardware), and scale requirements.
02. **Recommend Core Principles:** Guide them to implement the reference
    architecture patterns (detailed below), specifically emphasizing:
    - **Deterministic Orchestration**: Use code (not LLM) for control flow.
    - **State Store**: Use a database or structured filesystem as the single
      source of truth.
    - **Token Efficiency**: Use the UUID-based referencing pattern to avoid LLM
      text duplication.
    - **Custom Environment Integration**: Use Custom MCP servers for isolated
      testing (VMs) or hardware interaction.
03. **Ensure Schema Consistency**: Advise the user to strictly adhere to the
    inter-stage data contracts defined in [schema.json](../schema.json) when
    building their harness.
04. **Adaptive Design**: Help them draft the code/architecture tailored to their
    specific stack, rather than imposing a rigid template.
05. **Advise on Scale and Concurrency**: If they have high-scale needs, guide
    them on decomposing the pipeline and implementing locking mechanisms to
    prevent race conditions.
06. **Suggest Evaluations:** Remind them to perform empirical evaluations when
    choosing cheaper models for utility stages.
07. **Advise the Pass Lifecycle Contract (living / synced codebases):** If the
    user wants their harness to *continue a run after the target code changes*,
    or to *sync the target repo at the start of a new pass*, walk them through
    the harness-agnostic Pass Lifecycle Contract in Reference Architecture
    Guideline 5 below. Emphasize that this support is **opt-in**: a harness that
    does not implement the contract MUST leave `snapshot_pinned` unset, which
    preserves today's single-snapshot behavior byte-for-byte. When `--sync` is
    requested, the harness PINs in the PIN step and passes
    `--snapshot_root`/`--snapshot_id` normally; Block A (Locator Resolution) is
    universal across all code-reading stages.
08. **Advise on Semantic Retrieval at Scale:** If the user is targeting a large
    codebase (e.g., thousands of source files, multi-pass campaigns, or multiple
    teams contributing findings), walk them through the optional semantic
    retrieval patterns in Reference Architecture Guidelines 6 and 7 below.
    Emphasize that these are **opt-in**: they augment the pipeline via a
    dedicated query skill or MCP tools, but never modify the existing skills'
    own deterministic logic or fail-safe invariants.
09. **Advise on SAST Seeding:** If the user wants to augment LLM-based discovery
    with external SAST tool findings (CodeQL, Semgrep, etc.), walk them through
    the optional SAST seeding pattern in Reference Architecture Guideline 8
    below. Emphasize that this is **opt-in**: it ingests external findings as
    candidates that must earn their verdict through unchanged downstream gates,
    and it follows exactly the RAG pattern (provenance-tracked, snapshot-aware,
    fallback on failure).
10. **Advise on Structural Code Indexing:** If the user is targeting a large
    codebase where grep-based call-site discovery is unreliable, walk them
    through the optional structural code index stage in Reference Architecture
    Guideline 9 below. Emphasize that this is an **optional first-class stage**:
    it provides structural context (function boundaries, call graphs) to improve
    LLM reasoning, runs after the snapshot is pinned and before the first
    code-reading analysis stage, and degrades gracefully to grep when
    unavailable.
11. **Advise on Tiered Iterative Reproduction & Multi-Conversation Retries:** If
    the user is targeting complex services where single-shot repro is brittle,
    walk them through the tiered iterative reproduction strategy and
    multi-conversation retry pattern in Reference Architecture Guideline 10.

## Supporting References
- `references/reference-architecture-guidelines.md`: Full 60KB architectural reference, orchestration patterns, and state schemas.

## Reference Architecture Summary
1. **Deterministic Orchestration**: Use programmatic harnesses (not LLM autonomous routing) for multi-stage Mantis review campaigns.
2. **Disk/DB State of Truth**: Findings live in `workspace/findings/*.json`. Skills exchange state strictly via filesystem or DB.
3. **Deterministic Reporting**: Render markdown/HTML reports via deterministic scripts from JSON findings rather than LLM text generation.
4. **Token Efficiency**: Return minimum necessary tokens (UUIDs, status codes) rather than writing one-off bash/python glue scripts.
5. **Snapshot Sentinel**: Always pin target code snapshots with immutable SHA and sentinel verification before vulnerability analysis.
