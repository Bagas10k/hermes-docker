# Atmo routes behind a native 9Router round-robin combo

Use this workflow when the user wants an existing OpenAI-compatible provider's routes alternated rather than a Mixture-of-Agents panel. Round-robin routes requests; MoA consults multiple models and has different cost/behavior.

## Preserve scope

- Do not switch Hermes's main/delegation model merely because a combo was requested. Report combo creation and activation separately.
- Resolve the precise IDs with the upstream `/v1/models` catalog; then run one real completion per member. Catalog presence alone does not prove the route works.
- A shared account quota is not expanded by route rotation. Keep attempts bounded; do not promise success on exhausted billing or shared quota.
- Snapshot the router SQLite database with `sqlite3.Connection.backup()` under mode 600 before writes. It contains credentials; never attach or print it.

## Use the installed management API

Discover the installed package and CLI API helper, often `src/cli/api/client.js` beneath the global `9router` npm package. This helper authenticates using the local CLI mechanism without exposing tokens. Prefer it over direct SQL writes, since management APIs update the running router coherently.

- `getProviderNodes()` / `createProviderNode({name,prefix,baseUrl,type:'openai-compatible',apiType:'chat'})` register a scoped custom upstream.
- `getProviders()` / `createApiKeyProvider({provider:node.id,name,apiKey,isActive:true})` add its credential. Resolve the existing Hermes custom-provider key in-process and pass via stdin, never argv/logs. Inspect only whitelisted metadata in responses.
- Prefix the upstream model ID with the custom node prefix. Upstream IDs containing a slash are preserved, e.g. `customprefix/ali/deepseek-v4.1-flash-1017`; prove the router sends the correct upstream ID with real completions.
- `createCombo({name,models,kind:null})` takes an array of model-ID **strings**, not objects. Reject an existing name/prefix with a different target instead of overwriting it.
- Read `getSettings()` and merge only `comboStrategies[comboName] = {fallbackStrategy:'round-robin'}` through `updateSettings()`. Inspect the installed dispatcher: some versions use global `comboStickyRoundRobinLimit`, not a per-combo sticky override. The native default 1 alternates every request; do not change global stickiness without authorization because other combos are affected.
- Read back the exact combo, node, and settings through API before claiming it is installed. Compare pre/post settings excluding the authorized new key and verify existing combos are unchanged.

## Verification boundaries

1. Three sequential real requests to the combo must return member A, B, A, HTTP 200, and usable assistant content; persist sanitized evidence.
2. Exercise the installed native combo function in an isolated harness for retryable error fallback and exhaustion. Use controlled response doubles and name them as a simulation, not real provider quota failure. Do not duplicate the algorithm into a homemade test and claim it tested native behavior.
3. Inspect native retry classification and confirm the member loop stops after exhausting its list. Mid-stream failures after HTTP 200 are a separate case; do not assume an untested stream can be safely replayed.
4. Register/select through Hermes only after verifying the exact local CLI/session resolution mechanism. A new router combo does not automatically replace an existing pinned delegation model.
5. Use at least 2048 max tokens for short reasoning-model probes unless the provider documents a different minimum. Very low caps can produce reasoning-only or blank content.

## Rollback

Use the management API to delete only the created combo/connection/node and remove only its named strategy entry, preserving concurrent updates. Do not restore an entire older DB over a live router just to undo one combo.
