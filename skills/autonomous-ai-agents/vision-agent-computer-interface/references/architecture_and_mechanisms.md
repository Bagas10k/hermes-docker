# Vision-Language Agent-Computer Interface (ACI) & Hybrid Grounding Reference

## 1. Latar Belakang & Problem Formulation

Dalam evolusi agen otonom, antarmuka interaksi GUI (Graphical User Interface) menghadapi dikotomi:
1. **Pendekatan Murni DOM/Selector:** Cepat dan hemat bandwidth token, namun rapuh terhadap class names acak dinamis (CSS-in-JS, Tailwind minified, shadow DOM) dan buta terhadap elemen berbasis `<canvas>` atau WebGL.
2. **Pendekatan Murni Visi/Piksel (Computer Use murni):** Kebal terhadap obfuscation kode HTML, namun lambat (latensi inferensi model VLM 3–10 detik per aksi), rentan halusinasi koordinat saat elemen berdekatan, dan memboroskan token context window.

**Solusi: Hybrid Grounding ACI.**
Menggabungkan kecepatan struktur semantik Accessibility Tree (AXTree) dengan validasi spasial visual (VLM bounding box detection).

---

## 2. Sintesis Tiga Mindset Problem Solving

### A. Lensa Mekanistik-Kausal (Mechanism & Bounds)
Sistem memodelkan aksi sebagai fungsi pemetaan:
$$A_t = f(S_t^{\text{AX}}, I_t^{\text{Vis}}, \mathcal{G}) + \epsilon$$

Di mana:
- $S_t^{\text{AX}}$ adalah snapshot pohon aksesibilitas terstruktur.
- $I_t^{\text{Vis}}$ adalah tangkapan layar bitmap resolusi $W \times H$.
- $\mathcal{G}$ adalah intent tujuan pengguna (e.g., *"Klik tombol submit order"*).

**Batas Teoretis Kecepatan (Hukum Amdahl):**
Jika inferensi VLM memakan waktu $T_{\text{VLM}} \approx 2500\text{ms}$ dan parsing AXTree memakan waktu $T_{\text{AX}} \approx 15\text{ms}$, maka mengeksekusi filter AXTree terlebih dahulu memangkas pencarian ruang visual dari seluruh layar $1920 \times 1080$ menjadi bounding crop kecil $200 \times 100$, mereduksi ukuran patch visual hingga $98.9\%$ dan menekan waktu inferensi VLM ke $<400\text{ms}$.

### B. Lensa Bayesian-Eksperimental (Evidence & Belief Updating)
Pembaruan keyakinan target klik:
$$P(\text{Target} = e \mid E_{\text{sem}}, E_{\text{spat}}) \propto P(E_{\text{spat}} \mid \text{Target} = e) \cdot P(E_{\text{sem}} \mid \text{Target} = e) \cdot P(\text{Prior}(e))$$

- **Prior:** Node dengan peran interaktif (`role="button"`, `role="link"`) memiliki prior $P \approx 0.70$ dibanding elemen statis ($P \approx 0.10$).
- **Evidence 1 ($E_{\text{sem}}$):** Kecocokan token intent semantik pada atribut `name` / `aria-label`.
- **Evidence 2 ($E_{\text{spat}}$):** Jarak Euclidean pusat kotak visual dan tumpang-tindih IoU:
  $$\text{IoU}(B_{\text{AX}}, B_{\text{Vis}}) = \frac{\text{Area}(B_{\text{AX}} \cap B_{\text{Vis}})}{\text{Area}(B_{\text{AX}} \cup B_{\text{Vis}})}$$
- **Veto Barrier:** Jika $\text{IoU} < 0.20$ meskipun teks cocok, curigai elemen tertutup (*occluded*) atau elemen bayangan tak terlihat (*invisible ghost DOM*).

### C. Lensa Desain Sistem & Optimasi
- **Optimasi Terkendala Keras:**
  $$\arg\min_{\text{Action}} \text{Latency} \quad \text{s.t.} \quad P(\text{Miss-Click}) \le 0.01$$
- **Fail-Closed Fallback Hierarchy:**
  1. *Tier 1 (Hybrid Match, Confidence $\ge 0.85$):* Eksekusi klik langsung sub-detik.
  2. *Tier 2 (Ambiguous Match, $0.50 \le \text{Confidence} < 0.85$):* Lakukan visual crop setempat dan minta second-opinion VLM cepat.
  3. *Tier 3 (Low Confidence $< 0.50$):* Hindari klik membabi buta; lakukan scroll penyesuaian atau beralih ke navigasi keyboard tab/shortcut.

---

## 3. Spesifikasi Arsitektur Aksi Sub-Detik

```
[User Goal / Intent]
         │
         ├───► [CDP Accessibility Tree Snapshot] ───► [Fast Semantic Pre-Filter] (10ms)
         │                                                      │
         └───► [Viewport Screenshot Frame]                      ▼
                      │                         [Candidate Regions of Interest (ROI)]
                      ▼                                         │
             [Visual Object Detector] ◄─────────────────────────┘
                      │
                      ▼
         [Hybrid Spatial Correlation Engine]
            - Euclidean Center Distance
            - Bounding Box IoU
            - Role Affordance Score
                      │
                      ▼
            [Confidence Evaluation Gate]
            ├─ >= 0.85  ──► [Verified Physical Click (x, y)] (Sub-second)
            ├─ 0.50-0.84 ─► [Local ROI Zoom & VLM Refinement]
            └─ < 0.50   ──► [Scroll / Fallback Replanning]
```

## 4. Evaluasi Invarian & Keamanan

1. **Anti-Drift Guard:** Snapshot koordinat divalidasi tidak bergerak melebihi $\pm 2\text{px}$ dalam 3 frame rendering rAF berturut-turut untuk mencegah klik pada elemen bergerak.
2. **Retina Display Normalizer:**
   $$x_{\text{phys}} = x_{\text{CSS}} \times \text{devicePixelRatio}$$
   $$y_{\text{phys}} = y_{\text{CSS}} \times \text{devicePixelRatio}$$
3. **Post-Action State Verification:** Setelah klik dikirim, delta frame buffer dievaluasi untuk memastikan event mendarat (adanya perubahan DOM atau transisi visual).
