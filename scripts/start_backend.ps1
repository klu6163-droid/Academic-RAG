param(
    [int]$Port = 8001,
    [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$LogDir = Join-Path $ProjectRoot "data\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$OutLog = Join-Path $LogDir "backend_uvicorn.out.log"
$ErrLog = Join-Path $LogDir "backend_uvicorn.err.log"

$existing = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" } |
    Select-Object -First 1

if ($existing) {
    Write-Host "Backend port $Port is already listening (PID $($existing.OwningProcess))."
    Write-Host "Health: http://$HostAddress`:$Port/health"
    exit 0
}

$python = (Get-Command python).Source
$command = ('cd /d "{0}" && "{1}" -B -m uvicorn src.api.server:app --host {2} --port {3} 1> "{4}" 2> "{5}"' -f
    $ProjectRoot, $python, $HostAddress, $Port, $OutLog, $ErrLog)

$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = $env:ComSpec
$psi.Arguments = "/c $command"
$psi.WorkingDirectory = $ProjectRoot
$psi.UseShellExecute = $true
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden

$process = [System.Diagnostics.Process]::Start($psi)

Start-Sleep -Seconds 3

if ($process.HasExited) {
    Write-Host "Backend failed to start. See:"
    Write-Host "  $ErrLog"
    Get-Content $ErrLog -Tail 40
    exit $process.ExitCode
}

try {
    $health = Invoke-RestMethod -Uri "http://$HostAddress`:$Port/health" -TimeoutSec 10
    Write-Host "Backend started (PID $($process.Id)). Health: $($health.status)"
} catch {
    Write-Host "Backend process started, but health check did not respond yet."
}

Write-Host "URL: http://$HostAddress`:$Port"
Write-Host "Logs:"
Write-Host "  $OutLog"
Write-Host "  $ErrLog"
