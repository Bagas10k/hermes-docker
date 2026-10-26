#!/usr/bin/env python3
"""
Engine Analisis Keuangan Lanjutan & Diagnostik Bisnis (Magister Akuntansi).
Menggunakan pustaka standar Python dan presisi Decimal.
"""

import sys
import argparse
from decimal import Decimal, ROUND_HALF_UP

def round_val(val: Decimal, places: int = 4) -> Decimal:
    fmt = "0." + "0" * places if places > 0 else "1"
    return val.quantize(Decimal(fmt), rounding=ROUND_HALF_UP)

def round_curr(val: Decimal) -> Decimal:
    return val.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

def hitung_dupont5(net_income: Decimal, ebt: Decimal, ebit: Decimal, sales: Decimal, assets: Decimal, equity: Decimal) -> dict:
    if any(v <= Decimal("0") for v in [ebt, ebit, sales, assets, equity]):
        raise ValueError("Nilai EBT, EBIT, Sales, Assets, dan Equity harus bernilai positif.")
        
    tax_burden = net_income / ebt
    interest_burden = ebt / ebit
    ebit_margin = ebit / sales
    asset_turnover = sales / assets
    equity_multiplier = assets / equity
    
    roe = tax_burden * interest_burden * ebit_margin * asset_turnover * equity_multiplier
    
    return {
        "tax_burden_ratio": str(round_val(tax_burden, 4)),
        "interest_burden_ratio": str(round_val(interest_burden, 4)),
        "operating_margin_ebit": f"{round_val(ebit_margin * Decimal('100'), 2)}%",
        "asset_turnover_x": str(round_val(asset_turnover, 4)),
        "equity_multiplier_leverage": str(round_val(equity_multiplier, 4)),
        "return_on_equity_roe": f"{round_val(roe * Decimal('100'), 2)}%",
        "evaluasi": (
            "ROE sehat didukung efisiensi operasional" if ebit_margin >= Decimal("0.15") 
            else "Perhatian: Tingkat leverage utang tinggi menopang ROE" if equity_multiplier >= Decimal("2.5")
            else "Kinerja ROE moderat"
        )
    }

def hitung_altman_z(wc: Decimal, re: Decimal, ebit: Decimal, equity_bv: Decimal, total_liab: Decimal, sales: Decimal, total_assets: Decimal) -> dict:
    if total_assets <= Decimal("0") or total_liab <= Decimal("0"):
        raise ValueError("Total Aset dan Total Liabilitas harus positif.")
        
    x1 = wc / total_assets
    x2 = re / total_assets
    x3 = ebit / total_assets
    x4 = equity_bv / total_liab
    x5 = sales / total_assets
    
    # Model Manufaktur Privat Altman (1983)
    z_prime = (
        (Decimal("0.717") * x1) +
        (Decimal("0.847") * x2) +
        (Decimal("3.107") * x3) +
        (Decimal("0.420") * x4) +
        (Decimal("0.998") * x5)
    )
    z_score = round_val(z_prime, 3)
    
    if z_score > Decimal("2.90"):
        zona = "SAFE ZONE (Risiko default sangat rendah)"
    elif z_score >= Decimal("1.23"):
        zona = "GREY ZONE (Zona waspada, rentan tekanan likuiditas)"
    else:
        zona = "DISTRESS ZONE (Risiko gagal bayar / kebangkrutan tinggi)"
        
    return {
        "x1_working_capital_to_assets": str(round_val(x1, 4)),
        "x2_retained_earnings_to_assets": str(round_val(x2, 4)),
        "x3_ebit_to_assets": str(round_val(x3, 4)),
        "x4_equity_bv_to_liabilities": str(round_val(x4, 4)),
        "x5_sales_to_assets": str(round_val(x5, 4)),
        "altman_z_prime_score": str(z_score),
        "klasifikasi_risiko": zona
    }

