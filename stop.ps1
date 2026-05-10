Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agent-Platform 停止脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 停止后端
Write-Host "[1/2] 停止后端服务 (端口 8000)..." -ForegroundColor Yellow
$backendProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($backendProcess) {
    Stop-Process -Id $backendProcess -Force -ErrorAction SilentlyContinue
    Write-Host "      后端已停止" -ForegroundColor Green
} else {
    Write-Host "      后端未运行" -ForegroundColor Gray
}
Write-Host ""

# 停止前端
Write-Host "[2/2] 停止前端服务 (端口 3000)..." -ForegroundColor Yellow
$frontendProcess = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($frontendProcess) {
    Stop-Process -Id $frontendProcess -Force -ErrorAction SilentlyContinue
    Write-Host "      前端已停止" -ForegroundColor Green
} else {
    Write-Host "      前端未运行" -ForegroundColor Gray
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  所有服务已停止！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "按 Enter 退出"
