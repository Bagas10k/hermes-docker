#!/usr/bin/env python3
import argparse
import sys

def calculate_pass_at_k(n: int, c: int, k: int) -> float:
    if c == 0:
        return 0.0
    if n - c < k:
        return 1.0
    prob_failure = 1.0
    for i in range(k):
        prob_failure *= (n - c - i) / (n - i)
    return 1.0 - prob_failure

def main():
    parser = argparse.ArgumentParser(description="Kalkulator Unbiased Pass@k Chen et al.")
    parser.add_argument("-n", "--total-samples", type=int, required=True, help="Total sampel (n)")
    parser.add_argument("-c", "--correct-samples", type=int, required=True, help="Jumlah sampel benar (c)")
    parser.add_argument("-k", "--k-values", type=str, default="1,3,5,10", help="Daftar nilai k dipisah koma")
    
    args = parser.parse_args()
    n = args.total_samples
    c = args.correct_samples
    
    if c > n:
        print("Error: c tidak boleh lebih besar dari n", file=sys.stderr)
        sys.exit(1)
        
    k_list = [int(x.strip()) for x in args.k_values.split(",") if x.strip()]
    
    print(f"Total Sampel (n): {n} | Sukses (c): {c}")
    print("-" * 35)
    for k in k_list:
        if k > n:
            print(f"Pass@{k:2d}: Tidak dapat dihitung (k > n)")
        else:
            val = calculate_pass_at_k(n, c, k)
            print(f"Pass@{k:2d}: {val:.4f} ({val * 100:.2f}%)")

if __name__ == "__main__":
    main()
