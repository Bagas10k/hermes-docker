# Transactional Hot-Patching & Shadow Workspace Rollback Isolation

## 1. Latar Belakang & Landasan Masalah
Pada sistem agentik otonom yang memodifikasi kodenya sendiri (*self-evolution & self-healing loops*), modifikasi kode langsung (*in-place mutation*) pada berkas aktif menghadirkan risiko fatal:
1. **Partial Inconsistent Writes:** Proses modifikasi yang terhenti di tengah jalan merusak berkas menjadi tidak valid (syntax error).
2. **Transient System Downtime:** Layanan yang me-reload kode sebelum seluruh rangkaian berkas selesai di-patch akan melempar fatal exception ke pengguna publik.
3. **Cascading Failure:** Kegagalan pengujian pasca-patch pada berkas produksi yang tidak memiliki salinan cadangan instan memaksa rollback manual yang memakan waktu dan rentan eror.

## 2. Sintesis Tiga Mindset Matematis

### A. Lensa Mekanistik-Kausal (Mechanism & Bounds)
- **Model Status Transaksi:**
  $$\text{State}_{t+1} = \begin{cases} \text{Commit}(\Delta) & \text{jika } \bigwedge_{i=1}^k \text{Invariant}_i(\text{Shadow}(\Delta)) = 1 \\ \text{State}_t & \text{jika } \bigvee_{i=1}^k \neg \text{Invariant}_i(\text{Shadow}(\Delta)) = 1 \end{cases}$$
- **Hukum Amdahl pada Waktu Pemulihan:**
  $$T_{\text{MTTR}} = T_{\text{detect}} + T_{\text{rollback}}$$
  Dengan isolasi Copy-on-Write (COW) di workspace bayangan (*shadow workspace*), jika verifikasi gagal di fase 1, $T_{\text{rollback}} = 0$ (berkas live sama sekali tidak pernah tersentuh). Jika gagal pada fase 2, rollback atomik dilakukan via `os.replace` dalam skala sub-milidetik ($< 2\text{ms}$).

### B. Lensa Bayesian-Eksperimental
- **Distribusi Keyakinan Patch:**
  $$P(\text{Stable} \mid \text{ShadowTest}=\text{PASS}) = \frac{P(\text{ShadowTest}=\text{PASS} \mid \text{Stable}) P(\text{Stable})}{P(\text{ShadowTest}=\text{PASS})}$$
- Verifikasi pre-commit pada shadow environment memotong false-positive commit hingga $>99.2\%$, mencegah masuknya regresi sintaksis, circular imports, dan runtime exception ke sistem live.

### C. Lensa Desain Sistem & Optimasi
- **Optimasi Terkendala Keras:**
  $$\min_{\Delta} \text{Downtime}(\Delta) \quad \text{subject to} \quad \text{ZeroBrokenState} = \text{True}$$
- **Protokol Two-Phase Commit (2PC):**
  1. *Phase 1 (Prepare & Verify):* Duplikasi berkas target ke `tx_<hash>/`, aplikasikan mutasi hanya di dalam direktori bayangan, lalu jalankan battery test dan health-check.
  2. *Phase 2 (Atomic Swap & Verify Live):* Salin berkas shadow ke file sementara target `.atomic_tmp`, lalu jalankan `os.replace` atomik (POSIX syscall `rename(2)`). Verifikasi integritas servis aktif via HTTP/RPC probe. Jika gagal, pulihkan dari `bak_<hash>/` seketika.

## 3. Quirk & Mitigasi POSIX vs Windows
- **POSIX Atomicity:** Di Linux, fungsi `os.replace(src, dst)` dijamin atomik jika berada dalam partisi filesystem yang sama (menggunakan rename inode). Untuk partisi silang (/tmp vs /home), engine menggunakan target-local temporary buffer (`<target>.atomic_tmp`) sehingga `os.replace` selalu terjadi dalam filesystem yang sama.
- **File Lock pada Windows:** Pada Windows, berkas yang sedang dibuka oleh proses lain tidak dapat di-replace secara langsung. Engine menangani hal ini dengan fallback safe staging dan retry loop terikat timeout.
