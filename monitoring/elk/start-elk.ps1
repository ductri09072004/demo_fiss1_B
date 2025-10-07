# Start ELK Stack for demo_fiss1
Write-Host "Starting ELK Stack for demo_fiss1..." -ForegroundColor Green

# Stop existing containers if running
docker stop demo-fiss-kibana demo-fiss-logstash demo-fiss-elasticsearch demo-fiss-filebeat 2>$null
docker rm demo-fiss-kibana demo-fiss-logstash demo-fiss-elasticsearch demo-fiss-filebeat 2>$null

# Start ELK Stack
docker-compose -f docker-compose.yml up -d

Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check services status
Write-Host "`n=== Service Status ===" -ForegroundColor Cyan
Write-Host "Elasticsearch: http://localhost:9200" -ForegroundColor Green
Write-Host "Kibana: http://localhost:5601" -ForegroundColor Green
Write-Host "Logstash: http://localhost:9600" -ForegroundColor Green

# Test Elasticsearch
try {
    $response = Invoke-RestMethod -Uri "http://localhost:9200" -ErrorAction Stop
    Write-Host "✅ Elasticsearch is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Elasticsearch is not ready yet" -ForegroundColor Red
}

Write-Host "`n=== Access URLs ===" -ForegroundColor Cyan
Write-Host "Kibana Dashboard: http://localhost:5601" -ForegroundColor Yellow
Write-Host "Elasticsearch API: http://localhost:9200" -ForegroundColor Yellow
Write-Host "Logstash API: http://localhost:9600" -ForegroundColor Yellow

Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Open Kibana: http://localhost:5601" -ForegroundColor White
Write-Host "2. Create index pattern: demo-fiss-logs-*" -ForegroundColor White
Write-Host "3. View logs from demo_fiss1 API" -ForegroundColor White
