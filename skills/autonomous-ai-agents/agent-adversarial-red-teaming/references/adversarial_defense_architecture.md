# Autonomous Agent Adversarial Red-Teaming & Jailbreak Defense Architecture

## 1. Mekanistik & Formalisasi Kausal Serangan Injeksi
Dalam agen otonom multi-langkah (*long-horizon multi-turn agents*), ancaman terbagi dalam 3 vektor utama:
1. **Direct Jailbreak (Intervensi Langsung)**: Perintah manipulatif dari pengguna nakal untuk mematikan safety boundary atau mengekstraksi memori/system prompt.
2. **Indirect Prompt Injection (Untrusted Tool Channels)**: Data dari web scraper, RSS feed, API pihak ketiga, atau dokumen yang memuat payload instruksi tersembunyi (`<!-- ai-instructions: ... -->`) yang mencoba membajak *execution loop*.
3. **Multi-Turn Gradient Drift**: Serangan bertahap (salami attack) yang secara kumulatif menggeser prioritas sistem melalui pertanyaan bertubi-tubi.

### Formulasi Deteksi Bayesian
$$P(\text{Hostile} \mid E) = \frac{P(E \mid \text{Hostile}) P(\text{Hostile})}{P(E)}$$
Di mana bukti $E$ mencakup pencocokan heuristik regex, deteksi token canary, dan keberadaan tag instruksi anomali pada kanal eksternal.

## 2. Invarian Canary Token & Pembuktian Kebocoran
Canary token adalah token rahasia berentropi tinggi yang disuntikkan secara dinamis ke lapisan *System Prompt* atau *Virtual Memory*. 
- Jika token ini muncul pada respon akhir atau payload keluaran tool publik, probabilitas kompromi adalah $1.0$ (Critical Veto).
- Respon seketika dibatalkan (*veto abort*) dan sesi diisolasi.

## 3. Sandboxing & Dual-Boundary Sanitization
- Kanal input dari luar (*scraped HTML*, *user inputs*, *webhook events*) disaring melalui sanitasi regex sebelum mencapai model reasoning utama.
- Output dari tool diisolasi (*quarantine boundary*) sehingga model memperlakukannya sebagai *data payload* murni, bukan *meta-instructions*.

## 4. Evaluasi Amdahl & Trade-off Latensi
- Audit regex dan canary check berjalan secara sinkronus in-memory (< 1.5ms overhead), tidak menambah beban latensi LLM (Amdahl fraction $p < 0.001$).
