# Neural Knowledge Graph Verification & Triplet Extraction Architecture

## 1. Mekanistik-Kausal Triplet Extraction
Sistem mengekstrak relasi berarah $G = (V, E)$ dari trajektori operasional dan berkas markdown Obsidian.
Setiap tepi $e = (u, v, r, c)$ merepresentasikan:
- $u$: Subjek (node asal)
- $v$: Objek (node target)
- $r$: Relasi predikat (e.g. `references`, `implements`, `depends_on`, `calls`)
- $c \in [0, 1]$: Skor keyakinan empiris

### Batasan Kompleksitas & Hukum Amdahl
- Parsing teks menggunakan regex deterministik dengan bound $O(L)$ terhadap panjang token dokumen.
- Verifikasi simetri relasi beroperasi pada adjacency list berbobot dengan kompleksitas $O(|V| + |E|)$.
- Eliminasi siklus tautologis (mutual cycles) dibatasi pada depth 2 ($u 	o v 	o u$) dengan kompleksitas $O(|E| \cdot 	ext{deg}_{	ext{max}})$, mencegah ledakan komputasi $O(|V|!)$ dari algoritma enumerasi siklus bebas.

## 2. Lensa Bayesian-Eksperimental & Pengurangan Entropi
- Keyakinan awal (prior) terhadap relasi sintaksis:
  $$P(	ext{Valid} \mid 	ext{Wikilink}) = 0.95$$
  $$P(	ext{Valid} \mid 	ext{Directed Arrow}) = 0.90$$
  $$P(	ext{Valid} \mid 	ext{Technical Verb}) = 0.85$$
- Jika relasi terbukti simetris pada Obsidian vault ($A 	o B$ dan $B 	o A$), posterior probabilitas keabsahan konseptual meningkat secara Bayesian:
  $$P(	ext{ConceptLink} \mid 	ext{Bidirectional}) > 0.98$$
- Node yatim piatu (orphan nodes dengan $d_{	ext{total}} = 0$) menandakan entitas terisolasi yang belum terintegrasi ke dalam memori prosedural, memicu rekomendasi eskalasi atau penautan silang.

## 3. Desain Sistem & Sintesis 3D Force Coordinates
Visualisasi 3D Neural Graph pada portal web (`/grafik`) mengadopsi distribusi bola Fibonacci:
- Setiap node aktif ditempatkan pada sudut emas:
  $$\phi = \pi (3 - \sqrt{5})$$
  $$	heta_i = i \cdot \phi$$
  $$y_i = 1 - rac{2i}{N - 1}$$
- Radius orbit $r_i$ dikalibrasi terbalik terhadap derajat sentralitas total:
  $$r_i = R_{	ext{max}} \cdot \left(1 - lpha \cdot rac{d_{	ext{total}}(i)}{d_{	ext{max}}}ight)$$
  dengan $lpha = 0.7$, memastikan hub pengetahuan utama terkonsentrasi di dekat titik pusat koordinat $(0,0,0)$ sementara daun dan node perifer menyebar ke cangkang luar ($r \le 200$, orphan pada $r = 350$).
