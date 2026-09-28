# © 2026 Mathew. All rights reserved.
# Blender bridge control — same idea as uectl.
param(
    [Parameter(Position = 0)]
    [ValidateSet("status", "up", "send", "ping", "doctor")]
    [string]$Cmd = "status",
    [string]$Blend = "C:\Users\Mathe\Desktop\DialogueArtbar_Import\OrnateDialoguePanel.blend",
    [string]$File = "",
    [string]$Name = "job"
)

$Root = "C:\Users\Mathe\Meridian\tools\blender_bridge"
$Status = Join-Path $Root "status.json"
$Inbox = Join-Path $Root "inbox"
$Outbox = Join-Path $Root "outbox"

function Read-Status {
    if (-not (Test-Path $Status)) { return $null }
    return Get-Content $Status -Raw | ConvertFrom-Json
}

function Test-Alive($st) {
    if ($null -eq $st) { return $false }
    $procs = @(Get-Process blender -ErrorAction SilentlyContinue)
    if ($procs.Count -eq 0) { return $false }
    try {
        $t = [datetime]::Parse($st.time)
        $age = (Get-Date) - $t
        return $age.TotalSeconds -lt 12
    } catch {
        return $false
    }
}

switch ($Cmd) {
    "status" {
        $st = Read-Status
        $alive = Test-Alive $st
        if ($null -eq $st) {
            Write-Host "status_file missing"
            Write-Host "alive False"
            exit 1
        }
        Write-Host ("state   {0}" -f $st.state)
        Write-Host ("alive   {0}" -f $alive)
        Write-Host ("blend   {0}" -f $st.blend)
        Write-Host ("objects {0}" -f $st.objects)
        Write-Host ("job     {0}" -f $st.last_job)
        Write-Host ("time    {0}" -f $st.time)
        Write-Host ("pid     {0}" -f $st.pid)
        if (-not $alive) { exit 2 }
    }
    "up" {
        & (Join-Path $Root "start_blender_bridge.ps1") -Blend $Blend
    }
    "send" {
        if (-not (Test-Path $File)) { throw "missing File $File" }
        $dest = Join-Path $Inbox ("{0}.py" -f $Name)
        Copy-Item -Force $File $dest
        Write-Host "queued $dest"
    }
    "ping" {
        $py = "import bpy`r`nprint('PONG', bpy.data.filepath, 'objs', len(bpy.data.objects))`r`n"
        $tmp = Join-Path $Inbox "ping.py"
        Set-Content -Path $tmp -Value $py -Encoding UTF8
        Write-Host "queued ping"
    }
    "doctor" {
        Write-Host "blender exe" (Test-Path "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe")
        Write-Host "blend file" (Test-Path $Blend)
        Write-Host "addon 4.4" (Test-Path "$env:APPDATA\Blender Foundation\Blender\4.4\scripts\addons\meridian_blender_bridge\__init__.py")
        $st = Read-Status
        Write-Host "status exists" ($null -ne $st)
        if ($st) { $st | ConvertTo-Json -Compress }
        Write-Host "blender processes"
        Get-Process blender -ErrorAction SilentlyContinue | Format-Table Id, MainWindowTitle
        Write-Host "inbox files"
        Get-ChildItem $Inbox -ErrorAction SilentlyContinue | Select-Object Name
        Write-Host "outbox files"
        Get-ChildItem $Outbox -ErrorAction SilentlyContinue | Select-Object Name
    }
}
