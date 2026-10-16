#!/usr/bin/env python3
"""Verifikasi berkas catatan ERP: frontmatter YAML wajib, tautan wikilink tidak putus,
dan setiap catatan punya minimal satu uji invarian (fungsi ber-assert).

Jalankan: python3 verifikasi_catatan_erp.py
Keluar dengan kode 1 bila ada pelanggaran — sehingga bisa dipakai di CI.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
WAJIB_KUNCI = {"judul", "kategori", "tag", "tanggal_dibuat", "terakhir_diperbarui", "tautan_terkait"}
POLA_TAUTAN = re.compile(r"\[\[([^\]|#]+)")
POLA_FUNGSI_UJI = re.compile(r"^\s*(?:async\s+)?def (uji_\w+)\(", re.MULTILINE)

# Berkas peta/indeks tidak wajib memuat fungsi uji sendiri.
DINECUALIKAN_DARI_UJI = {"Daftar-Invarian-Mutlak-Rekayasa-ERP", "Peta-Modul-Rekayasa-ERP"}


def baca_frontmatter(teks: str) -> dict[str, str] | None:
    if not teks.startswith("---\n"):
        return None
    akhir = teks.find("\n---", 4)
    if akhir == -1:
        return None
    hasil: dict[str, str] = {}
    for baris in teks[4:akhir].splitlines():
        cocok = re.match(r"^([a-z_]+):\s*(.*)$", baris)
        if cocok:
            hasil[cocok.group(1)] = cocok.group(2).strip()
    return hasil


def main() -> int:
    import sys as _sys
    if len(_sys.argv) > 1:
        direktori = Path(_sys.argv[1]).resolve()
    else:
        # Default: folder doktrin ERP di vault; jatuh ke folder skrip bila tidak ada.
        bawaan = Path.home() / "otak-koding" / "10-Rekayasa-ERP-dan-Akuntansi-Sistem"
        direktori = bawaan if bawaan.is_dir() else Path(__file__).resolve().parent
    berkas = sorted(direktori.glob("*.md"))
    if not berkas:
        print("TIDAK ADA BERKAS .md — periksa direktori", direktori)
        return 1

    # Kumpulkan seluruh nama catatan (stem) untuk validasi tautan.
    nama_tersedia = {b.stem for b in direktori.glob("*.md")}
    # Catatan di luar folder ini yang sah dirujuk.
    luar = {
        "Indeks-Utama-Otak-Koding", "Panduan-Navigasi-dan-Standar-Catatan",
        "Arsitektur-Monolitik-vs-Mikroservis", "Clean-Architecture-dan-Hexagonal",
        "Desain-API-RESTful-dan-GraphQL", "Pola-Desain-Gang-of-Four",
        "Prinsip-Dasar-Clean-Code", "Prinsip-SOLID",
        "Mitigasi-Kafka-Consumer-Lag-Dan-Rebalance-Storm",
        "Atribusi-Hak-Cipta-Bagas-Cihuy",
    }
    sah = nama_tersedia | luar

    galat: list[str] = []
    peringatan: list[str] = []
    ringkas: list[tuple[str, int, int, int]] = []

    for b in berkas:
        teks = b.read_text(encoding="utf-8")
        fm = baca_frontmatter(teks)

        if fm is None:
            galat.append(f"{b.name}: frontmatter YAML tidak ditemukan atau tidak ditutup")
            continue

        kurang = WAJIB_KUNCI - set(fm)
        if kurang:
            galat.append(f"{b.name}: kunci frontmatter hilang: {sorted(kurang)}")

        # Tautan putus
        putus = [t for t in POLA_TAUTAN.findall(teks) if t not in sah]
        if putus:
            galat.append(f"{b.name}: tautan wikilink putus: {sorted(set(putus))}")

        # Uji invarian wajib ada (kecuali berkas peta/indeks).
        uji = POLA_FUNGSI_UJI.findall(teks)
        jumlah_assert = teks.count("assert ")
        if not uji and b.stem not in DINECUALIKAN_DARI_UJI:
            galat.append(f"{b.name}: tidak ada fungsi uji_* (uji invarian wajib ada)")
        elif uji and jumlah_assert == 0:
            galat.append(f"{b.name}: fungsi uji ada tetapi tanpa assert")

        # Dua baris penutup wajib
        if "*Skipped:" not in teks:
            peringatan.append(f"{b.name}: baris '*Skipped:' tidak ditemukan")
        if "*Add when:" not in teks:
            peringatan.append(f"{b.name}: baris '*Add when:' tidak ditemukan")

        # Panjang minimum
        baris = len(teks.splitlines())
        if baris < 100:
            peringatan.append(f"{b.name}: hanya {baris} baris (target >= 150)")

        ringkas.append((b.name, baris, len(uji), jumlah_assert))

    print(f"Diperiksa: {len(berkas)} berkas di {DIR.name}/\n")
    print(f"{'berkas':<62} {'baris':>6} {'uji':>4} {'assert':>7}")
    print("-" * 82)
    for nama, baris, uji, assert_ in ringkas:
        print(f"{nama:<62} {baris:>6} {uji:>4} {assert_:>7}")

    total_baris = sum(r[1] for r in ringkas)
    print("-" * 82)
    print(f"{'TOTAL':<62} {total_baris:>6} "
          f"{sum(r[2] for r in ringkas):>4} {sum(r[3] for r in ringkas):>7}")

    if peringatan:
        print(f"\nPERINGATAN ({len(peringatan)}):")
        for p in peringatan:
            print("  !", p)

    if galat:
        print(f"\nGALAT ({len(galat)}):")
        for g in galat:
            print("  X", g)
        return 1

    print("\nLULUS: seluruh catatan memenuhi standar doktrin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
