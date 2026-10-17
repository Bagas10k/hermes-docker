# Chat Bridge Structured Output & JSON Resilience Guide

Defensive engineering patterns for AI agents delivering structured JSON or hybrid command-content payloads to chat platforms (WhatsApp, Telegram, Web).

## 1. The Token Truncation Hazard

When an LLM endpoint is called with structured output mode (`response_format: { type: "json_object" }` or JSON schema prompts):
- **Never artificially cap `max_tokens` to small budgets (e.g., 200–250 tokens)** for conversational or customer-facing turns.
- Conversational messages containing emojis, markdown styling, and multi-sentence explanations frequently exceed 200 tokens.
- When `max_tokens` is exceeded, the model halts generation mid-string. This leaves the JSON unclosed (missing closing quote `"` and brace `}`), rendering `JSON.parse()` impossible.
- **Rule**: Set `max_tokens` to at least 1,000–1,500 for chat responses, even when requesting JSON.

## 2. Robust Fault-Tolerant JSON Parser (No-Leak Guarantee)

Never let raw JSON strings, brackets, or escaped characters (`\n`, `\"`) leak to end-user chat interfaces.

```javascript
function parseStructuredAiResponse(rawText) {
    let reply = '';
    let metadata = {};
    const text = (rawText || '').trim().replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/i, '').trim();

    // Strategy 1: Standard JSON parse
    try {
        const obj = JSON.parse(text);
        if (obj && typeof obj === 'object') {
            reply = obj.reply || obj.message || obj.answer || obj.text || '';
            delete obj.reply; delete obj.message; delete obj.answer; delete obj.text;
            metadata = obj;
            if (reply) return { reply: String(reply).trim(), metadata };
        }
    } catch (_) {}

    // Strategy 2: Regex extraction for truncated or dirty JSON strings
    const replyMatch = text.match(/"reply"\s*:\s*"([\s\S]*?)(?:"\s*,\s*"[a-zA-Z0-9_-]+"|"[\s\S]*\}|$)/i);
    if (replyMatch && replyMatch[1]) {
        reply = replyMatch[1]
            .replace(/\\n/g, '\n')
            .replace(/\\"/g, '"')
            .replace(/\\\\/g, '\\')
            .trim();
    } else {
        // Strategy 3: Strip leading JSON keys and trailing dangling delimiters
        reply = text
            .replace(/^\{[\s\S]*?"reply"\s*:\s*"/i, '')
            .replace(/["}\s]+$/g, '')
            .replace(/\\n/g, '\n')
            .replace(/\\"/g, '"')
            .replace(/\\\\/g, '\\')
            .trim();
    }

    // Extract any known sibling fields (e.g. show_node, intent, action)
    const fieldMatches = text.matchAll(/"([a-zA-Z0-9_-]+)"\s*:\s*(?:"([^"]*)"|([true|false|null\d]+))/gi);
    for (const match of fieldMatches) {
        const key = match[1];
        const val = match[2] !== undefined ? match[2] : match[3];
        if (key !== 'reply' && val !== 'null') {
            metadata[key] = val;
        }
    }

    return { reply: reply || text, metadata };
}
```

## 3. Session History Hygiene (Preventing Context Poisoning)

When recording conversation history in SQLite, Redis, or local JSON state:
- **Always store the cleaned human-readable text** in `history.push({ role: 'assistant', content: cleanReply })`.
- **Never store the raw JSON envelope** in multi-turn history.
- **Why**: LLMs are few-shot learners. If previous turns in the prompt history contain `{"reply": "..."}`, the model will mimic that exact structure in future turns—even when instructed to speak plainly—and compounding token counts will trigger further truncation.
- **Database Remediation**: If an existing conversation session has been contaminated with raw JSON strings, run a migration/cleanup pass to strip envelopes and unescape newlines before the next turn runs.

## 4. Temperature Calibration for Structured Customer-Facing Agents

- Pure deterministic data extraction (e.g., receipt OCR): `temperature: 0.1` is appropriate.
- Conversational chat agents that return structured envelopes (e.g. `{ reply: "...", show_node: "..." }`): use `temperature: 0.6–0.7`.
- Using `0.1` for customer service bots causes rigid, repetitive, and mechanical replies; `0.6–0.7` preserves warmth and humor while maintaining schema compliance under JSON mode.
