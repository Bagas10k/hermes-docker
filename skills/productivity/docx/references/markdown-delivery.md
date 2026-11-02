# Long Markdown-to-Word delivery

Use this recipe for researched manuals and reports with many headings, tables and citations. Reuse an existing converter or the skill's JSON-spec creator before writing a new conversion engine.

## 1. Align the source before formatting

1. Lock the deliverable manifest: master, brief and any optional supporting files. Use one consistent version across titles, metadata, brief and output filenames.
2. Reconcile the latest authorized choices against ICP, first use case, value proposition, skill catalog, pilot criteria, examples, proposal, marketing calendar and action list. Keep secondary capabilities distinct from the primary offer.
3. If the buyer mix or strategy changes, do not present an old model as the new forecast. Recalculate with defensible inputs or retain it explicitly as a legacy sensitivity/stress test, with the incompatible assumptions named.
4. Preserve intentional legal-template placeholders; report them as fields to complete, not conversion defects. Remove authoring metadata/frontmatter from the customer-facing Word body.

## 2. Discover and isolate dependencies

Check imports and an existing renderer before installing anything. If a separate environment is needed, use a task-local environment rather than changing services or the shared Python installation. When `uv` is available, the following setup pattern supports the conversion workflow:

```bash
uv venv <workspace>/.word-venv
uv pip install --python <workspace>/.word-venv/bin/python python-docx markdown-it-py
```

Resolve paths from the current workspace; do not copy machine-specific paths from another task. Rendering requires a real Word-compatible renderer independently of `python-docx`.

## 3. Build native Word structure

For Markdown parsing, a minimal working route is:

```python
from markdown_it import MarkdownIt
parser = MarkdownIt("commonmark").enable("table")
tokens = parser.parse(markdown_without_frontmatter)
```

- Assign actual `Heading 1`, `Heading 2`, etc. styles, not just font sizes; Word navigation and TOC fields depend on semantic styles.
- Detect numbered chapters only at the specified heading level with an anchored pattern such as `^\d+\.\s+`; subsection numbers and SOP list items must not inflate the chapter count.
- Convert pipe tables into editable Word tables, with repeated header rows, suitable column widths and readable text. Track any extra cover table separately from content tables.
- Preserve emphasis, code, URLs, citations, blockquotes and ordered SOP steps. Explicitly restart independent lists or use literal step numbers when automatic numbering would continue across SOPs.
- Keep a readable static chapter list when inserting an uncomputed dynamic TOC. Tell the user to update fields in Word; do not fabricate page numbers.
- Give a short brief its own compact layout without a cover or TOC. A word count and page-budget design do not prove a physical one-page result.

## 4. Verify the exact outputs once, then deliver

Run three distinct checks:

1. **Package health:** reopen both files with `python-docx`, test ZIP integrity, and run the skill's `scripts/docx_validate.py`. Require exit code 0 and inspect its issues list.
2. **Content/structure preservation:** compare normalized Markdown inline text against body paragraphs and native table cells. Preserve each source table's row/column mapping, not only the global presence of common phrases. Check expected chapter sequence, native heading styles, citation URLs, material numbers and caveats. Explicitly whitelist deliberate transformations such as a reordered cover title; never drop arbitrary unmatched text.
3. **Rendered layout when available:** open/render the actual deliverables and inspect wide tables, page breaks, clipping and brief page count. If no renderer was exercised, state visual pagination is unverified; successful XML/ZIP checks are not visual verification.

Scope checks to the intended section: financial month rows belong to financial tables, not every matching row in the whole document. A roadmap may legitimately contain another row named M1.

Record independent-review findings and disposition separately from proof of parent verification. Reject reviewer suggestions that introduce unsupported tax rates, contractual promises or numeric corrections that fail recalculation.

Attach the requested Word files directly. Keep the final report short: what changed, what passed, and what remains unverified. Do not make the user open a support archive to find the primary deliverables.
