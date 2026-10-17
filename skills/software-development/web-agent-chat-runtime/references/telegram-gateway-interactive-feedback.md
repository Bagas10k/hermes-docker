# Telegram Gateway Interactive Feedback & UI Controls

Prosedur dan pola implementasi kontrol pesan interaktif pada Telegram Bot Adapter di Hermes Gateway.

## 1. Arsitektur Tombol Feedback Respon (Inline Rating)

### 1.1 Struktur Keyboard
- Gunakan `InlineKeyboardMarkup` dengan format 1 baris (2 tombol) agar hemat ruang di layar HP:
  - `[👍 Bagus]` -> `callback_data="fb:up:<id>"`
  - `[👎 Kurang]` -> `callback_data="fb:down:<id>"`
- Batas keras Telegram: `callback_data` maksimal 64 byte. Gunakan prefix pendek (`fb:`) dan ID ringkas (timestamp atau sequence id).

### 1.2 Aturan Penyematan (Gating Rule)
Tombol feedback HANYA disematkan pada pesan respon akhir turn konversasi:
- **Dilarang:** Jangan sematkan pada pesan progress (`_is_progress`), pesan interim (`_interim_send=True`), prompt persetujuan eksekusi (`exec_approval`), atau dialog klarifikasi (`send_clarify`).
- Sematkan hanya pada chunk pesan terakhir (`index == len(chunks) - 1`) dari pesan final.

### 1.3 Siklus Hidup Callback (In-Place Update & Anti-Double Vote)
1. Tangkap callback query dengan prefix `fb:` di handler `_handle_callback_query`.
2. Jika data == `fb:done`:
   - Panggil `await query.answer("Penilaian ini sudah tersimpan.", show_alert=False)`.
   - Segera return untuk mencegah pencatatan berulang.
3. Jika data diawali `fb:up:` atau `fb:down:`:
   - Ambil nilai rating (`up` -> "👍 Bagus", `down` -> "👎 Kurang").
   - Berikan notifikasi toast: `await query.answer(f"Terima kasih atas nilainya: {label}!", show_alert=False)`.
   - Update tampilan tombol in-place menggunakan `await query.edit_message_reply_markup(reply_markup=...)` menjadi:
     `[✅ Dinilai: {label}]` dengan `callback_data="fb:done"`.
   - Rekam metadata voting ke pangkalan data SQLite terisolasi.

## 2. Penyimpanan Data Evaluasi (SQLite Telemetry)

Gunakan file database terisolasi (misal `~/.hermes/response_feedback.db`) agar tidak membebani transaksi atau merusak skema `state.db`:
```sql
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT,
    message_id TEXT,
    user_id TEXT,
    user_name TEXT,
    vote TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 3. Verifikasi & Pengujian
1. Cek kompilasi sintaks Python:
   `python3 -m py_compile plugins/platforms/telegram/adapter.py`
2. Jalankan pengujian mandiri simulasi callback query dan verifikasi data SQLite.
3. Pastikan restart gateway sukses tanpa crash boot:
   `systemctl --user restart hermes-gateway hermes-gateway-bikagent`
   `systemctl --user status hermes-gateway --no-pager`
