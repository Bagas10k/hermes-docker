# Fluid Interactive Surface: Arsitektur Simulasi Fluida 2D Navier-Stokes untuk Vibe Coding

Dokumen ini mendokumentasikan prinsip matematis dan implementasi kanvas fluida interaktif (Eulerian Grid Fluid Simulation) berbasis metode Stam (Stable Fluids) yang dioptimasi untuk berjalan 60 FPS pada peramban web modern tanpa dependensi eksternal.

## 1. Landasan Mekanistik Navier-Stokes 2D
Persamaan fluida incompressible Newtonian:
$$\frac{\partial \mathbf{u}}{\partial t} = -(\mathbf{u} \cdot \nabla)\mathbf{u} - \frac{1}{\rho}\nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{f}$$
$$\nabla \cdot \mathbf{u} = 0$$

Komponen utama:
1. **Advection (Transport)**: Menggerakkan medan kecepatan dan densitas sepanjang alur arus fluida. Menggunakan skema semi-Lagrangian *backtracing* yang dijamin stabil tanpa batasan Courant-Friedrichs-Lewy (CFL).
2. **Diffusion (Viskositas)**: Menyebarkan momentum dan partikel warna ke sel-sel tetangga melalui relaksasi implisit Gauss-Seidel 4 iterasi.
3. **Projection (Helmholtz-Hodge Decomposition)**: Memproyeksikan medan kecepatan agar divergensi nol ($\nabla \cdot \mathbf{u} = 0$), menghasilkan tekanan fluida yang mencegah massa bertumpuk atau hilang di satu titik.
4. **Dissipation (Peredaman Energi)**: Memperkenalkan faktor redaman $\gamma = 0.992$ agar riak fluida mereda secara elegan saat tidak ada kursor bergerak, menjaga konsumsi CPU/GPU kembali ke 0%.

## 2. Optimasi Performa Vibe Coding (Sub-16ms Invariant)
- **Grid Subsampling**: Simulasi fisika fluida tidak perlu berjalan pada resolusi piksel layar (1920x1080). Cukup gunakan grid simulasi $48 \times 48$ atau $64 \times 64$ sel.
- **Bilinear Canvas Upscaling**: Render tekstur densitas fluida ke off-screen canvas resolusi rendah, lalu proyeksikan ke viewport utama dengan `ctx.imageSmoothingEnabled = true`. Hasilnya menghasilkan gradasi asap/cairan halus tanpa membebani GPU.
- **Auto-Sleep / Idle Suspension**: Jika akumulasi magnitudo kecepatan $\sum |\mathbf{u}| < \epsilon$ selama 1.5 detik, pause loop `requestAnimationFrame` dan tunggu event `pointermove` berikutnya.
- **Zero-Emoji & Visual Palette**: Warna tinta fluida mengadopsi palet semantik cerah terkalibrasi (Cyan `#0EA5E9`, Amber `#F59E0B`, Emerald `#10B981`, Rose `#F43F5E`) di atas sasis Warm Obsidian atau Luminous Slate.
