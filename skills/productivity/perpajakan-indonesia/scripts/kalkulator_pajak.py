#!/usr/bin/env python3
"""
Kalkulator Pajak Usaha Indonesia (UU HPP, PP 55/2022, PP 58/2023, PMK 168/2023).
Menggunakan pustaka standar Python dan presisi Decimal.
"""

import sys
import argparse
from decimal import Decimal, ROUND_HALF_UP

def round_idr(val: Decimal) -> Decimal:
    return val.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

# PTKP 2024 / UU HPP
PTKP_MAP = {
    "TK/0": Decimal("54000000"),
    "TK/1": Decimal("58500000"),
    "TK/2": Decimal("63000000"),
    "TK/3": Decimal("67500000"),
    "K/0": Decimal("58500000"),
    "K/1": Decimal("63000000"),
    "K/2": Decimal("67500000"),
    "K/3": Decimal("72000000"),
}

def hitung_tarif_pasal17(pkp: Decimal) -> Decimal:
    if pkp <= Decimal("0"):
        return Decimal("0")
    
    tier1 = Decimal("60000000")
    tier2 = Decimal("250000000")
    tier3 = Decimal("500000000")
    tier4 = Decimal("5000000000")
    
    pajak = Decimal("0")
    sisa = pkp
    
    # Lapisan 1: 5% s.d. 60 juta
    b1 = min(sisa, tier1)
    pajak += b1 * Decimal("0.05")
    sisa -= b1
    if sisa <= Decimal("0"):
        return round_idr(pajak)
        
    # Lapisan 2: 15% > 60 juta s.d. 250 juta (lebar 190 juta)
    b2 = min(sisa, tier2 - tier1)
    pajak += b2 * Decimal("0.15")
    sisa -= b2
    if sisa <= Decimal("0"):
        return round_idr(pajak)
        
    # Lapisan 3: 25% > 250 juta s.d. 500 juta (lebar 250 juta)
    b3 = min(sisa, tier3 - tier2)
    pajak += b3 * Decimal("0.25")
    sisa -= b3
    if sisa <= Decimal("0"):
        return round_idr(pajak)
        
    # Lapisan 4: 30% > 500 juta s.d. 5 miliar (lebar 4.5 miliar)
    b4 = min(sisa, tier4 - tier3)
    pajak += b4 * Decimal("0.30")
    sisa -= b4
    if sisa <= Decimal("0"):
        return round_idr(pajak)
        
    # Lapisan 5: 35% > 5 miliar
    pajak += sisa * Decimal("0.35")
    return round_idr(pajak)

def hitung_pph_umkm(omzet: Decimal, tipe: str = "badan", akumulasi_sebelumnya: Decimal = Decimal("0")) -> dict:
    tarif = Decimal("0.005")
    threshold_op = Decimal("500000000")
    
    if tipe.lower() == "op":
        total_kumulatif = akumulasi_sebelumnya + omzet
        if total_kumulatif <= threshold_op:
            dpp = Decimal("0")
            pajak = Decimal("0")
        elif akumulasi_sebelumnya < threshold_op and total_kumulatif > threshold_op:
            dpp = total_kumulatif - threshold_op
            pajak = round_idr(dpp * tarif)
        else:
            dpp = omzet
            pajak = round_idr(dpp * tarif)
    else:
        dpp = omzet
        pajak = round_idr(dpp * tarif)
        
    return {
        "tipe": tipe.upper(),
        "omzet_bulan_ini": str(omzet),
        "akumulasi_omzet_sebelumnya": str(akumulasi_sebelumnya),
        "dpp_dikenai_pajak": str(dpp),
        "tarif": "0.5%",
        "pph_terutang": str(pajak)
    }

