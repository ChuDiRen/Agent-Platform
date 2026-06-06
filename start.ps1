$StateDir = Join-Path $PSScriptRoot ".runtime"
New-Item -ItemType Directory -Path $StateDir -Force | Out-Null

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

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agent-Platform 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Start-DevService `
    -Name "后端" `
    -Port 8000 `
    -WorkingDirectory (Join-Path $PSScriptRoot "backend") `
    -Command "venv\Scripts\uvicorn app.main:app --reload --port 8000" `
    -PidFile (Join-Path $StateDir "backend.pid")

Write-Host "  API 文档: http://localhost:8000/docs" -ForegroundColor Green
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
Write-Host "========================================" -ForegroundColor Cyan
