# Arsitektur Ephemeral Tool Sandboxing & MicroVM untuk Autonomous AI Agents

Dokumen ini menyajikan perbandingan arsitektur, parameter matematis, dan protokol isolasi runtime eksekusi tool berisiko tinggi pada sistem multi-agen otonom.

## 1. Spektrum Tingkat Isolasi (Sandboxing Spectrum)

| Tingkat | Teknologi | Startup Latency | Overhead RAM | Keamanan Kernel | Cocok Untuk |
|---|---|---|---|---|---|
| **Tier 0** | Host Unprivileged | <1 ms | 0 MB | Tidak ada (Shared host) | Read-only commands (`cat`, `grep`, `git diff`) |
| **Tier 1** | Wasm/WASI (Wasmtime) | 2–5 ms | 5–15 MB | Cap-based virtual mem | Eksekusi parser JSON/YAML, algoritma terisolasi |
| **Tier 2** | Bubblewrap / gVisor (runsc) | 25–100 ms | 30–80 MB | User-space kernel intercept | Kompilasi build, script Python, test execution |
| **Tier 3** | MicroVM (Firecracker/Kata) | 125–250 ms | 128–256 MB | Hardware virtualization (KVM) | Package install mentah, Docker in Docker, untrusted binary |

---

## 2. Model Matematis & Formulasi Tiga Mindset

### Lensa Mekanistik-Kausal (Mechanism & Bounds)
Sistem isolasi dimodelkan sebagai fungsi transformasi terkendala:
$$y = f(T_{\text{cmd}}, W_{\text{ephemeral}}, \Theta_{\text{resource}}) \quad \text{dengan batas} \quad \text{RAM} \le M_{\max}, \, t \le T_{\text{deadline}}$$

Efek percepatan eksekusi dengan mitigasi overhead sandbox dihitung melalui Hukum Amdahl:
$$S_{\text{latency}} = \frac{1}{(1 - p) + \frac{p}{s_{\text{tier}}}}$$
Di mana $p$ adalah fraksi komputasi aman yang dapat dialirkan ke Tier 0/1 tanpa pembentukan MicroVM penuh ($s \approx 250\times$ lebih cepat daripada cold-start Firecracker).

### Lensa Bayesian-Eksperimental (Evidence & Belief Updating)
Keyakinan tingkat risiko suatu tool dihitung berdasarkan riwayat pola intervensi:
$$P(\text{Dangerous} \mid E_{\text{pattern}}) = \frac{P(E_{\text{pattern}} \mid \text{Dangerous}) \cdot P(\text{Dangerous})}{P(E_{\text{pattern}})}$$
- Prior $P(\text{Dangerous}) = 0.05$ untuk skrip standar di workspace.
- Jika ditemukan manipulasi filesystem root (`/dev/`, `/etc/`, `rm -rf /`), Likelihood $\approx 0.99$, sehingga posterior keyakinan melompat ke $>0.98$, memicu eskalasi seketika ke Tier 3 (MicroVM) atau Hard Veto.

### Lensa Desain Sistem & Optimasi (Structure & Trade-offs)
Formulasi optimasi sumber daya agen:
$$\min_{\text{Tier}} \left( \text{Latency}(\text{Tier}) + \text{Cost}(\text{Tier}) \right) \quad \text{subject to} \quad \text{RiskEscape}(\text{Tier}) \le 0$$
- Kendala keras: Zero-leakage host filesystem.
- Pola Copy-on-Write (CoW) memastikan kegagalan run agen tidak merusak workspace asli (`commit` hanya berjalan saat exit code == 0 dan seluruh verifikasi lulus).

---

## 3. Protokol Transaksional Dua Fase (Two-Phase Commit / Rollback)

```
[Agent Emits Command]
         |
         v
[Risk Classifier]
         |
  +------+------+
  |             |
[Tier 0]     [Tier 2/3]
Direct       Create Ephemeral CoW Workspace
Host Read          |
             Run with RLIMIT_AS & Timeout
                   |
             Did it succeed (code == 0)?
             /                       \
           YES                       NO
            |                         |
     [Commit Phase]            [Rollback Phase]
  Promote verified files       shutil.rmtree(temp_dir)
  to Base Workspace            Zero host pollution
```
