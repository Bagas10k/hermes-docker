#!/usr/bin/env python3
"""Gerbang gabung deterministik untuk armada sub-agent paralel.

Memeriksa 6 pilar sebelum sebuah cabang boleh digabung ke inti:
  1. Uji lulus (exit code)
  2. Tidak ada kebocoran kredensial
  3. Kepatuhan lingkup berkas
  4. Berkas target wajib benar-benar diubah
  5. Tidak ada bentrok antar-pekerja (kepemilikan)
  6. Tidak ada pergeseran kontrak antarmuka (bentrok semantik)

Jalankan mandiri untuk uji invarian:  python3 gerbang_gabung.py
Dipakai sebagai pustaka:            from gerbang_gabung import periksa_gerbang_gabung
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

POLA_KREDENSIAL = [
    re.compile(r"(?i)(api[_-]?key|secret|password|bearer|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
]

# Berkas bersama: tempat semua pekerja bertemu. Daftar mencakup nama Inggris dan Indonesia,
# karena proyek ini memakai keduanya (rute/route, indeks/index, konfigurasi/config, migrasi).
BERKAS_BERSAMA = re.compile(
    r"(^|/)("
    r"routes?|router|rute|jalur|"
    r"index|indeks|"
    r"__init__|modul|module|"
    r"config|konfigurasi|settings|pengaturan|"
    r"migrasi|migration|"
    r"changelog|readme|package|paket|composer|requirements|persyaratan"
    r")[^/]*\.(js|ts|tsx|jsx|mjs|cjs|py|php|rb|go|java|rs|json|ya?ml|toml|ini|md|txt)$",
    re.IGNORECASE,
)


@dataclass
class HasilVerifikasi:
    lulus: bool
    temuan_gerbang: list[str] = field(default_factory=list)


# --- Kepemilikan berkas: satu berkas = satu penulis ---

def muat_kepemilikan(path: str | Path) -> dict[str, str]:
    """Baca manifest kepemilikan (`.fleet/kepemilikan.json`): {"berkas": "nama_pekerja"}."""
    p = Path(path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {str(k): str(v) for k, v in (data.get("berkas", data) or {}).items()}


def periksa_kepemilikan(berkas_diubah, kepemilikan: dict[str, str], penulis: str) -> list[str]:
    """Pilar 5: setiap berkas wajib dimiliki tepat satu penulis, dan penulisnya benar.

    Berkas bersama (rute, indeks, konfigurasi) hanya boleh dimiliki induk.
    """
    temuan: list[str] = []
    for berkas in berkas_diubah:
        pemilik = kepemilikan.get(berkas)
        if pemilik is None:
            temuan.append(f"Berkas tanpa pemilik terdaftar: {berkas}")
            continue
        if pemilik != penulis:
            temuan.append(f"Bentrok kepemilikan: {berkas} dimiliki {pemilik}, bukan {penulis}")
        if BERKAS_BERSAMA.search(berkas) and pemilik != "induk":
            temuan.append(f"Berkas bersama wajib ditulis induk: {berkas} (pemilik: {pemilik})")
    return temuan


# --- Kontrak antarmuka: penangkap bentrok semantik ---

def sidik_kontrak(kontrak: dict[str, str]) -> str:
    """Sidik isi kontrak antarmuka; berubahnya sidik = ada pihak yang mengubah kesepakatan."""
    kanonik = json.dumps(kontrak, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(kanonik.encode("utf-8")).hexdigest()


def periksa_kontrak(sidik_sebelum: str, kontrak_sekarang: dict[str, str],
                    diubah_oleh: str, id_kontrak: str) -> list[str]:
    """Pilar 6: bila sidik kontrak berubah, perubahan itu wajib tercatat sebagai keputusan.

    Git tidak menangkap bentrok semantik: dua pekerja mengubah berkas berbeda,
    masing-masing benar sendiri, tetapi bentuk data di antaranya berubah. Yang
    mendeteksinya hanyalah perbandingan sidik kontrak.
    """
    sidik_kini = sidik_kontrak(kontrak_sekarang)
    if sidik_kini == sidik_sebelum:
        return []
    return [
        f"Kontrak {id_kontrak} berubah (sidik {sidik_sebelum[:12]} -> {sidik_kini[:12]}) "
        f"oleh {diubah_oleh}; wajib tercatat di KEPUTUSAN.md sebelum digabung"
    ]


# --- Gerbang utama ---

def periksa_gerbang_gabung(
    berkas_diubah: list[str],
    lingkup_berkas: set[str],
    berkas_target_wajib: set[str],
    kode_keluar_uji: int,
    konten_berkas_map: dict[str, str],
    berkas_pekerja_lain: set[str],
    ada_konflik_git: bool,
    kepemilikan: dict[str, str] | None = None,
    penulis: str = "",
    sidik_kontrak_sebelum: str | None = None,
    kontrak_sekarang: dict[str, str] | None = None,
    id_kontrak: str = "",
) -> HasilVerifikasi:
    temuan: list[str] = []

    # Pilar 1: uji
    if kode_keluar_uji != 0:
        temuan.append(f"Uji unit gagal dengan status kode keluar: {kode_keluar_uji}")
    if ada_konflik_git:
        temuan.append("Konflik git terdeteksi terhadap cabang inti")

    # Pilar 4: berkas target wajib
    for target in berkas_target_wajib:
        if target not in berkas_diubah:
            temuan.append(f"Berkas target wajib belum diubah: {target}")

    for berkas in berkas_diubah:
        # Pilar 3: lingkup
        if berkas not in lingkup_berkas:
            temuan.append(f"Pelanggaran lingkup modifikasi: {berkas} di luar kontrak")
        # Pilar 5: bentrok antar-pekerja
        if berkas in berkas_pekerja_lain:
            temuan.append(f"Konflik antar-pekerja: {berkas} sedang dimodifikasi pekerja lain")
        # Pilar 2: kredensial
        konten = konten_berkas_map.get(berkas, "")
        for pola in POLA_KREDENSIAL:
            if pola.search(konten):
                temuan.append(f"Kebocoran kredensial rahasia terdeteksi di {berkas}")

    # Pilar 5: kepemilikan (bila manifest tersedia)
    if kepemilikan:
        temuan.extend(periksa_kepemilikan(berkas_diubah, kepemilikan, penulis))

    # Pilar 6: pergeseran kontrak (bentrok semantik)
    if sidik_kontrak_sebelum is not None and kontrak_sekarang is not None:
        temuan.extend(periksa_kontrak(sidik_kontrak_sebelum, kontrak_sekarang,
                                      penulis or "?", id_kontrak))

    return HasilVerifikasi(lulus=len(temuan) == 0, temuan_gerbang=temuan)


# --- Uji invarian (jalankan berkas ini langsung) ---

def _uji() -> None:
    KEPEMILIKAN = {"app.py": "pekerja-a", "rute.py": "induk", "kunci.py": "pekerja-a"}

    # Jalur bahagia
    r = periksa_gerbang_gabung(["app.py"], {"app.py"}, {"app.py"}, 0, {"app.py": "x = 1"},
                               set(), False, KEPEMILIKAN, "pekerja-a")
    assert r.lulus, r.temuan_gerbang

    # Pilar 1: uji gagal
    r = periksa_gerbang_gabung(["app.py"], {"app.py"}, {"app.py"}, 1, {}, set(), False)
    assert not r.lulus and "kode keluar: 1" in r.temuan_gerbang[0], r

    # Pilar 2: kredensial
    r = periksa_gerbang_gabung(["kunci.py"], {"kunci.py"}, set(), 0,
                               {"kunci.py": "api_key = 'abcdef123456'"}, set(), False)
    assert not r.lulus and any("Kebocoran" in t for t in r.temuan_gerbang), r

    # Pilar 3: di luar lingkup
    r = periksa_gerbang_gabung(["rahasia.py"], {"app.py"}, set(), 0, {}, set(), False)
    assert not r.lulus and any("Pelanggaran lingkup" in t for t in r.temuan_gerbang), r

    # Pilar 4: target wajib tidak diubah
    r = periksa_gerbang_gabung(["app.py"], {"app.py"}, {"wajib.py"}, 0, {}, set(), False)
    assert not r.lulus and any("wajib belum diubah" in t for t in r.temuan_gerbang), r

    # Pilar 5: bentrok antar-pekerja
    r = periksa_gerbang_gabung(["app.py"], {"app.py"}, set(), 0, {}, {"app.py"}, False)
    assert not r.lulus and any("Konflik antar-pekerja" in t for t in r.temuan_gerbang), r

    # Pilar 5: berkas tanpa pemilik
    r = periksa_gerbang_gabung(["baru.py"], {"baru.py"}, set(), 0, {}, set(), False,
                               KEPEMILIKAN, "pekerja-a")
    assert not r.lulus and any("tanpa pemilik" in t for t in r.temuan_gerbang), r

    # Pilar 5: menulis berkas milik pekerja lain
    r = periksa_gerbang_gabung(["app.py"], {"app.py"}, set(), 0, {}, set(), False,
                               KEPEMILIKAN, "pekerja-b")
    assert not r.lulus and any("Bentrok kepemilikan" in t for t in r.temuan_gerbang), r

    # Pilar 5: pekerja menulis berkas bersama
    r = periksa_gerbang_gabung(["rute.py"], {"rute.py"}, set(), 0, {}, set(), False,
                               {"rute.py": "pekerja-a"}, "pekerja-a")
    assert not r.lulus and any("Berkas bersama wajib ditulis induk" in t for t in r.temuan_gerbang), r

    # Pilar 6: kontrak tidak berubah -> lolos
    k = {"kirimPesanan": "{id_pesanan:int} -> {status:str}"}
    r = periksa_gerbang_gabung(["app.py"], {"app.py"}, set(), 0, {}, set(), False,
                               None, "", sidik_kontrak(k), dict(k), "K-01")
    assert r.lulus, r.temuan_gerbang

    # Pilar 6: kontrak berubah -> ditolak (bentrok semantik yang tidak terlihat git)
    k2 = {"kirimPesanan": "{id_pesanan:str} -> {status:int}"}
    r = periksa_gerbang_gabung(["app.py"], {"app.py"}, set(), 0, {}, set(), False,
                               None, "pekerja-a", sidik_kontrak(k), k2, "K-01")
    assert not r.lulus and any("Kontrak K-01 berubah" in t for t in r.temuan_gerbang), r

    print("LULUS: 11 uji invarian gerbang lolos.")


if __name__ == "__main__":
    _uji()
