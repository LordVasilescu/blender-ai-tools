# © 2026 Mathew. All rights reserved.
# Launch Blender OUTSIDE the AI Job Object (Scheduled Task, interactive).
param(
    [string]$Blend = "C:\Users\Mathe\Desktop\DialogueArtbar_Import\OrnateDialoguePanel.blend"
)

$ErrorActionPreference = "Stop"
$blender = "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
$boot = "C:\Users\Mathe\Meridian\tools\blender_bridge\boot_bridge_session.py"
$task = "MeridianBlenderGrok"

if (-not (Test-Path $blender)) { throw "Blender not found: $blender" }
if (-not (Test-Path $Blend)) { throw "Blend not found: $Blend" }

$arg = "`"$Blend`" --python `"$boot`""
$action = New-ScheduledTaskAction -Execute $blender -Argument $arg
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $task -Action $action -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $task
Write-Host "Started task $task"
Write-Host "Blend: $Blend"
Write-Host "Look for Blender on the taskbar."
