# Tripo bridge (Meridian)

Same job as the Blender bridge: Grok talks to Tripo without you clicking Studio.

## One-time: API key

1. Create a key at https://platform.tripo3d.ai (API Keys).
2. In **PowerShell as you** (not as admin unless you want Machine scope):

```powershell
[System.Environment]::SetEnvironmentVariable("TRIPO_API_KEY", "sk-YOUR-KEY", "User")
```

3. Close that window. Open a **new** PowerShell. Check:

```powershell
if ($env:TRIPO_API_KEY) { "key is set" } else { "key missing — new shell?" }
```

Never paste the key into chat or commit it.

## Commands

```powershell
cd C:\Users\Mathe\Meridian\tools\tripo_bridge
.\tctl.ps1 doctor
.\tctl.ps1 text "a cute cat" -Out model.glb
.\tctl.ps1 image "C:\path\to\part.jpg" -Out coat.glb
.\tctl.ps1 merrix
```

`merrix` sends the approved Stefan parts (textures **off**) into:

`Desktop\Meridian\art\characters\merrix\stefan\fbx\`
