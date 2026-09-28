# © 2026 Mathew. All rights reserved.
# Tripo v2 bridge. Key: User env TRIPO_API_KEY (tsk_...). Never commit the key.
param(
    [Parameter(Position = 0)]
    [ValidateSet("doctor", "text", "image", "merrix")]
    [string]$Cmd = "doctor",
    [Parameter(Position = 1)]
    [string]$Input = "",
    [string]$Out = "",
    [string]$ModelVersion = "v2.5-20250123",
    [switch]$LowPoly,
    [int]$FaceLimit = 0,
    [switch]$Texture
)

$ErrorActionPreference = "Stop"
$Base = "https://api.tripo3d.ai/v2/openapi"
$FbxDir = "C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\fbx"
$PartsDir = "C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\parts"

function Get-Key {
    $k = [Environment]::GetEnvironmentVariable("TRIPO_API_KEY", "User")
    if (-not $k) { $k = $env:TRIPO_API_KEY }
    if (-not $k) { throw "TRIPO_API_KEY is not set." }
    return $k
}

function Get-Balance([string]$Key) {
    $raw = & curl.exe -sS -H "Authorization: Bearer $Key" "$Base/user/balance"
    return ($raw | ConvertFrom-Json)
}

function Wait-Task([string]$Key, [string]$TaskId) {
    while ($true) {
        $raw = & curl.exe -sS -H "Authorization: Bearer $Key" "$Base/task/$TaskId"
        $j = $raw | ConvertFrom-Json
        if ($j.code -ne 0) { throw $raw }
        $d = $j.data
        $st = [string]$d.status
        $pg = 0
        if ($null -ne $d.progress) { $pg = $d.progress }
        Write-Host ("  {0} {1}%" -f $st, $pg)
        if ($st -eq "success") { return $d }
        if ($st -in @("failed", "cancelled", "banned", "expired")) {
            throw ("Tripo task {0}: {1}" -f $TaskId, $st)
        }
        Start-Sleep -Seconds 3
    }
}

function Save-Model($Task, [string]$Path) {
    $url = $null
    if ($Task.output.model) { $url = $Task.output.model }
    if (-not $url -and $Task.output.pbr_model) { $url = $Task.output.pbr_model }
    if (-not $url -and $Task.result.pbr_model.url) { $url = $Task.result.pbr_model.url }
    if (-not $url -and $Task.result.model.url) { $url = $Task.result.model.url }
    if (-not $url) { throw ("no model url: {0}" -f ($Task | ConvertTo-Json -Depth 6 -Compress)) }
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    & curl.exe -sS -L $url -o $Path
    if (-not (Test-Path $Path) -or ((Get-Item $Path).Length -lt 100)) { throw "download failed $Path" }
    Write-Host "saved $Path"
}

function Send-Text([string]$Key, [string]$Prompt, [string]$Path) {
    $body = @{ type = "text_to_model"; prompt = $Prompt; model_version = $ModelVersion } | ConvertTo-Json -Compress
    $raw = & curl.exe -sS -H "Authorization: Bearer $Key" -H "Content-Type: application/json" -d $body "$Base/task"
    $j = $raw | ConvertFrom-Json
    if ($j.code -ne 0) { throw $raw }
    $tid = $j.data.task_id
    Write-Host "task $tid"
    $done = Wait-Task $Key $tid
    if (-not $Path) { $Path = Join-Path (Get-Location) "model.glb" }
    Save-Model $done $Path
}

