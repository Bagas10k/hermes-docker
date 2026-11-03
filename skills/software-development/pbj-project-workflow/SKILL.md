---
name: pbj-project-workflow
description: Use when working on Bagas's website-pbj Laravel project.
version: 0.2.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [laravel, pbj, accounting, erp, mysql, livewire, blade]
---

# PBJ Project Workflow

Operational, architectural, accounting, and UI engineering doctrine for the PBJ Laravel project (`/home/ubuntu/website-pbj`).

## Supporting References
- `references/unabridged-pbj-workflow.md`: Full unabridged reference and historical incident log.
- `references/branch-integration.md`: Collaborator review, git fetch, and landing protocols.
- `references/financial-reporting.md`: Laba Rugi, Neraca, Arus Kas, Buku Besar, and revenue-profit bridge architecture.
- `references/role-workflow-guides.md`: Comprehensive RBAC matrix and role-specific UI workflows.
- `references/superadmin-account-management.md`: Super Admin creation, username changes, and authentication seeder.
- `references/invoice-catalog-cache.md`: Caching layers, dropdown options, and inventory catalog synchronization.
- `references/workflow-documentation.md`: Executive PDF reporting, screenshot evidence, and client presentation standards.

---

## 1. Database & Migration Invariants

- **Engine Lockdown (MySQL 8.0)**: PBJ strictly targets MySQL 8.0.30 (`pbj_db` on Docker). Never test or migrate using SQLite or MariaDB syntax variations that produce engine-divergence bugs.
- **Disposable Testing**: Always rehearse migrations and test regressions on a disposable target MySQL container before touching live state.
- **Opening Balance Baseline**: When auditing initial balances (`saldo_awal`), first sum `saldo_awal` grouped by `saldo_normal`. Debit must equal Credit exactly before approving postings.
- **Dropdown & Master Data Pipeline**: When dropdown data is reported missing, verify in order: master rows in DB → cached options/catalog → controller payload → view component inclusion.

## 2. Git & Branching Protocol

- **Target Worktree**: PBJ lives at `/home/ubuntu/website-pbj`. Inspect active branch and remote divergence before editing.
- **Dedicated Exploration**: Use branch `sandbox` tracked to `origin/sandbox`. Never commit exploratory experiments or unapproved refactors directly to `main`.
- **Collaborator Review**: Run `git fetch origin` before assuming branch spelling or existence. Inspect diffs via three-way merge preview before merging collaborator work.
- **Publish Sandbox**: "Publish sandbox" means building and deploying to Bagas's public PBJ preview instance, NOT pushing untested code to production.

## 3. RBAC, Authentication & Security

- **Direktur Role (Strict Read-Only)**: The `Direktur` role is strictly read-only across all modules. Enforce at both Blade UI level (`app.blade.php`) and server-side middleware/controller level.
  - Direktur views financial statements, KPI metrics, and transaction ledgers.
  - Direktur CANNOT create, update, delete, post, or cancel journal entries or master records.
- **Server-Side Enforcement**: Hiding buttons in Alpine.js or Blade is NOT security. Block mutation routes (`POST`, `PUT`, `DELETE`) with policy/middleware checks returning HTTP 403.
- **Super Admin Credentials**: DB uses bcrypt. To create or reset Super Admin, use `php artisan tinker` or `references/superadmin-account-management.md`. Keep `AutentikasiSeeder` clean of hardcoded passwords in VCS.
- **Role Seeding**: Seed reference roles via `JabatanSeeder`. Never create disposable demo logins in production seeders.

## 4. Master Data & Fleet Separation (KSO / Sewa vs Asset)

- **Operational vs Capital Assets**: External vehicles (KSO / Sewa) are operational records, NEVER PBJ capital assets.
  - Create KSO/Sewa records with `kode_aset = null` on the operational path; never mutate PBJ's `data_aset`.
  - Operational vehicle tables retain exactly 8 columns; PBJ capital asset tables retain 10 asset columns.
- **Dispatcher Vehicle IDs**: Accept canonical master identifiers in Dispatcher create and edit forms. When armada category changes in Alpine state, clear canonical IDs and free-text fields cleanly.
- **Three-Part Plate Entry**: Vehicle license plates use a shared three-part input component (`kode_wilayah`, `nomor_polisi`, `kode_akhir`). Inspect all callers before altering validation regex.

## 5. Financial Accounting & COA Integration

- **COA Integrity**: Trace posting callers, account identifiers, and linked bank accounts before altering journal mechanics.
- **Manual Journals**: Check balance guards at posting service level (`Debit == Kredit`). For `The nominal field is required` errors, verify formatted currency inputs unmask to raw numbers before payload dispatch.
- **Financial Reporting Cadence**: Execute reporting changes in small gated slices with durable ledgers (done, verified, blocked, next).
  - Prioritize a compact revenue-to-profit bridge chart over decorative KPIs.
  - Preserve full account breakdowns, Buku Besar drilldowns, and subtotal lines.
  - Pass report filter parameters (`tanggalCutoff`, `bulan`, `tahun`) from controller into view with fallback defaults (`now()->month`, `now()->year`).
  - Zero In-Page Nav Redundancy: If a financial report menu exists in the sidebar, never duplicate redundant in-page tab navigators.
- **Tax Architecture (PPN & PPh)**: Tax automation is a requirements backlog item, not active default policy. Never apply automated tax deductions without explicit schema sign-off.
- **Payment-Out Forms**: Enforce role authorization at controller level for debt repayments, cash advances, top-up credit limits, and bank-funded purchases.

## 6. PBJ UI Component Tokens ("Warm Paper & Obsidian")

- **Card Container Tokens**: Strictly adhere to `bg-white dark:bg-[#14161F] border border-[#E2E8F0] dark:border-[#232738] rounded-2xl p-6 shadow-sm`.
- **Form Inputs & Modals**:
  - Inputs: `bg-[#F4F6F9] dark:bg-[#1C1E2A] border border-[#E2E8F0] dark:border-[#2A2E3D] text-[#0F172A] dark:text-[#F8FAFC] rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-[#2563EB]`.
  - Modals: Centered, high-contrast backdrop blur (`bg-slate-900/60 backdrop-blur-sm`), header divider, explicit cancel/save buttons.
- **Table Components**:
  - Row Actions: Always use `<x-menu-aksi-tabel>` with copy, edit, delete modals and audit trail.
  - Empty States: In `@empty`, use `<x-tabel-kosong colspan="..." judul="..." deskripsi="...">`.
  - Filter & Search Bar: Wrap in `animasi-masuk flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6`.
- **Sidebar & Navigation**: A parent category in the sidebar must never be converted into a direct link if it contains child modules. Keep dropdown chevron indicators synchronized with Alpine open state.

## 7. Deliverables & Verification Standards

- **Evidence-First Verification**: HTTP 200 alone does not prove visible UI rendering. Verify target text and component elements exist in the rendered DOM.
- **Visual Proof Screenshots**: For every requested UI surface, capture full screenshots showing URL, role, responsive width, and populated data.
- **Director Executive Summary (PDF)**: When reporting financial UI completions to Bagas, provide a concise PDF executive brief pairing full screenshots with business explanation and verified transaction balances.
