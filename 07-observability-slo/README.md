# 07 — Observability & SLO

## User journey kritis (tema Education)
1. Siswa melihat daftar kursus (`GET /courses`)
2. Siswa mendaftar kursus (`POST /enrollments`)

## SLI / SLO

| # | SLI | Cara ukur | SLO (30 hari) | Error budget |
|---|-----|-----------|---------------|--------------|
| 1 | Availability | 1 − (request 5xx / total request) | **99.5%** | 0.5% ≈ 3 jam 36 menit |
| 2 | Latency | request selesai < 500 ms / total request | **95%** | 5% |

Metrik berasal dari `/metrics` aplikasi (`http_requests_total`, `http_request_duration_seconds`),
di-scrape lewat `servicemonitor.yaml`.

## Alerting (multi-window burn rate)
| Alert | Kondisi | Severity | Arti |
|-------|---------|----------|------|
| FastBurn | burn 14.4x pada 5m **dan** 1h | critical | budget habis ~2 hari, harus ditangani segera |
| SlowBurn | burn 6x pada 30m **dan** 6h | warning | budget habis ~5 hari |
| LatencySLOBreach | good ratio < 95% selama 10m | warning | latensi melanggar SLO |
| APIDown | tidak ada target `up` | critical | layanan mati |

## Cara pasang
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
kubectl apply -k 07-observability-slo/
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80   # admin / prom-operator
kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090:9090
```

## Cara demo (bikin trafik + simulasi error)
```bash
# trafik normal
for i in $(seq 1 200); do curl -s -H "Host: edulearn.localtest.me" localhost:8081/courses >/dev/null; done
# simulasi DB mati -> /courses jadi 500 -> alert burn rate menyala
kubectl -n edulearn scale statefulset postgres --replicas=0
```

## Query Grafana untuk dashboard
- Request rate: `sum(rate(http_requests_total{job="edulearn-api"}[5m]))`
- Error ratio: `sli:http_error_ratio:rate5m`
- p95 latency: `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{job="edulearn-api"}[5m])))`
- Sisa error budget (30d): `1 - (sum(increase(http_requests_total{job="edulearn-api",status=~"5.."}[30d])) / sum(increase(http_requests_total{job="edulearn-api"}[30d]))) / 0.005`

## Evidence yang harus di-screenshot → `07_evidence.jpg`
Gabungan (collage) dari: dashboard Grafana (rate/error/p95), halaman Prometheus → Alerts (rules terdaftar),
dan satu alert yang firing saat simulasi.
