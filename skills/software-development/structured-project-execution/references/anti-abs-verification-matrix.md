# Anti-ABS Verification Matrix & Radical Truthfulness

Prohibiting premature, fabricated, or ungrounded success claims through strict empirical assertions.

## 1. The Anti-ABS Doctrine
ABS (*Asal Bapak Senang*) is the pathological habit of declaring a task successful simply because a file was saved or a command was sent, without independently verifying runtime output.
- **The Core Rule:** A task is NOT complete until proven by direct, verifiable runtime evidence (exit code 0, HTTP status code 200, clean log output, or browser visual inspection).

---

## 2. Epistemic Classification System

Every technical claim must be explicitly categorized:

| Status | Definition | When to Use | Action Required |
|---|---|---|---|
| `KNOWN` | Empirically verified fact | Command executed, curl test returned 200, unit test passed. | Report result with exact command output. |
| `LIKELY` | High probability based on standard specs | File syntax validated, pattern matches working sibling, but live runtime uncalled. | Explicitly label: *"Telah disesuaikan secara sintaks, menunggu uji runtime."* |
| `UNCERTAIN` | Ambiguous symptom or competing causes | Multiple potential root causes identified in log trace. | Execute a diagnostic discriminator probe before patching. |
| `UNKNOWN` | Unverified assumption | No empirical data available. | State ignorance honestly; never present as fact. |

---

## 3. Mandatory Verification Checklist Before Reporting "Done"
- [ ] **Runtime Process Check:** Is the service active and listening on the expected port?
- [ ] **HTTP Ingress Assertion:** Does `curl -s -o /dev/null -w "%{http_code}" <URL>` return 200 or 302?
- [ ] **Zero Regression Audit:** Are existing sibling services or database tables untouched and functioning?
- [ ] **Error Log Absence:** Are there zero fatal stack traces in `pm2 logs` or application error streams?
