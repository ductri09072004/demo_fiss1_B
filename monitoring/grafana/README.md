# Grafana Monitoring Setup

## Cấu trúc files:
- `deployment.yaml` - Grafana deployment
- `service.yaml` - Grafana service
- `secret.yaml` - Admin password secret
- `configmap-datasources.yaml` - Prometheus datasource config
- `configmap-dashboards.yaml` - Dashboard configurations
- `ingress.yaml` - Ingress for external access
- `argocd-application.yaml` - ArgoCD application manifest
- `deploy-grafana.ps1` - Deployment script

## Deploy Grafana:

### Cách 1: Sử dụng script
```powershell
cd monitoring/grafana
.\deploy-grafana.ps1
```

### Cách 2: Manual deploy
```powershell
kubectl apply -f secret.yaml
kubectl apply -f configmap-datasources.yaml
kubectl apply -f configmap-dashboards.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f argocd-application.yaml
```

## Truy cập Grafana:

### Port Forward (tạm thời):
```powershell
kubectl -n demo-fiss port-forward svc/grafana 3000:3000
```
Truy cập: http://localhost:3000

### Ingress (cần cấu hình hosts):
1. Thêm vào file `C:\Windows\System32\drivers\etc\hosts`:
```
127.0.0.1 grafana.local
```
2. Truy cập: http://grafana.local

## Credentials:
- Username: `admin`
- Password: `admin123`

## Monitoring:
- Grafana sẽ tự động kết nối với Prometheus (nếu có)
- Dashboard mặc định cho Demo FISS API
- Có thể import thêm dashboard từ Grafana.com

## Troubleshooting:
```powershell
# Check pods
kubectl -n demo-fiss get pods -l app=grafana

# Check logs
kubectl -n demo-fiss logs -l app=grafana

# Check service
kubectl -n demo-fiss get svc grafana

# Check ingress
kubectl -n demo-fiss get ingress grafana-ingress
```
