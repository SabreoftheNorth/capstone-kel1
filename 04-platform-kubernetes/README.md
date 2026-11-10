# 04 — Platform Kubernetes

## Cluster
Lokal pakai **kind** (1 control-plane + 2 worker). Untuk cloud, manifest yang sama berjalan di GKE/EKS/AKS
(ganti ingress host & StorageClass).

```bash
kind create cluster --name edulearn --config 04-platform-kubernetes/kind-config.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait -n ingress-nginx --for=condition=ready pod -l app.kubernetes.io/component=controller --timeout=120s
helm install metrics-server ...   # untuk HPA (kind: tambahkan flag --kubelet-insecure-tls)
```

## Komponen (folder `manifests/`)
| File | Isi | Alasan |
|------|-----|--------|
| `namespace.yaml` | ns `edulearn` + Pod Security `baseline` | isolasi |
| `secret.yaml` | kredensial DB (demo) | dipisah dari image |
| `postgres.yaml` | StatefulSet + PVC 1Gi + headless Service | data stateful butuh identitas & volume tetap |
| `api.yaml` | Deployment (2 replika, rolling update, probes, limits), Service, HPA 2–6 @70% CPU, PDB minAvailable 1, Ingress | HA & scalability |
| `networkpolicy.yaml` | default-deny + izinkan api→db saja | least privilege jaringan |

## Deploy manual (tanpa Argo, untuk uji awal)
```bash
docker build -t ghcr.io/OWNER/edulearn-api:dev source/app
kind load docker-image ghcr.io/OWNER/edulearn-api:dev --name edulearn
kubectl apply -k 04-platform-kubernetes/manifests   # butuh CRD Prometheus Operator dulu (lihat 07), atau comment baris ../../07-...
kubectl -n edulearn get pods,svc,hpa,pdb,ingress
curl -H "Host: edulearn.localtest.me" localhost:8081/healthz
```

## Evidence → `04_evidence.jpg`
`kubectl get nodes` + `kubectl -n edulearn get all,hpa,pdb,ingress,pvc` (satu screenshot terminal, semua Running).
