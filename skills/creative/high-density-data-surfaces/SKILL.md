---
name: high-density-data-surfaces
description: Build high-density data surfaces & hybrid card-tables.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui-ux, data-tables, enterprise-grid, high-density, wcag-aaa, mobile-ergonomics]
    related_skills: [otak-koding, zero-layout-shift-artifacts, enterprise-ui-architecture]
---

# High-Density Accessible Data Surfaces & Hybrid Card-Tables

Skill untuk merancang dan merealisasikan matriks data enterprise berdensitas tinggi (*high-density data tables/grids*) dengan jaminan mutlak nol *horizontal blowout* pada mobile, kontras warna aksesibel WCAG AAA, dan transformasi hybrid card-table responsif.

## 1. Lensa Masalah & Invarian Mekanistik
Data grid enterprise sering mengalami dua kegagalan struktural klasik:
1. **Horizontal Blowout / Truncation Ruptures**: Pada layar mobile ($W < 640\text{px}$), tabel konvensional melebar tak terkendali memicu horizontal scrollbar atau teks terjepit tak terbaca.
2. **Kelemahan Kontras & Slop Styling**: Penggunaan teks abu-abu pucat, padding vertikal boros ($>32\text{px}$), border-radius berlebih, atau emoji sembarang yang menurunkan martabat enterprise.

### Formulasi Invarian Layout
$$\forall W_{\text{viewport}} \in [320\text{px}, 2560\text{px}], \quad W_{\text{rendered}} \le W_{\text{viewport}} \quad (\text{Overflow-X} = 0)$$

1. **Mobile Breakpoint ($W < 640\text{px}$)**:
   - Tabel bertransformasi deterministik menjadi **Hybrid Card Matrix**.
   - Kolom kunci primer ($C_{\text{primary}}$) dijadikan header kartu, metrik utama diposisikan di ringkasan, dan kolom sekunder dialirkan ke drawer/accordion detail.
2. **Desktop & Tablet Breakpoint ($W \ge 640\text{px}$)**:
   - Tabel padat (*dense-table mode*) dengan alokasi prioritas kolom $P \in [1..5]$.
   - Kolom prioritas rendah secara anggun dialihkan ke sub-baris expandable jika lebar layar tidak mencukupi, menjaga kolom prioritas 1 & 2 tetap terbaca utuh.

---

## 2. Standar Tipografi & Desain Zero-Emoji
- **Font**: *Plus Jakarta Sans* untuk teks label & header, *JetBrains Mono* (dengan `tabular-nums`) untuk angka, kode, dan nilai moneter.
- **Rata Kanan Angka**: Seluruh kolom numerik/keuangan wajib `text-right` + `tabular-nums` dengan format rupiah baku (`Rp 1.085.330.000`).
- **Zero-Emoji Policy**: Sanitasi 100% dari emoji Unicode; gunakan badge mikro monokrom atau status dot 6px terkalibrasi.
- **Tingkat Kontras WCAG AAA**:
  - Teks primer terhadap permukaan kartu: rasio kontras $\ge 12.0:1$.
  - Aksen status semantik (Emerald, Amber, Crimson): rasio kontras $\ge 4.5:1$ (AA/AAA).

---

## 3. Komponen Implementasi Cepat

### Python Layout Optimizer Engine
```bash
python3 -c "
from density_surface_engine import ColumnDefinition, SurfaceLayoutOptimizer
cols = [
    ColumnDefinition('id', 'TX ID', min_width=120, priority=1, is_primary=True),
    ColumnDefinition('client', 'Client', min_width=160, priority=2),
    ColumnDefinition('amount', 'Nominal', min_width=140, priority=1, numeric=True),
    ColumnDefinition('ip', 'IP Node', min_width=120, priority=5)
]
opt = SurfaceLayoutOptimizer(cols)
print(opt.compute_layout(375)) # Hybrid card mode
print(opt.compute_layout(1024)) # Dense table mode
"
```

### Pola CSS Grid / Table Hybrid
```css
/* Container Invariant */
.data-surface-container {
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* Dense Enterprise Row */
.dense-table-row {
  display: grid;
  align-items: center;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 13px;
  border-bottom: 1px solid var(--border-hairline);
  padding: 8px 12px;
}

.dense-table-row .numeric-cell {
  font-family: 'JetBrains Mono', monospace;
  font-variant-numeric: tabular-nums;
  text-align: right;
}

/* Mobile Hybrid Card Transformation */
@media (max-width: 639px) {
  .hybrid-card-surface {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    border-radius: 8px;
    background: var(--surface-card);
    border: 1px solid var(--border-hairline);
  }
}
```

---

## 4. Checklist Verifikasi
- [x] Invarian $W_{\text{rendered}} \le W_{\text{viewport}}$ teruji pada seluruh rentang viewport (320px - 2560px).
- [x] Audit kontras WCAG AAA lulus $\ge 12:1$ untuk teks primer.
- [x] Kolom angka menggunakan `tabular-nums` dan rata kanan.
- [x] Nol emoji Unicode pada render UI.