def get_ter_kategori_a(bruto: Decimal) -> Decimal:
    brackets = [
        (Decimal("5400000"), Decimal("0.0000")),
        (Decimal("5650000"), Decimal("0.0025")),
        (Decimal("5950000"), Decimal("0.0050")),
        (Decimal("6300000"), Decimal("0.0075")),
        (Decimal("6750000"), Decimal("0.0100")),
        (Decimal("7500000"), Decimal("0.0125")),
        (Decimal("8550000"), Decimal("0.0150")),
        (Decimal("9650000"), Decimal("0.0175")),
        (Decimal("10050000"), Decimal("0.0200")),
        (Decimal("10350000"), Decimal("0.0225")),
        (Decimal("10700000"), Decimal("0.0250")),
        (Decimal("11050000"), Decimal("0.0300")),
        (Decimal("11600000"), Decimal("0.0350")),
        (Decimal("12500000"), Decimal("0.0400")),
        (Decimal("13750000"), Decimal("0.0500")),
        (Decimal("15100000"), Decimal("0.0600")),
        (Decimal("16950000"), Decimal("0.0700")),
        (Decimal("19750000"), Decimal("0.0800")),
        (Decimal("24100000"), Decimal("0.0900")),
        (Decimal("26450000"), Decimal("0.1000")),
        (Decimal("28000000"), Decimal("0.1100")),
        (Decimal("30050000"), Decimal("0.1200")),
        (Decimal("32400000"), Decimal("0.1300")),
        (Decimal("35400000"), Decimal("0.1400")),
        (Decimal("39100000"), Decimal("0.1500")),
        (Decimal("43850000"), Decimal("0.1600")),
        (Decimal("47800000"), Decimal("0.1700")),
        (Decimal("51400000"), Decimal("0.1800")),
        (Decimal("56300000"), Decimal("0.1900")),
        (Decimal("62200000"), Decimal("0.2000")),
        (Decimal("68600000"), Decimal("0.2100")),
        (Decimal("77500000"), Decimal("0.2200")),
        (Decimal("89000000"), Decimal("0.2300")),
        (Decimal("103000000"), Decimal("0.2400")),
        (Decimal("125000000"), Decimal("0.2500")),
        (Decimal("157000000"), Decimal("0.2600")),
        (Decimal("206000000"), Decimal("0.2700")),
        (Decimal("337000000"), Decimal("0.2800")),
        (Decimal("454000000"), Decimal("0.2900")),
        (Decimal("550000000"), Decimal("0.3000")),
        (Decimal("695000000"), Decimal("0.3100")),
        (Decimal("910000000"), Decimal("0.3200")),
        (Decimal("1400000000"), Decimal("0.3300")),
    ]
    for limit, rate in brackets:
        if bruto <= limit:
            return rate
    return Decimal("0.3400")

def get_ter_kategori_b(bruto: Decimal) -> Decimal:
    brackets = [
        (Decimal("6200000"), Decimal("0.0000")),
        (Decimal("6500000"), Decimal("0.0025")),
        (Decimal("6850000"), Decimal("0.0050")),
        (Decimal("7300000"), Decimal("0.0075")),
        (Decimal("9200000"), Decimal("0.0100")),
        (Decimal("10750000"), Decimal("0.0150")),
        (Decimal("12550000"), Decimal("0.0200")),
        (Decimal("14300000"), Decimal("0.0300")),
        (Decimal("16000000"), Decimal("0.0400")),
        (Decimal("18000000"), Decimal("0.0500")),
        (Decimal("20500000"), Decimal("0.0600")),
        (Decimal("23000000"), Decimal("0.0700")),
        (Decimal("26000000"), Decimal("0.0800")),
        (Decimal("29000000"), Decimal("0.0900")),
        (Decimal("32000000"), Decimal("0.1000")),
        (Decimal("35000000"), Decimal("0.1100")),
        (Decimal("38000000"), Decimal("0.1200")),
        (Decimal("41000000"), Decimal("0.1300")),
        (Decimal("44000000"), Decimal("0.1400")),
        (Decimal("47000000"), Decimal("0.1500")),
        (Decimal("51000000"), Decimal("0.1600")),
        (Decimal("55000000"), Decimal("0.1700")),
        (Decimal("60000000"), Decimal("0.1800")),
        (Decimal("66000000"), Decimal("0.1900")),
        (Decimal("73000000"), Decimal("0.2000")),
        (Decimal("82000000"), Decimal("0.2100")),
        (Decimal("93000000"), Decimal("0.2200")),
        (Decimal("107000000"), Decimal("0.2300")),
        (Decimal("126000000"), Decimal("0.2400")),
        (Decimal("153000000"), Decimal("0.2500")),
        (Decimal("194000000"), Decimal("0.2600")),
        (Decimal("263000000"), Decimal("0.2700")),
        (Decimal("387000000"), Decimal("0.2800")),
        (Decimal("504000000"), Decimal("0.2900")),
        (Decimal("600000000"), Decimal("0.3000")),
        (Decimal("750000000"), Decimal("0.3100")),
        (Decimal("975000000"), Decimal("0.3200")),
        (Decimal("1450000000"), Decimal("0.3300")),
    ]
    for limit, rate in brackets:
        if bruto <= limit:
            return rate
    return Decimal("0.3400")

