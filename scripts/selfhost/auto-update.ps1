# Glimmervoid auto-update: keeps the running container in sync with main.
# Rebuilds when either the remote HEAD has moved OR the running container was
# built from a different commit than the current HEAD (handles manual pulls).
#
# Usage:
#   .\auto-update.ps1                    # use defaults
#   .\auto-update.ps1 -Port 9090         # override port
#   .\auto-update.ps1 -ContainerName foo # override container name
#   .\auto-update.ps1 -Force             # rebuild even if commits match
#
# Exit codes: 0 = no-op or success, 1 = failure (logged).

param(
    [string]$ContainerName = "glimmervoid",
    [string]$ImageTag      = "glimmervoid",
    [int]   $Port          = 8080,
    [string]$Branch        = "main",
    [string]$LogFile       = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

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

function Get-DeployedCommit {
    param([string]$Container)
    $id = docker ps -a --filter "name=^/$Container$" --format "{{.ID}}" 2>$null
    if (-not $id) { return $null }
    $raw = docker inspect $Container 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { return "unknown" }
    try {
        $info = $raw | ConvertFrom-Json
        $sha = $info[0].Config.Labels.'glimmervoid.commit'
        if (-not $sha) { return "unknown" }
        return $sha.Trim()
    } catch {
        return "unknown"
    }
}

function Invoke-Rebuild {
    param([string]$TargetCommit)

    Write-Log "Building image '$ImageTag' (commit=$TargetCommit)."
    docker build `
        --label "glimmervoid.commit=$TargetCommit" `
        -t $ImageTag $RepoRoot 2>&1 | ForEach-Object { Write-Log $_ "BUILD" }
    if ($LASTEXITCODE -ne 0) { throw "docker build failed (exit $LASTEXITCODE)" }

    $existing = docker ps -a --filter "name=^/$ContainerName$" --format "{{.ID}}"
    if ($existing) {
        Write-Log "Stopping/removing existing container '$ContainerName'."
        docker stop $ContainerName | Out-Null
        docker rm   $ContainerName | Out-Null
    }

    Write-Log "Starting new container on port $Port."
    docker run -d `
        -p "${Port}:8080" `
        --name $ContainerName `
        --restart unless-stopped `
        --label "glimmervoid.commit=$TargetCommit" `
        $ImageTag | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "docker run failed (exit $LASTEXITCODE)" }

    Write-Log "Update completed successfully (now at $TargetCommit)."
}

try {
    Write-Log "Check started (repo=$RepoRoot, branch=$Branch)"
    Set-Location $RepoRoot

    git fetch origin $Branch --quiet
    $localHead  = (git rev-parse HEAD).Trim()
    $remoteHead = (git rev-parse "origin/$Branch").Trim()

    if ($localHead -ne $remoteHead) {
        Write-Log "Pulling $localHead -> $remoteHead."
        git pull --ff-only origin $Branch | Out-Null
        $localHead = (git rev-parse HEAD).Trim()
    }

    $deployed = Get-DeployedCommit -Container $ContainerName
    if (-not $Force -and $deployed -eq $localHead) {
        Write-Log "Container already at $localHead. Skipping."
        exit 0
    }

    if ($Force) {
        Write-Log "Force rebuild requested."
    } elseif (-not $deployed) {
        Write-Log "No existing container. Building from $localHead."
    } else {
        Write-Log "Container drift: deployed=$deployed, target=$localHead."
    }

    Invoke-Rebuild -TargetCommit $localHead
    exit 0
}
catch {
    Write-Log $_.Exception.Message "ERROR"
    exit 1
}
