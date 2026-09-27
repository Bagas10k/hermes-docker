---
name: portable-liveboot-agent
description: Build minimal RAM-disk bootable Linux agents under 400MB.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [liveboot, alpine, ramdisk, initramfs, systems-engineering, portable]
    related_skills: [systems-engineering:ephemeral-worker-engine, systems-engineering:sqlite-production-hardening]
---

# Portable Live-Boot Agent & Minimal RAM-Disk Engineering

Engine dan panduan teknis rekayasa USB bootable live agent berbobot ultra-ringan berbasis Alpine Linux Standard/Extended. Dirancang khusus untuk skenario intervensi lapangan, edge computing darurat, dan audit mesin host dengan footprint RAM-disk $\le 400\text{ MB}$, isolasi memori volatile, persistensi terenkripsi hybrid, serta zero-trace host unmounting.

## When to Use

- Membangun media live USB darurat yang memuat runtime Hermes Agent mandiri.
- Menjalankan inspeksi atau perbaikan sistem host tanpa mengotori disk host (zero-trace audit).
- Membutuhkan sistem operasi agentik instan berbasis RAM (tmpfs/initramfs) dengan batas memori ketat ($\le 512\text{ MB} - 1\text{ GB}$).
- Konfigurasi auto-startup daemon tanpa interaksi manual (headless bootstrap).

## Prerequisites

- Linux host dengan toolchain utilitas disk: `fdisk`, `parted`, `e2fsprogs`, `dosfstools`, `mtools`, `syslinux`/`grub`.
- Akses root (`sudo`) saat menulis citra partisi ke blok perangkat fisik (misal `/dev/sdb`).
- Kernel Linux target dengan modul `overlayfs`, `loop`, `squashfs`, dan `tmpfs`.

## Quick Reference

Jalankan script verifikasi dan kalkulator footprint konfigurasi:

```bash
# Audit footprint alokasi RAM-disk dan skema partisi live boot
python3 ~/.hermes/skills/systems-engineering/portable-liveboot-agent/scripts/liveboot_calc.py --profile minimal
```

Uji unmount aman dan zero-trace verification:

```bash
# Validasi ketiadaan residual mount atau lock pada disk host
python3 ~/.hermes/skills/systems-engineering/portable-liveboot-agent/scripts/host_unmount_guard.py --target /mnt/host
```

## Architecture & Mathematical Bounds

### 1. Model Alokasi RAM (Footprint Bound $\le 400\text{ MB}$)
Sistem live-boot beroperasi sepenuhnya di atas `tmpfs` (volatile RAM-disk). Alokasi memori total $M_{\text{total}}$ dimodelkan sebagai:

$$M_{\text{used}} = M_{\text{kernel}} + M_{\text{initramfs\_root}} + M_{\text{overlayfs\_cow}} + M_{\text{runtime\_agent}}$$

- $M_{\text{kernel}} + M_{\text{base\_modules}} \approx 32\text{ MB}$ (Alpine hardened vmlinuz).
- $M_{\text{initramfs\_root}} \approx 95\text{ MB}$ (Alpine rootfs terkompresi SquashFS XZ block size 256KB).
- $M_{\text{overlayfs\_cow}} \approx 64\text{ MB}$ (Volatile upperdir copy-on-write scratchpad).
- $M_{\text{runtime\_agent}} \approx 160\text{ MB}$ (Python micro-runtime, SQLite WAL memory cache, model tokenizer).
- Total: $351\text{ MB} \le 400\text{ MB}$ (Lolos kendala batas RAM budget).

### 2. Skema Partisi Dual-Partition Hybrid
USB fisik diformat dengan dua partisi deterministik:
1. `PART 1 (ESP/BOOT)`: FAT32, ukuran 512 MB. Memuat EFI bootloader, GRUB/Syslinux, Kernel `vmlinuz-lts`, dan `initramfs-lts`. Flag: `boot, esp`.
2. `PART 2 (PERSISTENCE)`: ext4 (opsional LUKS2 encrypted), label `AGENT_DATA`. Memuat konfigurasi agent, log audit terenkripsi, dan local storage. Dimount read-write hanya pada direktori persistensi tertentu via overlay / bind-mount.

## Step-by-Step Procedure

### Langkah 1: Siapkan Alpine Linux Minimal Rootfs
1. Unduh rootfs mini Alpine Linux terkini (`x86_64`):
   ```bash
   mkdir -p /tmp/liveboot_build/rootfs
   cd /tmp/liveboot_build
   curl -Lo alpine-minirootfs.tar.gz https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-minirootfs-3.20.3-x86_64.tar.gz
   tar -xzf alpine-minirootfs.tar.gz -C rootfs/
   ```

