# Referensi Arsitektur: Alpine Minimal Live-Boot & Zero-Trace RAM-Disk

## 1. Topologi Booting RAM-Disk (Initramfs & OverlayFS)

```
+-----------------------------------------------------------+
| Physical USB Media (FAT32 EFI + ext4 Persistensi Opsional)|
+-----------------------------------------------------------+
                             |
                   GRUB EFI / Syslinux
                             |
                +------------v------------+
                | Kernel (vmlinuz-lts)    |
                | Initramfs (initramfs)   |
                +------------+------------+
                             |
       Parameter: 'copytoram=yes', 'modules=loop,squashfs,overlay'
                             |
         +-------------------v-------------------+
         | Alokasi RAM (Volatile tmpfs, <= 400MB)|
         |                                       |
         | [SquashFS Root (ro)] (~95MB)          |
         |         +                             |
         | [OverlayFS Upperdir (rw)] (~64MB)     |
         |         =                             |
         | Combined Root Virtual Filesystem      |
         +-------------------+-------------------+
                             |
        Flashdisk USB DAPAT DICABUT AMAN (Zero-IO)
                             |
                 Headless Agent Bootstrap
             (/usr/local/bin/agent-autostart)
```

## 2. Parameter Kernel Kunci untuk Booting Volatile

- `alpine_dev=UUID=...`: Identifikasi partisi boot sumber.
- `copytoram=yes`: Memerintahkan skrip init Alpine untuk menyalin seluruh berkas `.apkovl` atau `.squashfs` ke memori fisik sebelum melakukan pivot_root.
- `console=tty0 console=ttyS0,115200`: Membuka akses terminal simultan pada monitor lokal dan port serial virtual (COM).
- `quiet loglevel=3`: Mengurangi kebisingan log kernel pada konsol agar output agent tampil bersih.

## 3. Matriks Trade-Off Filesystem Kompresi Rootfs

| Format Kompresi | Rasio Kompresi | Decompression Speed | RAM Overhead Saat Mount | Keterangan |
|---|---|---|---|---|
| **SquashFS XZ (256KB block)** | **Tertinggi (~70% pangkas)** | Sedang (~120 MB/s) | $\approx 12\text{ MB}$ | **Rekomendasi Utama** untuk batas RAM 400MB |
| SquashFS ZSTD (level 19) | Tinggi (~65% pangkas) | Sangat Cepat (~450 MB/s) | $\approx 24\text{ MB}$ | Pilihan bila CPU sangat lemah |
| Gzip | Standar (~55% pangkas) | Cepat (~250 MB/s) | $\approx 8\text{ MB}$ | Legacy fallback |

## 4. Standar Isolasi Disk Host (Zero-Trace Policy)

Saat agen melakukan investigasi terhadap sistem host:
1. Blokir auto-mount kernel: `systemctl mask udisks2` atau matikan auto-mount rule di udev.
2. Gunakan flag kernel `norecovery` pada ext3/ext4: mencegah jurnal ditulis ulang.
3. Gunakan loop device read-only jika menganalisis file image raw: `losetup -r -f /path/to/image.raw`.
4. Jangan menyalin binary ke storage host: seluruh eksekusi dilakukan dari RAM-disk.