def get_ter_kategori_c(bruto: Decimal) -> Decimal:
    brackets = [
        (Decimal("6600000"), Decimal("0.0000")),
        (Decimal("6950000"), Decimal("0.0025")),
        (Decimal("7350000"), Decimal("0.0050")),
        (Decimal("7800000"), Decimal("0.0075")),
        (Decimal("8850000"), Decimal("0.0100")),
        (Decimal("9800000"), Decimal("0.0125")),
        (Decimal("10950000"), Decimal("0.0150")),
        (Decimal("11200000"), Decimal("0.0175")),
        (Decimal("12050000"), Decimal("0.0200")),
        (Decimal("12950000"), Decimal("0.0300")),
        (Decimal("14150000"), Decimal("0.0400")),
        (Decimal("15550000"), Decimal("0.0500")),
        (Decimal("17050000"), Decimal("0.0600")),
        (Decimal("19500000"), Decimal("0.0700")),
        (Decimal("22700000"), Decimal("0.0800")),
        (Decimal("25900000"), Decimal("0.0900")),
        (Decimal("28100000"), Decimal("0.1000")),
        (Decimal("30400000"), Decimal("0.1100")),
        (Decimal("33000000"), Decimal("0.1200")),
        (Decimal("36000000"), Decimal("0.1300")),
        (Decimal("39100000"), Decimal("0.1400")),
        (Decimal("43850000"), Decimal("0.1500")),
        (Decimal("47800000"), Decimal("0.1600")),
        (Decimal("51400000"), Decimal("0.1700")),
        (Decimal("56300000"), Decimal("0.1800")),
        (Decimal("62200000"), Decimal("0.1900")),
        (Decimal("68600000"), Decimal("0.2000")),
        (Decimal("77500000"), Decimal("0.2100")),
        (Decimal("89000000"), Decimal("0.2200")),
        (Decimal("103000000"), Decimal("0.2300")),
        (Decimal("125000000"), Decimal("0.2400")),
        (Decimal("157000000"), Decimal("0.2500")),
        (Decimal("206000000"), Decimal("0.2600")),
        (Decimal("337000000"), Decimal("0.2700")),
        (Decimal("454000000"), Decimal("0.2800")),
        (Decimal("550000000"), Decimal("0.2900")),
        (Decimal("695000000"), Decimal("0.3000")),
        (Decimal("910000000"), Decimal("0.3100")),
        (Decimal("1400000000"), Decimal("0.3200")),
    ]
    for limit, rate in brackets:
        if bruto <= limit:
            return rate
    return Decimal("0.3400")

def hitung_pph_21_ter(bruto: Decimal, kategori: str = "A") -> dict:
    kat = kategori.upper()
    if kat == "A":
        rate = get_ter_kategori_a(bruto)
    elif kat == "B":
        rate = get_ter_kategori_b(bruto)
    elif kat == "C":
        rate = get_ter_kategori_c(bruto)
    else:
        raise ValueError("Kategori TER harus A, B, atau C")
        
    pajak = round_idr(bruto * rate)
    return {
        "penghasilan_bruto": str(bruto),
        "kategori_ter": kat,
        "tarif_ter": f"{rate * 100}%",
        "pph_21_terutang": str(pajak)
    }