2. Pasang paket inti runtime tanpa dependensi GUI:
   ```bash
   # Masuk ke chroot / binfmt container
   # Pasang: linux-lts, udev, e2fsprogs, openrc, python3, sqlite, ca-certificates
   ```

### Langkah 2: Konfigurasi Initramfs & Headless Auto-Startup
1. Di dalam `/etc/inittab` rootfs, arahkan `tty1` dan `ttyS0` (serial console) untuk auto-login user service `agent`:
   ```text
   tty1::respawn:/sbin/getty -n -l /usr/local/bin/agent-autostart 38400 tty1
   ttyS0::respawn:/sbin/getty -n -l /usr/local/bin/agent-autostart 115200 ttyS0
   ```
2. Pasang skrip daemon `/usr/local/bin/agent-autostart` dengan flag non-blocking:
   ```bash
   #!/bin/sh
   # Deteksi partisi persistence jika tersedia
   mkdir -p /media/agent_data
   mount -L AGENT_DATA /media/agent_data 2>/dev/null || true
   # Jalankan background agent daemon
   exec /usr/bin/python3 -m hermes_liveboot_daemon
   ```

### Langkah 3: Build SquashFS Terkompresi XZ
Kompres seluruh rootfs menggunakan SquashFS dengan rasio kompresi maksimal:
```bash
mksquashfs rootfs/ rootfs.squashfs -comp xz -b 256K -Xbcj x86 -noappend
```

### Langkah 4: Konfigurasi Bootloader GRUB EFI
Buat berkas konfigurasi boot `boot/grub/grub.cfg` pada partisi boot FAT32:
```text
set default=0
set timeout=2

menuentry "Hermes Portable Live-Boot Agent (RAM-Disk 400MB)" {
    linux /boot/vmlinuz-lts quiet console=tty0 console=ttyS0,115200 alpine_dev=UUID=BOOT-PART modules=loop,squashfs,overlay copytoram=yes
    initrd /boot/initramfs-lts
}
```
*Parameter Kunci:* `copytoram=yes` memastikan seluruh citra dimuat ke RAM sehingga USB flashdisk dapat dicabut setelah proses boot selesai tanpa menyebabkan kernel panic.

### Langkah 5: Protokol Zero-Trace Host Unmounting
Saat agen melakukan inspeksi pada storage internal komputer host (misal `/dev/nvme0n1p1`):
1. **Wajib Mount Read-Only**:
   ```bash
   mount -o ro,noatime,nodiratime,norecovery /dev/nvme0n1p1 /mnt/host_target
   ```
2. **Siklus Pelepasan Bersih**:
   - Kirim `SIGTERM` lalu `SIGKILL` ke seluruh proses yang mengunci file descriptor di `/mnt/host_target`.
   - Sinkronisasi buffer dan flushing cache: `sync`.
   - Unmount bersih: `umount /mnt/host_target`.
   - Verifikasi melalui kernel proc: pastikan entri `/mnt/host_target` hilang dari `/proc/mounts`.

## Pitfalls & Failure Modes

1. **Jebakan `copytoram=no` (Disk Pull Kernel Panic)**:
   Jika parameter `copytoram=yes` tidak diaktifkan, kernel akan mempertahankan open file descriptor ke filesystem SquashFS di flashdisk. Mencabut USB akan memicu filesystem I/O error seketika dan kernel panic.
2. **Jebakan Replay Journal pada Partisi Host (Zero-Trace Violation)**:
   Melakukan mount standar `mount -o ro /dev/sdX` pada partisi ext4 atau NTFS dirty sering kali secara otomatis memicu replay journal kernel, yang menyebabkan mutasi metadata pada disk host.
   *Solusi*: Wajib sertakan opsi `norecovery` (untuk ext4) atau gunakan utilitas `ntfs-3g -o ro,norecover` untuk mencegah penulisan byte tunggal pun ke media target.
3. **RAM Exhaustion oleh tmpfs `/tmp`**:
   Operasi scraping atau ekstraksi log besar dapat menghabiskan ruang `tmpfs` RAM. Selalu tetapkan batas ukuran tmpfs: `mount -t tmpfs -o size=150M tmpfs /tmp`.

## Verification & Compliance

Verifikasi kesiapan live-boot dan kepatuhan footprint:
1. Jalankan `python3 ~/.hermes/skills/systems-engineering/portable-liveboot-agent/scripts/liveboot_calc.py` untuk memastikan alokasi RAM $\le 400\text{ MB}$.
2. Jalankan `python3 ~/.hermes/skills/systems-engineering/portable-liveboot-agent/scripts/host_unmount_guard.py` untuk menguji fungsionalitas zero-trace unmounting secara deterministik.
