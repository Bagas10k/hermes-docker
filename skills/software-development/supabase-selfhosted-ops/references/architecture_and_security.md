# Supabase Self-Hosted Architecture & RLS Security Reference

## 1. Topologi Layanan Docker Compose & Ingress Gateway

Supabase Self-Hosted diatur via multi-container Docker Compose. Arsitektur terbaru menggantikan Kong dengan **Envoy Proxy v1.39+** sebagai ingress API gateway terpadu pada port `8000`.

### Peta Routing Envoy Ingress:
- `/` -> Supabase Studio Dashboard (dilindungi HTTP Basic Auth via `DASHBOARD_USERNAME` & `DASHBOARD_PASSWORD`).
- `/rest/v1/` -> PostgREST daemon (port internal 3000):
  - Wajib menyertakan header `apikey: <ANON_KEY | SERVICE_ROLE_KEY>` dan `Authorization: Bearer <KEY>`.
  - Akses root schema OpenAPI `/rest/v1/` hanya diizinkan untuk `SERVICE_ROLE_KEY` (RBAC filter). Akses anonim dibatasi pada RPC atau tabel spesifik yang terbuka.
- `/auth/v1/` -> GoTrue Auth Engine (port internal 9999).
- `/storage/v1/` -> Storage API (port internal 5000).
- `/realtime/v1/` -> Supabase Realtime Engine (Elixir WebSocket & broadcast).

## 2. Row Level Security (RLS) Mechanics & Bounds

PostgreSQL Row Level Security (RLS) membatasi akses baris tabel pada tingkat mesin basis data:
1. `ALTER TABLE "tabel" ENABLE ROW LEVEL SECURITY;`
   - **PENTING**: Mengaktifkan RLS tanpa kebijakan (*0 policies*) menyebabkan **DEFAULT DENY**. PostgREST akan mengembalikan `42501 (new row violates row-level security policy)` pada INSERT/UPDATE dan list kosong `[]` pada SELECT untuk pengguna anon / authenticated.
2. Formulasi Kebijakan:
   - SELECT (USING expression): `CREATE POLICY "p_select" ON public.items FOR SELECT USING (auth.uid() = user_id);`
   - INSERT (WITH CHECK expression): `CREATE POLICY "p_insert" ON public.items FOR INSERT WITH CHECK (auth.uid() = user_id);`
   - Publik Baca Saja: `CREATE POLICY "p_anon_read" ON public.posts FOR SELECT TO anon USING (is_published = true);`
3. Perbedaan Kunci:
   - `ANON_KEY`: Terikat pada PostgreSQL role `anon` (atau `authenticated` setelah login JWT). Mutlak tunduk pada RLS.
   - `SERVICE_ROLE_KEY`: Memiliki role `service_role` yang mem-bypass seluruh RLS (`BYPASSRLS`). Hanya boleh digunakan di backend server-side rahasia, dilarang disematkan ke antarmuka web klien.

## 3. Strategi Backup, Schema Migration & Volume Isolation

- Backup schema publik PostgreSQL aman:
  ```bash
  docker exec supabase-db pg_dump -U postgres -d postgres --clean --if-exists --schema=public > backup_public.sql
  ```
- Backup seluruh database (termasuk Auth, Storage metadata):
  ```bash
  docker exec supabase-db pg_dumpall -U postgres --clean > backup_full.sql
  ```
- Volume persistensi fisik:
  - Database data: `/home/ubuntu/supabase/volumes/db/data`
  - Storage bucket files: `/home/ubuntu/supabase/volumes/storage`
  - Envoy ingress: `/home/ubuntu/supabase/volumes/api/envoy`
