param(
    [int]$Port = 8001
)

$ErrorActionPreference = "Stop"

$pids = @(Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" } |
    Select-Object -ExpandProperty OwningProcess -Unique)

if (-not $pids) {
    $pattern = ":$Port\s+.*LISTENING\s+(\d+)"
    $pids = @(netstat -ano | ForEach-Object {
        if ($_ -match $pattern) {
            [int]$Matches[1]
        }
    } | Select-Object -Unique)
}

if (-not $pids) {
    Write-Host "No process is listening on port $Port."
    exit 0
}

foreach ($pidValue in $pids) {
    try {
        $proc = Get-Process -Id $pidValue -ErrorAction Stop
        Stop-Process -Id $pidValue -Force
        Write-Host "Stopped $($proc.ProcessName) PID $pidValue on port $Port."
    } catch {
        Write-Host "Could not stop PID ${pidValue}: $($_.Exception.Message)"
    }
}
