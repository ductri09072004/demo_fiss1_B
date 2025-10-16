# Script import dashboard cho demo-v81
param(
    [string]$GrafanaUrl = "http://localhost:3000",
    [string]$Username = "admin",
    [string]$Password = "admin123"
)

Write-Host "=== Import Dashboard for demo-v81 ===" -ForegroundColor Cyan

# Function để gọi Grafana API
function Invoke-GrafanaAPI {
    param(
        [string]$Method,
        [string]$Endpoint,
        [string]$Body = $null
    )
    
    $base64Auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Username}:${Password}"))
    $headers = @{
        "Content-Type" = "application/json"
        "Authorization" = "Basic $base64Auth"
    }
    
    $uri = "${GrafanaUrl}/api${Endpoint}"
    
    try {
        if ($Body) {
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers -Body $Body
        } else {
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers
        }
        return $response
    }
    catch {
        Write-Host "API Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Kiểm tra kết nối Grafana
Write-Host "Checking Grafana connection..." -ForegroundColor Yellow
$health = Invoke-GrafanaAPI -Method "GET" -Endpoint "/health"
if ($health) {
    Write-Host "Grafana is running" -ForegroundColor Green
} else {
    Write-Host "Cannot connect to Grafana at $GrafanaUrl" -ForegroundColor Red
    exit 1
}

# Đọc dashboard JSON
$dashboardFile = "dashboard.json"
Write-Host "Reading dashboard file: $dashboardFile" -ForegroundColor Yellow
if (-not (Test-Path $dashboardFile)) {
    Write-Host "Dashboard file not found: $dashboardFile" -ForegroundColor Red
    exit 1
}

$dashboardJson = Get-Content $dashboardFile -Raw
$dashboard = $dashboardJson | ConvertFrom-Json
$dashboardTitle = $dashboard.dashboard.title

# Import dashboard
Write-Host "Importing dashboard..." -ForegroundColor Yellow
$importBody = $dashboard | ConvertTo-Json -Depth 10
$result = Invoke-GrafanaAPI -Method "POST" -Endpoint "/dashboards/db" -Body $importBody

if ($result) {
    Write-Host "Dashboard imported successfully!" -ForegroundColor Green
    Write-Host "Dashboard URL: ${GrafanaUrl}/d/$($result.uid)" -ForegroundColor Cyan
} else {
    Write-Host "Failed to import dashboard" -ForegroundColor Red
    exit 1
}

Write-Host "Dashboard import completed for demo-v81!" -ForegroundColor Green