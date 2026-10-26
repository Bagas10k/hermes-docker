---
name: bulk-translation-pipeline
description: Translating JSON/RSS in bulk safely via free APIs.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [translation, automation, rate-limits, api-resilience, data-pipeline]
---

# Bulk Translation Pipeline

Gunakan skill ini saat membuat skrip (Python/Node.js) untuk menerjemahkan kumpulan data besar secara massal menggunakan API penerjemah publik/gratis, untuk mencegah korupsi data akibat limitasi (rate limit).

## Aturan Pencegahan Mutlak (Quality Gates)

### 1. Deteksi "Silent 500" pada API Gratis
Beberapa API penerjemah gratis (seperti Google Translate backend pada library `deep-translator`) tidak melontarkan exception HTTP (429 atau 503) saat terkena *rate limit*. Sebaliknya, API tersebut diam-diam mengembalikan teks berbunyi `"Error 500 (Server Error)!!"`.
**Pitfall:** Jika skrip menyimpan respons secara membabi buta, *database* akan tertimpa teks "Error 500".
**Solusi:** Selalu periksa teks hasil terjemahan sebelum menyimpannya ke objek data:
```python
translated = translator.translate(text)
if "Error 500" in translated:
    print("Rate limited, keeping original text")
    # Skip saving translation flag, maintain original text, apply heavy sleep
    time.sleep(5)
    continue
```

### 2. Tunda Jeda secara Wajib (Sleep)
Gunakan *delay* antar putaran (minimal `1.5s` per dokumen). Jika terdeteksi *Error 500*, terapkan pinalti waktu (minimal `5s`).

### 3. Pekerjaan Latar Belakang & Daemon
Penerjemahan ratusan dokumen akan membekukan antarmuka *front-end* / proses *polling* utama jika dipanggil secara sinkron.
**Aturan:** Pisahkan skrip penerjemah menjadi file mandiri (`translate.py`), lalu panggil di latar belakang (`spawn('python', ['translate.py'], { detached: true })`) agar tidak menghambat rantai eksekusi utama.