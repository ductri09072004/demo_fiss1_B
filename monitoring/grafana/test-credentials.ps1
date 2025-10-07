# Test Grafana credentials
param(
    [string]$GrafanaUrl = "http://localhost:3000",
    [string]$Username = "admin",
    [string]$Password = "admin"
)

Write-Host "Testing Grafana credentials..." -ForegroundColor Yellow

$base64Auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Username}:${Password}"))
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Basic $base64Auth"
}

try {
    $response = Invoke-RestMethod -Uri "${GrafanaUrl}/api/user" -Method GET -Headers $headers
    Write-Host "Credentials are valid!" -ForegroundColor Green
    Write-Host "User: $($response.login)" -ForegroundColor White
    Write-Host "Email: $($response.email)" -ForegroundColor White
    return $true
} catch {
    Write-Host "Invalid credentials or connection error" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    return $false
}
