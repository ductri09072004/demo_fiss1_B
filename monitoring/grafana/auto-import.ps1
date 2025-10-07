# Script tự động import dashboard vào Grafana
param(
    [string]$GrafanaUrl = "http://localhost:3000",
    [string]$Username = "admin",
    [string]$Password = "admin",
    [string]$DashboardFile = "docker-dashboard.json"
)

Write-Host "=== Auto Import Dashboard to Grafana ===" -ForegroundColor Cyan

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
    Write-Host "Please check Grafana is running and credentials are correct" -ForegroundColor Yellow
    exit 1
}

# Đọc dashboard JSON
Write-Host "Reading dashboard file: $DashboardFile" -ForegroundColor Yellow
if (-not (Test-Path $DashboardFile)) {
    Write-Host "Dashboard file not found: $DashboardFile" -ForegroundColor Red
    exit 1
}

$dashboardJson = Get-Content $DashboardFile -Raw
$dashboard = $dashboardJson | ConvertFrom-Json

# Kiểm tra dashboard đã tồn tại chưa
Write-Host "Checking if dashboard exists..." -ForegroundColor Yellow
$existingDashboards = Invoke-GrafanaAPI -Method "GET" -Endpoint "/search?query=Demo FISS API Dashboard"
$existingDashboard = $existingDashboards | Where-Object { $_.title -eq "Demo FISS API Dashboard" }

if ($existingDashboard) {
    Write-Host "Dashboard already exists. Getting current version..." -ForegroundColor Yellow
    $currentDashboard = Invoke-GrafanaAPI -Method "GET" -Endpoint "/dashboards/uid/$($existingDashboard.uid)"
    if ($currentDashboard) {
        $dashboard.dashboard.id = $currentDashboard.dashboard.id
        $dashboard.dashboard.version = $currentDashboard.dashboard.version + 1
    }
} else {
    Write-Host "Creating new dashboard..." -ForegroundColor Yellow
}

# Import dashboard
Write-Host "Importing dashboard..." -ForegroundColor Yellow
$importBody = $dashboard | ConvertTo-Json -Depth 10
$result = Invoke-GrafanaAPI -Method "POST" -Endpoint "/dashboards/db" -Body $importBody

if ($result) {
    Write-Host "Dashboard imported successfully!" -ForegroundColor Green
    Write-Host "Dashboard URL: $GrafanaUrl/d/$($result.uid)" -ForegroundColor Cyan
} else {
    Write-Host "Failed to import dashboard. Trying to delete and recreate..." -ForegroundColor Yellow
    
    # Xóa dashboard cũ và tạo mới
    if ($existingDashboard) {
        $deleteResult = Invoke-GrafanaAPI -Method "DELETE" -Endpoint "/dashboards/uid/$($existingDashboard.uid)"
        if ($deleteResult) {
            Write-Host "Old dashboard deleted. Creating new one..." -ForegroundColor Yellow
            $dashboard.dashboard.id = $null
            $dashboard.dashboard.version = 0
            
            $importBody = $dashboard | ConvertTo-Json -Depth 10
            $result = Invoke-GrafanaAPI -Method "POST" -Endpoint "/dashboards/db" -Body $importBody
            
            if ($result) {
                Write-Host "Dashboard recreated successfully!" -ForegroundColor Green
                Write-Host "Dashboard URL: $GrafanaUrl/d/$($result.uid)" -ForegroundColor Cyan
            } else {
                Write-Host "Failed to recreate dashboard" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "Failed to delete old dashboard" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Failed to import dashboard" -ForegroundColor Red
        exit 1
    }
}

# Kiểm tra datasource
Write-Host "Checking Prometheus datasource..." -ForegroundColor Yellow
$datasources = Invoke-GrafanaAPI -Method "GET" -Endpoint "/datasources"
$prometheusDS = $datasources | Where-Object { $_.type -eq "prometheus" }

if ($prometheusDS) {
    Write-Host "Prometheus datasource found: $($prometheusDS.name)" -ForegroundColor Green
} else {
    Write-Host "No Prometheus datasource found. Creating one..." -ForegroundColor Yellow
    
    $datasourceConfig = @{
        name = "Prometheus"
        type = "prometheus"
        url = "http://host.docker.internal:9090"
        access = "proxy"
        isDefault = $true
    } | ConvertTo-Json
    
    $dsResult = Invoke-GrafanaAPI -Method "POST" -Endpoint "/datasources" -Body $datasourceConfig
    if ($dsResult) {
        Write-Host "Prometheus datasource created" -ForegroundColor Green
    } else {
        Write-Host "Failed to create Prometheus datasource" -ForegroundColor Red
    }
}

Write-Host "Dashboard import completed!" -ForegroundColor Green
Write-Host "Access Grafana: $GrafanaUrl" -ForegroundColor Cyan
Write-Host "Dashboard: $GrafanaUrl/d/$($result.uid)" -ForegroundColor Cyan