def hitung_pph_21_tahunan(bruto_setahun: Decimal, ptkp_kode: str = "TK/0", iuran_pensiun: Decimal = Decimal("0"), terpotong_jan_nov: Decimal = Decimal("0")) -> dict:
    ptkp = PTKP_MAP.get(ptkp_kode.upper(), Decimal("54000000"))
    
    # Biaya jabatan 5% maks 6.000.000 setahun
    biaya_jabatan = min(round_idr(bruto_setahun * Decimal("0.05")), Decimal("6000000"))
    neto_setahun = bruto_setahun - biaya_jabatan - iuran_pensiun
    pkp = max(Decimal("0"), neto_setahun - ptkp)
    pajak_setahun = hitung_tarif_pasal17(pkp)
    pph_desember = pajak_setahun - terpotong_jan_nov
    
    return {
        "bruto_setahun": str(bruto_setahun),
        "biaya_jabatan": str(biaya_jabatan),
        "iuran_pensiun": str(iuran_pensiun),
        "neto_setahun": str(neto_setahun),
        "ptkp_kode": ptkp_kode.upper(),
        "ptkp_nominal": str(ptkp),
        "penghasilan_kena_pajak": str(pkp),
        "pph_21_setahun": str(pajak_setahun),
        "terpotong_jan_nov": str(terpotong_jan_nov),
        "pph_21_masa_desember": str(pph_desember)
    }

def hitung_pph_21_ahli(bruto: Decimal, akumulasi_dpp_lalu: Decimal = Decimal("0")) -> dict:
    dpp = round_idr(bruto * Decimal("0.50"))
    total_dpp_kumulatif = akumulasi_dpp_lalu + dpp
    
    pajak_kumulatif = hitung_tarif_pasal17(total_dpp_kumulatif)
    pajak_lalu = hitung_tarif_pasal17(akumulasi_dpp_lalu)
    pajak_transaksi_ini = pajak_kumulatif - pajak_lalu
    
    return {
        "penghasilan_bruto": str(bruto),
        "dasar_pengenaan_pajak_50persen": str(dpp),
        "akumulasi_dpp_sebelumnya": str(akumulasi_dpp_lalu),
        "total_dpp_kumulatif": str(total_dpp_kumulatif),
        "pph_21_dipotong": str(pajak_transaksi_ini),
        "sisa_dibayarkan": str(bruto - pajak_transaksi_ini)
    }

def hitung_pph_23(nilai: Decimal, jenis: str = "jasa", punya_npwp: bool = True) -> dict:
    jenis_map = {
        "jasa": Decimal("0.02"),
        "sewa": Decimal("0.02"),
        "modal": Decimal("0.15"),
        "dividen": Decimal("0.15"),
        "bunga": Decimal("0.15"),
        "royalti": Decimal("0.15"),
    }
    base_rate = jenis_map.get(jenis.lower(), Decimal("0.02"))
    tarif = base_rate if punya_npwp else (base_rate * Decimal("2"))
    pajak = round_idr(nilai * tarif)
    
    return {
        "nilai_transaksi": str(nilai),
        "jenis_objek": jenis,
        "memiliki_npwp": punya_npwp,
        "tarif_efektif": f"{tarif * 100}%",
        "pph_23_dipotong": str(pajak),
        "sisa_dibayarkan": str(nilai - pajak)
    }

