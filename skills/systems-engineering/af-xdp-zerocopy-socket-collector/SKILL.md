---
name: af-xdp-zerocopy-socket-collector
description: AF_XDP zero-copy socket ingress for user-space collectors.
version: 0.1.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [af-xdp, zerocopy, umem, ring-buffer, telemetry, networking]
    related_skills: [xdp-packet-filtering-telemetry, zero-copy-ipc-and-shared-memory-ring-buffers]
---

# AF_XDP Zero-Copy Socket Ingress Collector

Skill ini menyediakan arsitektur dan pola penanganan paket jaringan performa ultra-tinggi menggunakan soket AF_XDP (XSK). Alur ini memotong overhead stack TCP/IP Linux (`sk_buff`, copy-to-user context switch, syscall `recvmsg()`) dengan mentransfer frame DMA langsung dari NIC ke memori UMEM terdaftar di ruang pengguna.

## Kapan Digunakan
- Pengumpulan telemetri jaringan berkecepatan tinggi (> 10 juta paket/detik).
- Pipeline metrik edge di mana alokasi socket buffer Linux konvensional memicu lonjakan CPU/softirq.
- Monitoring telemetri agentik terdistribusi tanpa latensi kernel stack copy.

## Arsitektur Ring Buffer & UMEM
Soket AF_XDP beroperasi dengan 4 ring buffer:
1. **UMEM (User Memory)**: Area memori virtual yang dipin (`mlock`) dan didaftarkan ke kernel.
2. **FILL Ring**: Ring produsen userspace -> konsumen kernel. Menyediakan alamat frame UMEM kosong yang siap diisi paket oleh NIC.
3. **RX Ring**: Ring produsen kernel -> konsumen userspace. Mengirimkan deskriptor paket masuk (`addr`, `len`) ke aplikasi.
4. **TX Ring & COMPLETION Ring**: Jalur transmisi nol-salin balik.

## Karakteristik & Batasan Mekanistik
- **Bypass sk_buff**: Paket tidak pernah diubah menjadi struktur `struct sk_buff` di kernel jika driver mendukung `XDP_ZEROCOPY`.
- **Power-of-Two Ring**: Ukuran ring wajib kelipatan 2 agar operasi modulo digantikan oleh operasi bitwise mask (`producer & mask`), memangkas siklus CPU.
- **Zero-Allocation Ingress**: Tidak ada malloc/free di dalam loop pemrosesan; chunk didaur ulang bolak-balik antara RX dan FILL ring.

## Script & Validasi
Model dan skrip parser telemetri tersedia di:
- Skrip: `scripts/xsk_collector.py`
- Test: `tests/test_xsk_collector.py`

Jalankan test suite deterministik:
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
