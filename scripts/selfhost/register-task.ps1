# Registers the Glimmervoid auto-update script as a Windows Scheduled Task
# that runs every 2 minutes in the background.
#
# Run once, as Administrator:
#   powershell -ExecutionPolicy Bypass -File .\register-task.ps1
#
# To unregister:
#   Unregister-ScheduledTask -TaskName "Glimmervoid AutoUpdate" -Confirm:$false

param(
    [string]$TaskName       = "Glimmervoid AutoUpdate",
    [int]   $IntervalMinutes = 2
)

$ErrorActionPreference = "Stop"

$ScriptPath = Join-Path $PSScriptRoot "auto-update.ps1"
if (-not (Test-Path $ScriptPath)) {
    throw "auto-update.ps1 not found at $ScriptPath"
}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`""

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType S4U `
    -RunLevel Highest

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "Task '$TaskName' already exists. Updating."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Pulls main and rebuilds the Glimmervoid Docker container when the remote moves."

Write-Host ""
Write-Host "Registered '$TaskName' (every $IntervalMinutes min)."
Write-Host "Log file: <repo>\auto-update.log"
Write-Host "First run: in ~1 minute."