def hitung_pph_badan_pasal31e(omzet: Decimal, pkp: Decimal) -> dict:
    tarif_umum = Decimal("0.22")
    tarif_fasilitas = Decimal("0.11")
    ambang_fasilitas = Decimal("4800000000")
    batas_maks_omzet = Decimal("50000000000")
    
    if pkp <= Decimal("0"):
        return {
            "omzet_bruto": str(omzet),
            "penghasilan_kena_pajak": str(pkp),
            "skema": "Nihil (Tidak ada laba fiskal)",
            "pph_terutang": "0"
        }
        
    if omzet <= ambang_fasilitas:
        pajak = round_idr(pkp * tarif_fasilitas)
        return {
            "omzet_bruto": str(omzet),
            "penghasilan_kena_pajak": str(pkp),
            "skema": "Fasilitas Penuh 31E (Omzet <= 4.8M)",
            "tarif_efektif": "11%",
            "pph_terutang": str(pajak)
        }
    elif omzet <= batas_maks_omzet:
        pkp_fasilitas = (ambang_fasilitas / omzet) * pkp
        pkp_non_fasilitas = pkp - pkp_fasilitas
        pajak_fasilitas = pkp_fasilitas * tarif_fasilitas
        pajak_non_fasilitas = pkp_non_fasilitas * tarif_umum
        total_pajak = round_idr(pajak_fasilitas + pajak_non_fasilitas)
        return {
            "omzet_bruto": str(omzet),
            "penghasilan_kena_pajak": str(pkp),
            "skema": "Fasilitas Sebagian 31E (Omzet 4.8M s.d 50M)",
            "pkp_fasilitas": str(round_idr(pkp_fasilitas)),
            "pajak_bagian_fasilitas": str(round_idr(pajak_fasilitas)),
            "pkp_non_fasilitas": str(round_idr(pkp_non_fasilitas)),
            "pajak_bagian_non_fasilitas": str(round_idr(pajak_non_fasilitas)),
            "pph_terutang": str(total_pajak)
        }
    else:
        pajak = round_idr(pkp * tarif_umum)
        return {
            "omzet_bruto": str(omzet),
            "penghasilan_kena_pajak": str(pkp),
            "skema": "Tanpa Fasilitas (Omzet > 50M)",
            "tarif_efektif": "22%",
            "pph_terutang": str(pajak)
        }

def hitung_ppn(nilai: Decimal, termasuk_ppn: bool = False) -> dict:
    tarif = Decimal("0.11")
    if termasuk_ppn:
        dpp = round_idr((Decimal("100") / Decimal("111")) * nilai)
        ppn = round_idr((Decimal("11") / Decimal("111")) * nilai)
        total = dpp + ppn
    else:
        dpp = nilai
        ppn = round_idr(dpp * tarif)
        total = dpp + ppn
        
    return {
        "skema": "Harga Termasuk PPN (Gross-Up)" if termasuk_ppn else "Harga Belum Termasuk PPN",
        "dpp": str(dpp),
        "tarif_ppn": "11%",
        "ppn_terutang": str(ppn),
        "total_nilai": str(total)
    }

def hitung_sanksi_bunga_kup(pokok: Decimal, bunga_kmk_persen: Decimal, bulan: int) -> dict:
    # Maksimal keterlambatan 24 bulan (UU HPP)
    bulan_efektif = min(max(1, bulan), 24)
    rate = bunga_kmk_persen / Decimal("100")
    sanksi = round_idr(pokok * rate * Decimal(bulan_efektif))
    
    return {
        "pokok_pajak_kurang_bayar": str(pokok),
        "tarif_bunga_kmk_per_bulan": f"{bunga_kmk_persen}%",
        "jumlah_bulan_keterlambatan": bulan,
        "bulan_maksimal_diperhitungkan": bulan_efektif,
        "total_sanksi_bunga": str(sanksi),
        "total_wajib_dibayar": str(pokok + sanksi)
    }

