# Retro Terminal HUD & Cyber Cockpit Reference

## 1. Mekanisme Zero-Flicker Terminal TUI
Pada terminal refresh berkecepatan tinggi (10–60Hz):
- Jangan pernah mengeksekusi `\033[2J` (clear screen penuh) setiap frame karena menyebabkan kedipan visual (*flickering*).
- Gunakan kode ANSI `\033[H` (Cursor Home) untuk memposisikan ulang kursor ke sudut kiri atas, lalu timpa baris secara atomik.
- Bersihkan baris hanya bila panjang baris berkurang menggunakan `\033[K` (Clear line to end).

## 2. Penataan Lebar Visual Teks ANSI (Visual Width Calculation)
Karakter escape sequence ANSI (seperti `\033[38;2;...m`) tidak memiliki lebar fisik di layar terminal, tetapi dihitung sebagai karakter oleh fungsi `len(str)` bawaan bahasa pemrograman.
- Jika padding kolom dihitung langsung dari `len(raw_str)`, garis tepi tabel (`│` atau `┐`) akan bergeser horizontal secara berantakan saat warna teks diubah.
- Regex sanitasi wajib sebelum menghitung padding:
  ```python
  import re
  def strip_ansi(text: str) -> str:
      return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
  ```

## 3. Efek Layar CRT & Scanline di Web
- **Scanlines**: Terapkan linear-gradient 4px transparan dengan pointer-events: none agar interaksi DOM di bawahnya tidak terblokir:
  ```css
  body::before {
    content: " ";
    position: fixed;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
    background-size: 100% 4px;
    z-index: 100;
    pointer-events: none;
    opacity: 0.6;
  }
  ```
- **Pendaran Fosfor (Phosphor Glow)**: Gunakan `box-shadow` berlapis dan `text-shadow: 0 0 8px rgba(14, 165, 233, 0.6)` pada tipografi monospaced.
- **Audio Sintesis Nol-Dependensi**: Manfaatkan `window.AudioContext` untuk menghasilkan nada retro blip frekuensi 880Hz -> 1760Hz saat tombol atau aksi dieksekusi.
