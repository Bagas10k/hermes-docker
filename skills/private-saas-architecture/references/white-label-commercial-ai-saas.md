# White-Label Commercial AI SaaS & Multi-Tenant Quota Metering

Topical reference for building multi-tenant commercial AI studio platforms, token quota billing, voucher redemption, Google OAuth integration, and dynamic persona isolation.

---

## 1. SQLite WAL Multi-Tenant Quota Schema

Use `better-sqlite3` with WAL mode enabled (`PRAGMA journal_mode = WAL;`) for sub-millisecond concurrent operations:

```sql
-- Users and token quotas
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  phone TEXT,
  password_hash TEXT NOT NULL,
  salt TEXT NOT NULL,
  role TEXT DEFAULT 'user', -- 'admin' | 'user'
  quota_tokens INTEGER DEFAULT 50000,
  used_tokens INTEGER DEFAULT 0,
  is_active INTEGER DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Voucher codes for top-up
CREATE TABLE IF NOT EXISTS voucher_codes (
  id TEXT PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  token_amount INTEGER NOT NULL,
  is_used INTEGER DEFAULT 0,
  used_by TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  used_at DATETIME,
  FOREIGN KEY (used_by) REFERENCES users(id)
);

-- Audit ledger for all token deductions and top-ups
CREATE TABLE IF NOT EXISTS token_transactions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  amount INTEGER NOT NULL,
  balance_after INTEGER NOT NULL,
  type TEXT NOT NULL, -- 'deduct' | 'topup' | 'bonus'
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Session tokens
CREATE TABLE IF NOT EXISTS user_sessions (
  id TEXT PRIMARY KEY,
  token TEXT UNIQUE NOT NULL,
  user_id TEXT NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 2. Password Security & Timing-Safe Verification

Avoid plain SHA-256 for passwords. Use Node native `crypto.scryptSync` with random 16-byte salt and constant-time comparison:

```javascript
const crypto = require('crypto');

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, 64).toString('hex');
  return { hash, salt };
}

