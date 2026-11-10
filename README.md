# Cloud Capstone — EduLearn (Education)

Platform pendaftaran kursus online yang dijalankan di Kubernetes dengan CI/CD GitOps dan SLO.

| Folder | Status Milestone 1 |
|--------|--------------------|
| 01-business | belum |
| 02-architecture | belum |
| **03-application-data** | ✅ |
| **04-platform-kubernetes** | ✅ |
| **05-ci-cd-gitops** | ✅ |
| 06-security | belum |
| **07-observability-slo** | ✅ |
| 08–11 | belum |
| source/ | kode aplikasi |

## Urutan menjalankan
1. `kind create cluster ...` (04) → ingress-nginx
2. Install kube-prometheus-stack (07)
3. Install Argo CD + apply Application (05)
4. Push ke `main` → CI membangun image → Argo CD deploy
5. Tes aplikasi (03) dan buka Grafana (07)

> Ganti semua `OWNER` dengan username/org GitHub tim. Ganti `<team>` pada nama repo.
> Setiap folder punya file `NN_evidence.jpg` — isi dengan screenshot sesuai instruksi di README folder tersebut.
