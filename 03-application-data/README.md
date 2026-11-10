# 03 — Application & Data

## Aplikasi: EduLearn API
Layanan backend sederhana (Flask) untuk platform belajar online.

| Endpoint | Fungsi |
|----------|--------|
| `GET /courses` / `POST /courses` | daftar / buat kursus |
| `POST /students` | daftar siswa |
| `POST /enrollments` | siswa mendaftar kursus |
| `GET /healthz`, `GET /readyz` | liveness / readiness (cek DB) |
| `GET /metrics` | metrik Prometheus |

Kode: `../source/app/` — container non-root, 12-factor (konfigurasi via env, log ke stdout).

## Data
Database **PostgreSQL 16** (relasional, cocok untuk integritas pendaftaran: FK + UNIQUE agar siswa tidak daftar 2× ke kursus sama).
Schema: `../source/app/schema.sql`

```
students (id PK, name, email UNIQUE, created_at)
   │ 1
   │
   │ N
enrollments (id PK, student_id FK, course_id FK, enrolled_at, UNIQUE(student_id, course_id))
   │ N
   │
   │ 1
courses (id PK, title, description, created_at)
```

| Aspek | Keputusan |
|-------|-----------|
| Persistensi | StatefulSet + PVC 1Gi |
| Integritas | FK `ON DELETE CASCADE`, UNIQUE constraint |
| Performa | index `idx_enrollments_course` |
| Backup | dibahas di folder 08 (CronJob `pg_dump`) |

## Uji lokal
```bash
curl -XPOST -H "Host: edulearn.localtest.me" -H "Content-Type: application/json" \
  -d '{"title":"Intro Cloud","description":"Dasar cloud"}' localhost:8081/courses
curl -H "Host: edulearn.localtest.me" localhost:8081/courses
```

## Evidence → `03_evidence.jpg`
Collage: response `curl` ke `/courses`, dan `kubectl exec -it postgres-0 -n edulearn -- psql -U edulearn -c '\dt'` yang menampilkan 3 tabel.
