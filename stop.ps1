$StateDir = Join-Path $PSScriptRoot ".runtime"

function Stop-ProcessTree {
    param(
        [Parameter(Mandatory = $true)][int]$ProcessId
    )

    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $process) {
        return $false
    }

    & taskkill.exe /T /F /PID $ProcessId *> $null
    return $true
}

function Stop-PortOccupants {
    param(
        [Parameter(Mandatory = $true)][int]$Port
    )

    $stopped = $false
    $pids = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($processId in $pids) {
        if (Stop-ProcessTree -ProcessId $processId) {
            $stopped = $true
        }
    }

    return $stopped
}

function Stop-DevService {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][int]$Port,
        [Parameter(Mandatory = $true)][string]$PidFile
    )

    Write-Host "停止 $Name 服务 (端口 $Port)..." -ForegroundColor Yellow

    $stopped = $false
    if (Test-Path $PidFile) {
        $savedPid = Get-Content -Path $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($savedPid -match '^\d+$') {
            $stopped = Stop-ProcessTree -ProcessId ([int]$savedPid)
        }
        Remove-Item -Path $PidFile -Force -ErrorAction SilentlyContinue
    }

    if (Stop-PortOccupants -Port $Port) {
        $stopped = $true
    }

    if ($stopped) {
        Write-Host "  $Name 已停止" -ForegroundColor Green
    }
    else {
        Write-Host "  $Name 未运行" -ForegroundColor Gray
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agent-Platform 停止脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Stop-DevService `
    -Name "后端" `
    -Port 8000 `
    -PidFile (Join-Path $StateDir "backend.pid")

Write-Host ""

Stop-DevService `
    -Name "前端" `
    -Port 3000 `
    -PidFile (Join-Path $StateDir "frontend.pid")

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  所有服务已停止" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