def run_verify():
    # 1. PPh UMKM Badan
    res1 = hitung_pph_umkm(Decimal("10000000"), "badan")
    assert res1["pph_terutang"] == "50000", f"Test 1 Failed: {res1}"
    
    # 2. PPh UMKM OP di bawah 500 jt
    res2 = hitung_pph_umkm(Decimal("100000000"), "op", Decimal("200000000"))
    assert res2["pph_terutang"] == "0", f"Test 2 Failed: {res2}"
    
    # 3. PPh UMKM OP menembus 500 jt
    res3 = hitung_pph_umkm(Decimal("150000000"), "op", Decimal("450000000"))
    assert res3["pph_terutang"] == "500000", f"Test 3 Failed: {res3}"
    
    # 4. PPh 21 TER A
    res4 = hitung_pph_21_ter(Decimal("10000000"), "A")
    assert res4["pph_21_terutang"] == "200000", f"Test 4 Failed: {res4}"
    
    # 5. PPh 21 Tahunan (Masa Desember) TK/0 Gaji 120jt setahun
    # Bruto 120jt - Biaya Jabatan 6jt = 114jt - PTKP 54jt = PKP 60jt -> 5% x 60jt = 3.000.000
    res5 = hitung_pph_21_tahunan(Decimal("120000000"), "TK/0", Decimal("0"), Decimal("2200000"))
    assert res5["pph_21_setahun"] == "3000000", f"Test 5 Failed: {res5}"
    assert res5["pph_21_masa_desember"] == "800000", f"Test 5b Failed: {res5}"
    
    # 6. PPh 21 Tenaga Ahli (DPP 50%)
    # Bruto 40 jt -> DPP 20 jt -> 5% x 20 jt = 1.000.000
    res6 = hitung_pph_21_ahli(Decimal("40000000"), Decimal("0"))
    assert res6["pph_21_dipotong"] == "1000000", f"Test 6 Failed: {res6}"
    
    # 7. PPh 23 Jasa NPWP vs Non-NPWP
    res7_a = hitung_pph_23(Decimal("10000000"), "jasa", True)
    assert res7_a["pph_23_dipotong"] == "200000", f"Test 7a Failed: {res7_a}"
    res7_b = hitung_pph_23(Decimal("10000000"), "jasa", False)
    assert res7_b["pph_23_dipotong"] == "400000", f"Test 7b Failed: {res7_b}"
    
    # 8. PPh Badan 31E
    res8 = hitung_pph_badan_pasal31e(Decimal("2000000000"), Decimal("200000000"))
    assert res8["pph_terutang"] == "22000000", f"Test 8 Failed: {res8}"
    
    # 9. PPN 11%
    res9 = hitung_ppn(Decimal("10000000"), False)
    assert res9["ppn_terutang"] == "1100000", f"Test 9 Failed: {res9}"
    
    # 10. Sanksi Bunga KUP (Maks 24 bulan cap test)
    res10 = hitung_sanksi_bunga_kup(Decimal("10000000"), Decimal("0.60"), 30)
    # 10 jt x 0.6% x 24 bulan = 1.440.000
    assert res10["total_sanksi_bunga"] == "1440000", f"Test 10 Failed: {res10}"
    
    print("STATUS: PASSED - Seluruh modul perhitungan pajak Indonesia tervalidasi presisi desimal.")