def hitung_cvp(fixed_cost: Decimal, price: Decimal, var_cost: Decimal, actual_units: Decimal) -> dict:
    if price <= var_cost:
        raise ValueError("Harga jual per unit harus lebih besar daripada biaya variabel per unit.")
        
    cm_unit = price - var_cost
    cm_ratio = cm_unit / price
    
    bep_units = round_curr(fixed_cost / cm_unit)
    bep_sales = round_curr(fixed_cost / cm_ratio)
    
    actual_sales = actual_units * price
    actual_ebit = (actual_units * cm_unit) - fixed_cost
    
    mos_nominal = max(Decimal("0"), actual_sales - bep_sales)
    mos_ratio = (mos_nominal / actual_sales) if actual_sales > Decimal("0") else Decimal("0")
    
    dol = ((actual_units * cm_unit) / actual_ebit) if actual_ebit > Decimal("0") else None
    
    return {
        "harga_jual_unit": str(price),
        "biaya_variabel_unit": str(var_cost),
        "margin_kontribusi_unit": str(cm_unit),
        "rasio_margin_kontribusi": f"{round_val(cm_ratio * Decimal('100'), 2)}%",
        "bep_unit": str(bep_units),
        "bep_rupiah": str(bep_sales),
        "penjualan_aktual_rupiah": str(actual_sales),
        "ebit_operasional": str(actual_ebit),
        "margin_of_safety_rupiah": str(mos_nominal),
        "margin_of_safety_persen": f"{round_val(mos_ratio * Decimal('100'), 2)}%",
        "degree_of_operating_leverage_dol": str(round_val(dol, 2)) if dol is not None else "N/A (EBIT <= 0)"
    }

def hitung_ccc(dio: Decimal, dso: Decimal, dpo: Decimal) -> dict:
    ccc = dio + dso - dpo
    return {
        "days_inventory_outstanding_dio": str(dio),
        "days_sales_outstanding_dso": str(dso),
        "days_payable_outstanding_dpo": str(dpo),
        "cash_conversion_cycle_days": str(ccc),
        "evaluasi": (
            "Siklus sangat prima (Kas didanai oleh rantai pasok pemasok)" if ccc <= Decimal("0")
            else "Siklus modal kerja efisien (< 45 hari)" if ccc <= Decimal("45")
            else "Perhatian: Kas terikat lama dalam siklus operasi modal kerja"
        )
    }

def run_verify():
    # 1. Test DuPont 5-Way
    # Sales: 1 Miliar, Assets: 800 Juta, Equity: 500 Juta, EBIT: 200 Juta, EBT: 180 Juta, NI: 140 Juta
    res_dp = hitung_dupont5(
        Decimal("140000000"), Decimal("180000000"), Decimal("200000000"),
        Decimal("1000000000"), Decimal("800000000"), Decimal("500000000")
    )
    # ROE = 140/500 = 28.00%
    assert res_dp["return_on_equity_roe"] == "28.00%", f"DuPont Test Failed: {res_dp}"
    
    # 2. Test Altman Z-Score
    # Total Assets: 1 Miliar, Liab: 400 Juta, Equity: 600 Juta, WC: 200 Juta, RE: 300 Juta, EBIT: 150 Juta, Sales: 1.2 Miliar
    # X1 = 0.2, X2 = 0.3, X3 = 0.15, X4 = 600/400 = 1.5, X5 = 1.2
    # Z' = 0.717*0.2 + 0.847*0.3 + 3.107*0.15 + 0.420*1.5 + 0.998*1.2
    # Z' = 0.1434 + 0.2541 + 0.46605 + 0.63 + 1.1976 = 2.69115 -> 2.691 (Grey Zone)
    res_z = hitung_altman_z(
        Decimal("200000000"), Decimal("300000000"), Decimal("150000000"),
        Decimal("600000000"), Decimal("400000000"), Decimal("1200000000"), Decimal("1000000000")
    )
    assert res_z["altman_z_prime_score"] == "2.691", f"Altman Test Failed: {res_z}"
    assert "GREY ZONE" in res_z["klasifikasi_risiko"], f"Altman Zone Failed: {res_z}"
    
    # 3. Test CVP
    # FC: 100 jt, Price: 20.000, VC: 12.000 -> CM: 8.000 (40%)
    # BEP units: 100 jt / 8.000 = 12.500 unit. BEP Sales = 250.000.000. Actual units: 20.000 -> Sales 400 jt, EBIT: 60 jt, MoS: 150 jt (37.5%)
    res_cvp = hitung_cvp(Decimal("100000000"), Decimal("20000"), Decimal("12000"), Decimal("20000"))
    assert res_cvp["bep_unit"] == "12500", f"CVP Unit Failed: {res_cvp}"
    assert res_cvp["bep_rupiah"] == "250000000", f"CVP Sales Failed: {res_cvp}"
    assert res_cvp["ebit_operasional"] == "60000000", f"CVP EBIT Failed: {res_cvp}"
    assert res_cvp["margin_of_safety_persen"] == "37.50%", f"CVP MoS Failed: {res_cvp}"
    # DOL = (20.000 x 8.000) / 60 jt = 160 jt / 60 jt = 2.67
    assert res_cvp["degree_of_operating_leverage_dol"] == "2.67", f"CVP DOL Failed: {res_cvp}"
    
    # 4. Test CCC
    res_ccc = hitung_ccc(Decimal("45"), Decimal("30"), Decimal("40"))
    # CCC = 45 + 30 - 40 = 35 days
    assert res_ccc["cash_conversion_cycle_days"] == "35", f"CCC Failed: {res_ccc}"
    
    print("STATUS: PASSED - Semua modul engine analisis keuangan tingkat lanjut tervalidasi presisi desimal.")