function Send-Image([string]$Key, [string]$Img, [string]$Path, [bool]$SmartLow, [int]$Limit) {
    if (-not (Test-Path $Img)) { throw "missing image $Img" }
    $upRaw = & curl.exe -sS -H "Authorization: Bearer $Key" -F "file=@$Img" "$Base/upload"
    $up = $upRaw | ConvertFrom-Json
    $token = $up.data.image_token
    if (-not $token) { $token = $up.data.file_token }
    if (-not $token) { throw ("upload failed: {0}" -f $upRaw) }
    Write-Host "image_token $token"

    $ext = ([IO.Path]::GetExtension($Img)).TrimStart(".").ToLowerInvariant()
    if ($ext -eq "jpeg") { $ext = "jpg" }
    $fileObj = @{ type = $ext; file_token = $token }
    $payload = [ordered]@{
        type           = "image_to_model"
        file           = $fileObj
        model_version  = $ModelVersion
        texture        = [bool]$Texture
        pbr            = [bool]$Texture
    }
    if ($SmartLow) { $payload.smart_low_poly = $true }
    if ($Limit -gt 0) { $payload.face_limit = $Limit }

    $tmp = Join-Path $env:TEMP ("tripo_" + [guid]::NewGuid().ToString("N") + ".json")
    ($payload | ConvertTo-Json -Compress -Depth 5) | Set-Content -Path $tmp -Encoding UTF8
    $raw = & curl.exe -sS -H "Authorization: Bearer $Key" -H "Content-Type: application/json" --data-binary "@$tmp" "$Base/task"
    Remove-Item -Force $tmp -ErrorAction SilentlyContinue
    $j = $raw | ConvertFrom-Json
    if ($j.code -ne 0) { throw $raw }
    $tid = $j.data.task_id
    Write-Host "task $tid"
    $done = Wait-Task $Key $tid
    if (-not $Path) {
        $baseName = [IO.Path]::GetFileNameWithoutExtension($Img)
        $Path = Join-Path $FbxDir ($baseName + ".glb")
    }
    Save-Model $done $Path
}

switch ($Cmd) {
    "doctor" {
        try { $k = Get-Key } catch { Write-Host $_.Exception.Message; exit 2 }
        Write-Host "TRIPO_API_KEY set (tsk_ prefix ok)"
        try {
            $b = Get-Balance $k
            Write-Host ("balance       {0}" -f $b.data.balance)
            Write-Host ("frozen        {0}" -f $b.data.frozen)
        } catch {
            Write-Host ("balance       error {0}" -f $_.Exception.Message)
        }
        Write-Host ("parts dir     {0} exists={1}" -f $PartsDir, (Test-Path $PartsDir))
        Write-Host ("fbx dir       {0}" -f $FbxDir)
    }
    "text" {
        if (-not $Input) { throw "usage: tctl text `"a cute cat`" -Out cat.glb" }
        Send-Text (Get-Key) $Input $Out
    }
    "image" {
        if (-not $Input) { throw "usage: tctl image path.jpg -Out out.glb [-LowPoly]" }
        Send-Image (Get-Key) $Input $Out $LowPoly.IsPresent $FaceLimit
    }
    "merrix" {
        $k = Get-Key
        $b = Get-Balance $k
        if ([double]$b.data.balance -le 0) { throw "Tripo balance is 0. Add credits, then rerun merrix." }
        New-Item -ItemType Directory -Force -Path $FbxDir | Out-Null
        $jobs = @(
            @{ f = "02_hair.jpg";       o = "hair.glb";       low = $true;  lim = 5000 }
            @{ f = "10_face.jpg";       o = "face.glb";       low = $true;  lim = 5000 }
            @{ f = "16_earring.jpg";    o = "earring.glb";    low = $true;  lim = 800 }
            @{ f = "11_coat_only.jpg";  o = "coat.glb";       low = $false; lim = 80000 }
            @{ f = "12_turtleneck.jpg"; o = "turtleneck.glb"; low = $false; lim = 40000 }
            @{ f = "13_harness.jpg";    o = "harness.glb";    low = $false; lim = 30000 }
            @{ f = "14_pants.jpg";      o = "pants.glb";      low = $false; lim = 40000 }
            @{ f = "15_boots.jpg";      o = "boots.glb";      low = $false; lim = 30000 }
        )
        foreach ($j in $jobs) {
            $img = Join-Path $PartsDir $j.f
            $dest = Join-Path $FbxDir $j.o
            Write-Host ""
            Write-Host ("=== {0} -> {1} ===" -f $j.f, $j.o)
            if (-not (Test-Path $img)) { Write-Host "SKIP missing $img"; continue }
            Send-Image $k $img $dest $j.low $j.lim
        }
        Write-Host ""
        Write-Host "done. meshes in $FbxDir"
    }
}
