# Glimmervoid auto-update: pulls main, rebuilds Docker image and restarts container
# only if the remote HEAD has moved. Designed to be invoked by Task Scheduler.
#
# Usage:
#   .\auto-update.ps1                    # use defaults
#   .\auto-update.ps1 -Port 9090         # override port
#   .\auto-update.ps1 -ContainerName foo # override container name
#
# Exit codes: 0 = no-op or success, 1 = failure (logged).

param(
    [string]$ContainerName = "glimmervoid",
    [string]$ImageTag      = "glimmervoid",
    [int]   $Port          = 8080,
    [string]$Branch        = "main",
    [string]$LogFile       = ""
)

$ErrorActionPreference = "Stop"

# Resolve repo root from script location: <repo>\scripts\selfhost\auto-update.ps1
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
if (-not $LogFile) {
    $LogFile = Join-Path $RepoRoot "auto-update.log"
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [$Level] $Message"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

try {
    Write-Log "Check started (repo=$RepoRoot, branch=$Branch)"
    Set-Location $RepoRoot

    $before = (git rev-parse HEAD).Trim()
    git fetch origin $Branch --quiet
    $remote = (git rev-parse "origin/$Branch").Trim()

    if ($before -eq $remote) {
        Write-Log "No new commits (HEAD=$before). Skipping."
        exit 0
    }

    Write-Log "Update available: $before -> $remote. Pulling."
    git pull --ff-only origin $Branch | Out-Null

    Write-Log "Building image '$ImageTag'."
    docker build -t $ImageTag $RepoRoot 2>&1 | ForEach-Object { Write-Log $_ "BUILD" }
    if ($LASTEXITCODE -ne 0) { throw "docker build failed (exit $LASTEXITCODE)" }

    $existing = docker ps -a --filter "name=^/$ContainerName$" --format "{{.ID}}"
    if ($existing) {
        Write-Log "Stopping/removing existing container '$ContainerName'."
        docker stop $ContainerName | Out-Null
        docker rm   $ContainerName | Out-Null
    }

    Write-Log "Starting new container on port $Port."
    docker run -d -p "${Port}:8080" --name $ContainerName --restart unless-stopped $ImageTag | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "docker run failed (exit $LASTEXITCODE)" }

    Write-Log "Update completed successfully (now at $remote)."
    exit 0
}
catch {
    Write-Log $_.Exception.Message "ERROR"
    exit 1
}
