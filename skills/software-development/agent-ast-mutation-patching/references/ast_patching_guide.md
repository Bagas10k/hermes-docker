# AST Mutation & Structural Patching Reference

## 1. Mekanisme & Teori Kompilasi
Perbaikan kode berbasis string/regex konvensional (`patch` atau `sed`) memiliki tingkat kegagalan tinggi pada modifikasi struktural karena:
1. Sensitivitas spasi, lekukan (indentasi), dan newline.
2. Ambiguitas pola string ketika nama variabel/fungsi digunakan di banyak tempat.
3. Ketiadaan jaminan sintaksis (syntactic guarantees) saat modifikasi selesai.

Manipulasi Abstract Syntax Tree (AST) membedah kode sumber menjadi representasi pohon terstruktur:
$$T = (V, E)$$
di mana setiap node $v \in V$ mewakili konstruksi gramatikal formal (misalnya `FunctionDef`, `If`, `Call`, `Return`).
Transformasi kode dilakukan melalui pemetaan pohon:
$$	au: T 	o T'$$
yang menjamin pelestarian struktur hirarki dan semantik program.

## 2. Invarian Statis Pra-Commit
Setiap transformasi AST wajib melewati 3 gerbang verifikasi bertingkat:
1. **Structural Well-Formedness**: Seluruh atribut wajib (`lineno`, `col_offset`, `ctx`) terdefinisi via `ast.fix_missing_locations`.
2. **Grammar Compilation Gate**: Kode hasil unparse wajib berhasil dikompilasi oleh interpreter (`compile(tree, '<ast>', 'exec')`).
3. **Behavioral Equivalence / Target Scoping**: Verifikasi bahwa mutasi hanya menyentuh node target (bounded blast radius), dibuktikan dengan kalkulasi diff linier.

## 3. Batas Matematis & Keuntungan Amdahl
Dibandingkan dengan siklus LLM re-prompting konvensional (mengirim ulang seluruh berkas 500-1000 baris untuk perbaikan 2 baris):
- Reduksi Token: $90-95\%$ penghematan token karena LLM hanya menghasilkan node sintaksis target (bukan file utuh).
- Latensi Eksekusi: Manipulasi AST Python/Babel berjalan dalam $O(N)$ waktu lintasan pohon ($<5	ext{ms}$), memotong latency turnaround hingga $99\%$.
