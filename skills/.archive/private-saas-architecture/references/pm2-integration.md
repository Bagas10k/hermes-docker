# PM2 Integration via Express API

When building a private SaaS dashboard (like Koper Kerja), you often need a DevOps compartment to monitor and control PM2 processes (e.g., stopping an automation agent or restarting the gateway) directly from the web interface.

Instead of writing complex custom daemon managers, wrap PM2's CLI via `child_process.exec` to serve JSON directly to the frontend.

## 1. Fetching Process List (`pm2 jlist`)
`pm2 jlist` outputs raw JSON. Parse it and map only the necessary fields to avoid exposing excessive internal server state or crashing the frontend with huge payloads.

```javascript
const { exec } = require('child_process');

app.get('/api/admin/pm2', (req, res) => {
    exec('pm2 jlist', (err, stdout) => {
        if (err) return res.status(500).json({error: err.message});
        try {
            const list = JSON.parse(stdout).map(p => ({
                id: p.pm_id,
                name: p.name,
                status: p.pm2_env.status, // e.g., 'online', 'stopped'
                cpu: p.monit ? p.monit.cpu : 0,
                ram: p.monit ? (p.monit.memory / 1024 / 1024).toFixed(1) : 0, // Convert bytes to MB
                uptime: p.pm2_env.pm_uptime
            }));
            res.json({ success: true, data: list });
        } catch (e) { 
            res.status(500).json({error: e.message}); 
        }
    });
});
```

## 2. Executing Actions (Restart/Stop/Start)
Use parameterized routing but strictly validate the action against an allowlist to prevent arbitrary code execution (Command Injection).

```javascript
app.post('/api/admin/pm2/:action', express.json(), (req, res) => {
    const action = req.params.action;
    const processName = req.body.name;
    
    // CRITICAL: Prevent command injection by strictly allowing specific actions
    if (!['restart', 'stop', 'start'].includes(action)) {
        return res.status(400).json({error: 'Invalid action'});
    }
    
    // In production, ensure processName is also validated/sanitized
    exec(\`pm2 \${action} "\${processName}"\`, (err, stdout) => {
        if (err) return res.status(500).json({error: err.message});
        res.json({ success: true, message: \`Proses \${processName} berhasil di-\${action}\` });
    });
});
```

## Pitfalls
- **Command Injection**: Never interpolate `req.body` directly into `exec()` without strictly validating it against an allowlist.
- **Missing Telemetry**: Processes that are stopped will not have a `p.monit` object in `pm2 jlist`. Always use optional chaining or fallback checks (e.g., `p.monit ? p.monit.cpu : 0`) to prevent `TypeError: Cannot read properties of undefined` when parsing.