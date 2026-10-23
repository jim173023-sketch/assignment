param([switch]$Rebuild)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    docker info --format '{{.ServerVersion}}' *> $null
    if ($LASTEXITCODE -ne 0) {
        docker desktop start
        if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop, then run this script again.' }
    }
    $composeArgs = @('compose', '-p', 'ai-learning-assistant', 'up', '-d')
    if ($Rebuild) { $composeArgs += '--build' }
    & docker @composeArgs
    if ($LASTEXITCODE -ne 0) { throw 'Docker Compose failed. Review the output above.' }
    $ready = $false
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try {
            $health = Invoke-RestMethod 'http://127.0.0.1:14242/health' -TimeoutSec 3
            if ($health.status -eq 'ok') { $ready = $true; break }
        } catch { }
        Start-Sleep -Seconds 2
    }
    if (-not $ready) { throw 'Backend did not become healthy. Run docker compose -p ai-learning-assistant logs --tail=50 backend.' }
    Start-Process 'http://127.0.0.1:14242/ui/'
} finally { Pop-Location }