def main():
    parser = argparse.ArgumentParser(description="Engine Analisis Keuangan Lanjutan (Magister Akuntansi)")
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcommand dupont5
    p_dp = subparsers.add_parser("dupont5", help="Analisis DuPont 5-Way pemecah ROE")
    p_dp.add_argument("--net-income", type=str, required=True)
    p_dp.add_argument("--ebt", type=str, required=True)
    p_dp.add_argument("--ebit", type=str, required=True)
    p_dp.add_argument("--sales", type=str, required=True)
    p_dp.add_argument("--assets", type=str, required=True)
    p_dp.add_argument("--equity", type=str, required=True)
    
    # Subcommand altmanz
    p_z = subparsers.add_parser("altmanz", help="Analisis Risiko Kebangkrutan Altman Z-Score")
    p_z.add_argument("--wc", type=str, required=True, help="Modal Kerja Bersih (Current Assets - Current Liab)")
    p_z.add_argument("--re", type=str, required=True, help="Saldo Laba Ditahan (Retained Earnings)")
    p_z.add_argument("--ebit", type=str, required=True, help="Laba Operasional (EBIT)")
    p_z.add_argument("--equity-bv", type=str, required=True, help="Nilai Buku Ekuitas")
    p_z.add_argument("--liab-total", type=str, required=True, help="Total Liabilitas")
    p_z.add_argument("--sales", type=str, required=True, help="Total Penjualan/Omzet")
    p_z.add_argument("--assets", type=str, required=True, help="Total Aset")
    
    # Subcommand cvp
    p_cvp = subparsers.add_parser("cvp", help="Analisis Cost-Volume-Profit, BEP, MoS, dan DOL")
    p_cvp.add_argument("--fixed-cost", type=str, required=True, help="Total Biaya Tetap")
    p_cvp.add_argument("--price", type=str, required=True, help="Harga Jual per Unit")
    p_cvp.add_argument("--var-cost", type=str, required=True, help="Biaya Variabel per Unit")
    p_cvp.add_argument("--actual-units", type=str, required=True, help="Volume Unit Penjualan Aktual/Target")
    
    # Subcommand ccc
    p_ccc = subparsers.add_parser("ccc", help="Siklus Konversi Kas (DIO + DSO - DPO)")
    p_ccc.add_argument("--dio", type=str, required=True, help="Days Inventory Outstanding")
    p_ccc.add_argument("--dso", type=str, required=True, help="Days Sales Outstanding")
    p_ccc.add_argument("--dpo", type=str, required=True, help="Days Payable Outstanding")
    
    # Subcommand verify
    subparsers.add_parser("verify", help="Uji validasi seluruh formula matematika")
    
    args = parser.parse_args()
    import json
    
    if args.command == "verify":
        run_verify()
    elif args.command == "dupont5":
        res = hitung_dupont5(
            Decimal(args.net_income), Decimal(args.ebt), Decimal(args.ebit),
            Decimal(args.sales), Decimal(args.assets), Decimal(args.equity)
        )
        print(json.dumps(res, indent=2))
    elif args.command == "altmanz":
        res = hitung_altman_z(
            Decimal(args.wc), Decimal(args.re), Decimal(args.ebit),
            Decimal(args.equity_bv), Decimal(args.liab_total), Decimal(args.sales), Decimal(args.assets)
        )
        print(json.dumps(res, indent=2))
    elif args.command == "cvp":
        res = hitung_cvp(
            Decimal(args.fixed_cost), Decimal(args.price),
            Decimal(args.var_cost), Decimal(args.actual_units)
        )
        print(json.dumps(res, indent=2))
    elif args.command == "ccc":
        res = hitung_ccc(Decimal(args.dio), Decimal(args.dso), Decimal(args.dpo))
        print(json.dumps(res, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
