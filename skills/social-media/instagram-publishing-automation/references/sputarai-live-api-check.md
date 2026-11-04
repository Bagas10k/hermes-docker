# SputarAI live API checks

## When to Use
Use when asked to test SputarAI's existing Instagram connection, comments, or DMs. This is a workflow reference, not permanent proof a token is valid.

## Credential discovery
- Check the existing dedicated credential store before recursively searching the home directory: `/home/ubuntu/.chronicle-secrets/instagram-token` is the known SputarAI token-file candidate. SputarBall uses a separate file; never substitute it.
- Read credentials only within the probe process; never print token text, authenticated URLs, raw responses containing pagination tokens, or secret-bearing config values.
- Confirm account identity with `GET /me?fields=id,username` and require `username == sputarai` before reading comments or conversations or sending anything.

## Minimal read-only probe
- Use the account's actual login host and a currently supported API version confirmed in official documentation.
- Read own media: `GET /<IG_ID>/media?fields=id&limit=1`.
- Read comments: `GET /<MEDIA_ID>/comments?fields=id&limit=1`.
- Read DM conversation metadata: `GET /<IG_ID>/conversations?platform=instagram&fields=id&limit=1`.
- Log only HTTP status, sanitized error code/message, and returned item counts. Empty HTTP 200 is successful endpoint access, not evidence of reply-send capability or proof no older comments exist.
- Do not assume Instagram Login supports `GET /me/permissions`; it can fail with code 100, `Tried accessing nonexisting field (permissions)`. That is an unsupported probe, not proof comment/DM access is denied. Use actual relevant endpoints to distinguish failures.

## Reply testing
- Do not send deliberately invalid recipient/comment requests as an authorization test. They do not prove permissions and add avoidable write risk.
- If available lists contain no suitable owner-controlled test target, ask the owner to send a clearly marked test DM and/or comment on their own account's post; avoid unsolicited test replies to followers.
- After a test send is authorized and a specific target identified, post one bounded reply and read the exact reply/message back before claiming send success. Keep read permission, send success, and unattended auto-reply implementation as separate statuses.

## Communication
- On an approved capability test, perform the probe and return concrete results; do not keep repeating conditional descriptions or ask the owner to enable permissions before observing an actual denial.
- If blocked, identify exactly what the API returned and the smallest next step. Never present an empty inbox as an authorization failure.
