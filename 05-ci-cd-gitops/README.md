# 05 — CI/CD & GitOps

## Alur
```
developer ──push──▶ GitHub ──▶ CI (GitHub Actions)
                                 1. flake8 + pytest
                                 2. build image  ghcr.io/<owner>/edulearn-api:<sha>
                                 3. Trivy scan (gagal bila HIGH/CRITICAL)
                                 4. push image
                                 5. commit tag baru ke 04-platform-kubernetes/manifests/kustomization.yaml
                                                │
                                   Argo CD ◀────┘  (pull, auto-sync, selfHeal, prune)
                                      │
                                      ▼
                              Kubernetes (ns: edulearn)
```
- **CI** (`.github/workflows/ci.yml`): hanya membangun & memverifikasi artefak. CI **tidak punya akses ke cluster**.
- **CD**: Git adalah *single source of truth*; Argo CD yang menarik perubahan ke cluster.
- **Rollback**: `git revert` commit deploy → Argo CD otomatis sinkron balik.
- **Drift**: perubahan manual via `kubectl` akan dikembalikan oleh `selfHeal`.

## Setup
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f 05-ci-cd-gitops/argocd-application.yaml
kubectl -n argocd port-forward svc/argocd-server 8080:443
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```
Ganti `OWNER` di `ci.yml`, `kustomization.yaml`, `api.yaml`, dan `argocd-application.yaml` dengan username/org GitHub tim.
Jika package GHCR private, buat `imagePullSecret`; paling mudah set package jadi *public*.

## Evidence → `05_evidence.jpg`
Collage: (1) GitHub Actions run hijau (test → build → scan → push), (2) Argo CD UI status *Synced / Healthy*,
(3) commit "ci: deploy <sha>" di history repo.
