# DOKTRIN PEMIKIRAN MINIMUM OPTIMAL (HERMES COGNITIVE BUDGET)
**Pencipta:** Bagas Saputra (Bagas Cihuy)  
**Dokumen:** `/home/ubuntu/otak-koding/SISTEM_AGENT/DOKTRIN_PEMIKIRAN_MINIMUM_OPTIMAL.md`  
**Status:** DOKTRIN OPERASIONAL RESMI  
**Tanggal:** 28 September 2026  

---

## 1. PRINSIP INTI
Bukan berpikir sebanyak mungkin, melainkan **menggunakan pemikiran minimum yang cukup untuk menghasilkan jawaban benar**.

## 2. FORMULA PIPELINE
```text
REQUEST
  ↓
COMPLEXITY CHECK (FAST / STANDARD / DEEP)
  ↓
MINIMUM CONTEXT (Intent-based routing)
  ↓
MINIMUM AGENT (1-2 agent cukup)
  ↓
MINIMUM SKILL (Lazy-load metadata dulu)
  ↓
EXECUTE (Filter/retrieval murah dulu, reasoning mahal belakangan)
  ↓
VERIFY (Stop condition saat kriteria acceptance terpenuhi)
  ↓
LEARN (Feedback -> Evaluasi -> Test -> Update)
```

## 3. 10 ATURAN EKSEKUSI
1. **Klasifikasikan Kompleksitas:**
   - `FAST`: Tugas langsung/sederhana (1 langkah).
   - `STANDARD`: Tugas rekayasa menengah (build/patch/test).
   - `DEEP`: Tugas arsitektur bercabang / multi-agent.
2. **Konteks Selektif:** `intent` → `pilih agen` → `pilih skill` → `ambil knowledge relevan`.
3. **Lazy-Load Skill:** Baca metadata awal, muat teks lengkap hanya jika skill terpilih.
4. **Context Budget:** Batasi alokasi token per komponen (task, skill, memory, knowledge, history).
5. **Pisahkan Retrieval vs Thinking:** Gunakan ripgrep/grep/curl murah di awal, simpan reasoning untuk sintesis.
6. **Minimum Necessary Agent:** Jangan spawn armada jika 1 proses cukup.
7. **Relevance Memory:** Hindari memasukkan seluruh vault; panggil hanya potongan relevan.
8. **Context Gatekeeper:** Cek kebutuhan sebelum memanggil tool (perlu skill? memory? research? reasoning?).
9. **Hard Stop Condition:** Berhenti berpikir saat kriteria verifikasi terpenuhi. Dilarang over-analyzing.
10. **Belajar Berbasis Bukti:** Tambah aturan hanya setelah kegagalan terbukti dan teruji, bukan menumpuk spekulasi.