function verifyPassword(password, storedHash, salt) {
  const hash = crypto.scryptSync(password, salt, 64).toString('hex');
  return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), Buffer.from(storedHash, 'hex'));
}
```

---

## 3. Dynamic Persona Isolation Pattern

To make the AI feel 100% like the customer's own personal assistant while preserving full administrative context for the owner:

```javascript
function resolveSystemPersona(currentUser) {
  if (currentUser.role === 'admin') {
    return `Kamu adalah Mumu Agent, mitra rekayasa kognitif otonom terpercaya milik Admin.
- Akses penuh infrastruktur internal, telemetri, dan repositori pengetahuan.
- Format jawaban terstruktur dengan Markdown dan estimasi token.`;
  }

  // Commercial customer: 100% white-label persona
  return `Kamu adalah Mumu, asisten cerdas pribadi profesional yang secara eksklusif didedikasikan untuk ${currentUser.name}.
- Jangan pernah menyebutkan rincian server backend, database, atau pemilik sistem lain.
- Fokus penuh pada kebutuhan, produktivitas, dan keberhasilan ${currentUser.name}.
- Cantumkan estimasi token di akhir balasan.`;
}
```

---

## 4. Real-Time Token Metering Lifecycle

1. **Pre-flight Check**: Before initiating the LLM stream, verify `remaining_tokens > 0`. If exhausted, return HTTP 200 with an SSE event containing an error message instructing the user to top-up, and terminate the stream.
2. **Streaming Execution**: Stream chunks as normal via SSE (`data: {"delta": "..."}`).
3. **Post-stream Deduction**: In the `[DONE]` completion handler:
   ```javascript
   const tokenEstimate = Math.max(25, Math.round(fullContent.length / 3.8));
   if (currentUser.role !== 'admin') {
     mumuDb.deductTokens(currentUser.id, tokenEstimate);
     currentUser = mumuDb.getUserById(currentUser.id);
   }
   res.write(`data: ${JSON.stringify({
     done: true,
     tokens: tokenEstimate,
     quota_remaining: currentUser.remaining_tokens
   })}\n\n`);
   ```
4. **Client UI Sync**: The frontend updates the navbar quota badge dynamically without reloading the page.

---

## 5. Google Identity Services & OAuth 2.0 Backend Verification

To implement Google Sign-In with zero external npm dependencies:

1. **Frontend Google SDK**:
   ```html
   <script src="https://accounts.google.com/gsi/client" async defer></script>
   ```
2. **Backend Native Token Verification**:
   Verify the incoming Google JWT credential directly against Google's public tokeninfo endpoint without heavy client libraries:
   ```javascript
   const verifyRes = await fetch(`https://oauth2.googleapis.com/tokeninfo?id_token=${encodeURIComponent(credential)}`);
   if (!verifyRes.ok) throw new Error('Token Google tidak valid');
   const gData = await verifyRes.json();
   const { email, name, sub, picture } = gData;
   ```
3. **Upsert User & Auto-Credit**:
   ```javascript
   function upsertGoogleUser({ email, name, googleId, avatar = '' }) {
     const cleanEmail = email.toLowerCase().trim();
     const existing = db.prepare('SELECT * FROM users WHERE email = ?').get(cleanEmail);
     if (existing) return sanitizeUser(existing);

     const id = 'usr_g_' + Date.now().toString(36) + crypto.randomBytes(4).toString('hex');
     const salt = crypto.randomBytes(16).toString('hex');
     const password_hash = hashPassword(crypto.randomBytes(32).toString('hex'), salt);
     db.prepare(`
       INSERT INTO users (id, name, email, phone, password_hash, salt, quota_tokens, used_tokens, role)
       VALUES (?, ?, ?, '', ?, ?, 50000, 0, 'user')
     `).run(id, (name || 'Pengguna Google').trim(), cleanEmail, password_hash, salt);
     return getUserById(id);
   }
   ```
4. **Dual-Mode Graceful Fallback**:
   When Google Cloud Client ID is not yet generated, provide a fast instant login modal allowing users to enter their Google identity directly for trial testing, alongside an on-the-fly Client ID configuration field that persists to `google_auth.json`.

---

## 6. Zero-Friction Fast Authentication Pattern (WhatsApp/Email-First)

When building consumer AI portals where users purchase token quotas, avoid multi-step registration forms or mandatory OAuth setup. Implement a **Zero-Friction Fast Login** pipeline:

```javascript
function fastAuthenticateOrRegister({ emailOrPhone, password = '', name = '' }) {
  const clean = (emailOrPhone || '').toLowerCase().trim();
  if (!clean) throw new Error('Email atau Nomor WhatsApp wajib diisi.');

  const isEmail = clean.includes('@');
  const user = db.prepare('SELECT * FROM users WHERE email = ? OR phone = ?').get(clean, clean);
  const now = new Date().toISOString();

  if (user) {
    // Master admin accounts MUST enforce password
    if (user.role === 'admin' || user.role === 'master') {
      if (!password) throw new Error('Akun Master Admin wajib memasukkan kata sandi.');
      const hash = hashPassword(password, user.salt);
      if (hash !== user.password_hash) throw new Error('Kata sandi salah.');
    } else if (password) {
      // Optional password check if customer set one
      const hash = hashPassword(password, user.salt);
      if (hash !== user.password_hash) throw new Error('Kata sandi salah.');
    }
    db.prepare('UPDATE users SET last_login = ? WHERE id = ?').run(now, user.id);
    return { user: sanitizeUser(user), isNew: false };
  }

  // Not found -> Auto-register seamless new user with bonus tokens!
  const id = 'usr_' + Date.now().toString(36) + crypto.randomBytes(4).toString('hex');
  const salt = crypto.randomBytes(16).toString('hex');
  const passToHash = password || crypto.randomBytes(24).toString('hex');
  const password_hash = hashPassword(passToHash, salt);

  const fallbackName = isEmail ? clean.split('@')[0] : ('Pengguna ' + clean.slice(-4));
  const finalName = (name || fallbackName).trim();
  const userEmail = isEmail ? clean : '';
  const userPhone = !isEmail ? clean : '';

  db.prepare(`
    INSERT INTO users (id, name, email, phone, password_hash, salt, quota_tokens, used_tokens, role, created_at, last_login)
    VALUES (?, ?, ?, ?, ?, ?, 50000, 0, 'user', ?, ?)
  `).run(id, finalName, userEmail, userPhone, password_hash, salt, now, now);

  return { user: getUserById(id), isNew: true };
}
```

### UX Principles for Zero-Friction Portals:
1. **Single Entry Field**: Only ask for "WhatsApp atau Email" on the primary view.
2. **Hidden/Collapsible Password**: Keep password fields hidden behind an optional `+ Gunakan Kata Sandi` toggle. Automatically expand and focus the password field if an admin account is detected.
3. **Auto-Register on Submit**: Never force users to toggle between "Login" and "Register" tabs. Submitting an unrecognized phone number or email creates the account with welcome tokens in 1 second.
4. **1-Click Guest Trial**: Provide an explicit "Coba Langsung Tanpa Akun (Tamu)" button generating an ephemeral session with 50.000 tokens for immediate evaluation.
