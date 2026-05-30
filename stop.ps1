Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agent-Platform 停止脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 停止后端
Write-Host "[1/2] 停止后端服务 (端口 8000)..." -ForegroundColor Yellow
$backendStopped = $false

# 方法1：找有 python/uvicorn 子进程的 cmd 窗口，杀整个进程树
$cmdPids = (Get-Process cmd -ErrorAction SilentlyContinue).Id
foreach ($cmdPid in $cmdPids) {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$cmdPid" -ErrorAction SilentlyContinue
    if ($children | Where-Object { $_.Name -match "python|uvicorn" }) {
        & taskkill /T /F /PID $cmdPid 2>$null
        $backendStopped = $true
    }
}
# 方法2：回退，按端口杀进程
if (-not $backendStopped) {
    $portPid = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
    if ($portPid) {
        & taskkill /T /F /PID $portPid 2>$null
        $backendStopped = $true
    }
}
Write-Host $(if ($backendStopped) { "      后端已停止" } else { "      后端未运行" }) -ForegroundColor $(if ($backendStopped) { "Green" } else { "Gray" })
Write-Host ""

# 停止前端
Write-Host "[2/2] 停止前端服务 (端口 3000)..." -ForegroundColor Yellow
$frontendStopped = $false

# 方法1：找有 node/pnpm/vite 子进程的 cmd 窗口，杀整个进程树
$cmdPids = (Get-Process cmd -ErrorAction SilentlyContinue).Id
foreach ($cmdPid in $cmdPids) {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$cmdPid" -ErrorAction SilentlyContinue
    if ($children | Where-Object { $_.Name -match "node|pnpm|vite" }) {
        & taskkill /T /F /PID $cmdPid 2>$null
        $frontendStopped = $true
    }
}
# 方法2：回退，按端口杀进程
if (-not $frontendStopped) {
    $portPid = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
    if ($portPid) {
        & taskkill /T /F /PID $portPid 2>$null
        $frontendStopped = $true
    }
}
Write-Host $(if ($frontendStopped) { "      前端已停止" } else { "      前端未运行" }) -ForegroundColor $(if ($frontendStopped) { "Green" } else { "Gray" })
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  所有服务已停止！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
