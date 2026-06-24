$StateDir = Join-Path $PSScriptRoot ".runtime"
New-Item -ItemType Directory -Path $StateDir -Force | Out-Null

function Import-BackendEnv {
    $envPath = Join-Path $PSScriptRoot "backend\.env"
    if (-not (Test-Path $envPath)) {
        return
    }
    Get-Content $envPath | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }
        $parts = $line.Split("=", 2)
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim().Trim('"').Trim("'"), "Process")
    }
}

function Stop-PortOccupants {
    param(
        [Parameter(Mandatory = $true)][int]$Port
    )

    $pids = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($processId in $pids) {
        if ($processId) {
            & taskkill.exe /T /F /PID $processId *> $null
        }
    }

    return [bool]$pids
}

function Start-DevService {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][int]$Port,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string]$PidFile
    )

    Write-Host "启动 $Name 服务 (端口 $Port)..." -ForegroundColor Yellow

    if (Stop-PortOccupants -Port $Port) {
        Write-Host "  已清理端口 $Port" -ForegroundColor DarkYellow
    }

    $cmd = "cd /d `"$WorkingDirectory`" && $Command"
    $process = Start-Process -FilePath "cmd.exe" -ArgumentList @("/k", $cmd) -WindowStyle Normal -PassThru
    Set-Content -Path $PidFile -Value $process.Id -Encoding ASCII

    Write-Host "  $Name 已启动: http://localhost:$Port" -ForegroundColor Green
}

function Start-DevProcess {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string]$PidFile
    )

    Write-Host "启动 $Name..." -ForegroundColor Yellow
    $cmd = "cd /d `"$WorkingDirectory`" && $Command"
    $process = Start-Process -FilePath "cmd.exe" -ArgumentList @("/k", $cmd) -WindowStyle Normal -PassThru
    Set-Content -Path $PidFile -Value $process.Id -Encoding ASCII
    Write-Host "  $Name 已启动" -ForegroundColor Green
}

function Get-BackendCeleryCommand {
    $venvCelery = Join-Path $PSScriptRoot "backend\venv\Scripts\celery.exe"
    if (Test-Path $venvCelery) {
        return "venv\Scripts\celery -A app.workers.celery_app.celery_app worker --loglevel=info --pool=solo"
    }
    return "python -m celery -A app.workers.celery_app.celery_app worker --loglevel=info --pool=solo"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agent-Platform 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Import-BackendEnv

Write-Host "Redis Broker: $env:CELERY_BROKER_URL" -ForegroundColor DarkCyan
Write-Host "Redis Result: $env:CELERY_RESULT_BACKEND" -ForegroundColor DarkCyan

if ($env:CELERY_BROKER_URL -match "localhost|127\.0\.0\.1") {
if (-not (Get-NetTCPConnection -LocalPort 6379 -State Listen -ErrorAction SilentlyContinue)) {
    $redis = Get-Command redis-server -ErrorAction SilentlyContinue
    if ($redis) {
        Start-DevProcess `
            -Name "Redis" `
            -WorkingDirectory $PSScriptRoot `
            -Command "redis-server --port 6379" `
            -PidFile (Join-Path $StateDir "redis.pid")
    }
    else {
        Write-Host "未找到 redis-server；如需完整分布式执行，请运行 backend\docker-compose.yml 或手动启动 Redis:6379" -ForegroundColor DarkYellow
    }
}
else {
    Write-Host "Redis 已在 6379 端口运行" -ForegroundColor Green
}
}
else {
    Write-Host "使用远程 Redis，跳过本机 6379 检查" -ForegroundColor Green
}

Write-Host ""

Start-DevService `
    -Name "后端" `
    -Port 8000 `
    -WorkingDirectory (Join-Path $PSScriptRoot "backend") `
    -Command "venv\Scripts\uvicorn app.main:app --reload --port 8000" `
    -PidFile (Join-Path $StateDir "backend.pid")

Write-Host "  API 文档: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

Start-DevProcess `
    -Name "Celery Worker" `
    -WorkingDirectory (Join-Path $PSScriptRoot "backend") `
    -Command (Get-BackendCeleryCommand) `
    -PidFile (Join-Path $StateDir "worker.pid")

Write-Host ""

Start-DevService `
    -Name "前端" `
    -Port 3000 `
    -WorkingDirectory (Join-Path $PSScriptRoot "fronted") `
    -Command "pnpm dev" `
    -PidFile (Join-Path $StateDir "frontend.pid")

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  所有服务已启动" -ForegroundColor Cyan
Write-Host "  前端: http://localhost:3000" -ForegroundColor White
Write-Host "  后端: http://localhost:8000" -ForegroundColor White
Write-Host "  API 文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Worker: Celery app.workers.celery_app.celery_app" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