def main():
    parser = argparse.ArgumentParser(description="Kalkulator Perpajakan Usaha Indonesia")
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcommand pphumkm
    p_umkm = subparsers.add_parser("pphumkm", help="Hitung PPh Final UMKM 0,5%% PP 55/2022")
    p_umkm.add_argument("--omzet", type=str, required=True, help="Nominal omzet bulan ini")
    p_umkm.add_argument("--tipe", type=str, default="badan", choices=["badan", "op"], help="Tipe entitas (badan/op)")
    p_umkm.add_argument("--akumulasi-sebelumnya", type=str, default="0", help="Akumulasi omzet s.d. bulan lalu")
    
    # Subcommand pph21ter
    p_21 = subparsers.add_parser("pph21ter", help="Hitung PPh 21 skema TER bulanan PP 58/2023")
    p_21.add_argument("--bruto", type=str, required=True, help="Penghasilan bruto bulanan")
    p_21.add_argument("--kategori", type=str, default="A", choices=["A", "B", "C"], help="Kategori TER (A/B/C)")
    
    # Subcommand pph21tahunan
    p_21des = subparsers.add_parser("pph21tahunan", help="Hitung PPh 21 Tahunan / Masa Desember (Pasal 17)")
    p_21des.add_argument("--bruto-setahun", type=str, required=True, help="Total penghasilan bruto setahun")
    p_21des.add_argument("--ptkp", type=str, default="TK/0", help="Kode PTKP (TK/0, K/1, dll)")
    p_21des.add_argument("--iuran-pensiun", type=str, default="0", help="Total iuran pensiun/JHT setahun dibayar karyawan")
    p_21des.add_argument("--terpotong-lalu", type=str, default="0", help="Total PPh 21 Jan-Nov yang sudah dipotong")
    
    # Subcommand pph21ahli
    p_ahli = subparsers.add_parser("pph21ahli", help="Hitung PPh 21 Tenaga Ahli / Bukan Pegawai (DPP 50%%)")
    p_ahli.add_argument("--bruto", type=str, required=True, help="Imbalan bruto transaksi ini")
    p_ahli.add_argument("--akumulasi-dpp", type=str, default="0", help="Akumulasi DPP 50%% sebelumnya tahun berjalan")
    
    # Subcommand pph23
    p_23 = subparsers.add_parser("pph23", help="Hitung PPh Pasal 23 (jasa, sewa, dividen/bunga/royalti)")
    p_23.add_argument("--nilai", type=str, required=True, help="Nilai transaksi")
    p_23.add_argument("--jenis", type=str, default="jasa", help="Jenis transaksi (jasa, sewa, modal)")
    p_23.add_argument("--tanpa-npwp", action="store_true", help="Set jika rekanan tidak memiliki NPWP")
    
    # Subcommand pphbadan
    p_badan = subparsers.add_parser("pphbadan", help="Hitung PPh Badan Fasilitas Pasal 31E UU PPh")
    p_badan.add_argument("--omzet", type=str, required=True, help="Total peredaran bruto setahun")
    p_badan.add_argument("--pkp", type=str, required=True, help="Penghasilan Kena Pajak (laba fiskal)")
    
    # Subcommand ppn
    p_ppn = subparsers.add_parser("ppn", help="Hitung PPN 11%%")
    p_ppn.add_argument("--nilai", type=str, required=True, help="Nilai transaksi")
    p_ppn.add_argument("--termasuk-ppn", action="store_true", help="Set jika nilai sudah include PPN")
    
    # Subcommand sanksikup
    p_sanksi = subparsers.add_parser("sanksikup", help="Hitung sanksi bunga administrasi KUP UU HPP")
    p_sanksi.add_argument("--pokok", type=str, required=True, help="Pokok pajak kurang bayar")
    p_sanksi.add_argument("--tarif-kmk", type=str, required=True, help="Tarif suku bunga KMK bulanan dalam persen (misal 0.58)")
    p_sanksi.add_argument("--bulan", type=int, required=True, help="Jumlah bulan keterlambatan")
    
    # Subcommand verify
    subparsers.add_parser("verify", help="Uji validasi seluruh modul")
    
    args = parser.parse_args()
    import json
    
    if args.command == "verify":
        run_verify()
    elif args.command == "pphumkm":
        res = hitung_pph_umkm(Decimal(args.omzet), args.tipe, Decimal(args.akumulasi_sebelumnya))
        print(json.dumps(res, indent=2))
    elif args.command == "pph21ter":
        res = hitung_pph_21_ter(Decimal(args.bruto), args.kategori)
        print(json.dumps(res, indent=2))
    elif args.command == "pph21tahunan":
        res = hitung_pph_21_tahunan(Decimal(args.bruto_setahun), args.ptkp, Decimal(args.iuran_pensiun), Decimal(args.terpotong_lalu))
        print(json.dumps(res, indent=2))
    elif args.command == "pph21ahli":
        res = hitung_pph_21_ahli(Decimal(args.bruto), Decimal(args.akumulasi_dpp))
        print(json.dumps(res, indent=2))
    elif args.command == "pph23":
        res = hitung_pph_23(Decimal(args.nilai), args.jenis, not args.tanpa_npwp)
        print(json.dumps(res, indent=2))
    elif args.command == "pphbadan":
        res = hitung_pph_badan_pasal31e(Decimal(args.omzet), Decimal(args.pkp))
        print(json.dumps(res, indent=2))
    elif args.command == "ppn":
        res = hitung_ppn(Decimal(args.nilai), args.termasuk_ppn)
        print(json.dumps(res, indent=2))
    elif args.command == "sanksikup":
        res = hitung_sanksi_bunga_kup(Decimal(args.pokok), Decimal(args.tarif_kmk), args.bulan)
        print(json.dumps(res, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
