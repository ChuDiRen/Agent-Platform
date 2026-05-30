Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agent-Platform 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 清理并启动后端
Write-Host "[1/2] 启动后端服务 (端口 8000)..." -ForegroundColor Yellow
$backendPid = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($backendPid) {
    Stop-Process -Id $backendPid -Force -ErrorAction SilentlyContinue
    Write-Host "      已清理占用 8000 端口的进程" -ForegroundColor DarkYellow
}
$backendPath = Join-Path $PSScriptRoot "backend"
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d $backendPath && venv\Scripts\uvicorn app.main:app --reload --port 8000" -WindowStyle Normal
Write-Host "      后端已启动: http://localhost:8000" -ForegroundColor Green
Write-Host "      API 文档: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

# 清理并启动前端
Write-Host "[2/2] 启动前端服务 (端口 3000)..." -ForegroundColor Yellow
$frontendPid = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($frontendPid) {
    Stop-Process -Id $frontendPid -Force -ErrorAction SilentlyContinue
    Write-Host "      已清理占用 3000 端口的进程" -ForegroundColor DarkYellow
}
$frontendPath = Join-Path $PSScriptRoot "fronted"
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d $frontendPath && pnpm dev" -WindowStyle Normal
Write-Host "      前端已启动: http://localhost:3000" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  所有服务已启动！" -ForegroundColor Cyan
Write-Host "  前端: http://localhost:3000" -ForegroundColor White
Write-Host "  后端: http://localhost:8000" -ForegroundColor White
Write-Host "  API 文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
