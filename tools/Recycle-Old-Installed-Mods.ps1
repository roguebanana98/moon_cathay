# Only inactive, individually verified files listed in the prepared inventory.
# SendToRecycleBin is required; there is no permanent-deletion fallback.
$ErrorActionPreference = 'Stop'
$cleanupRoot = 'D:\Warhammer3_Modding\moon_cathay\build\cleanup-old-mods-20261122'
$inventory = Get-Content -LiteralPath (Join-Path $cleanupRoot 'inventory.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$dataRoot = [System.IO.Path]::GetFullPath($inventory.game_data).TrimEnd('\')
$launcherHash = (Get-FileHash -LiteralPath $inventory.launcher -Algorithm SHA256).Hash
if ($launcherHash -ne $inventory.launcher_sha256) { throw 'Launcher changed; regenerate inventory before moving files.' }
if (Test-Path -LiteralPath (Join-Path $cleanupRoot 'recycle-report.json')) { throw 'Preserve completed cleanup report.' }
Add-Type -AssemblyName Microsoft.VisualBasic
$activePaths = @($inventory.active_preserved | ForEach-Object { [System.IO.Path]::GetFullPath($_.path) })
# Validate the whole exact target set before moving the first file.
foreach ($target in $inventory.targets) {
    $item = Get-Item -LiteralPath $target.path
    $resolved = (Resolve-Path -LiteralPath $target.path).ProviderPath
    if ($item.PSIsContainer -or $item.Extension -ne '.pack' -or $item.Directory.FullName -ne $dataRoot) { throw "Unexpected target: $resolved" }
    if ($resolved -ne [System.IO.Path]::GetFullPath($target.path) -or $activePaths -contains $resolved) { throw "Protected or redirected target: $resolved" }
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse target: $resolved" }
    if ($item.Length -ne $target.size -or (Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash -ne $target.sha256) { throw "File changed: $resolved" }
}
$moved = [System.Collections.Generic.List[object]]::new()
$failure = $null
try {
    foreach ($target in $inventory.targets) {
        if ((Get-FileHash -LiteralPath $inventory.launcher -Algorithm SHA256).Hash -ne $inventory.launcher_sha256) { throw 'Launcher changed during cleanup.' }
        [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile(
            $target.path,
            [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
            [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin,
            [Microsoft.VisualBasic.FileIO.UICancelOption]::ThrowException)
        if (Test-Path -LiteralPath $target.path) { throw "File still exists: $($target.path)" }
        $moved.Add([pscustomobject]@{path=$target.path;size=$target.size;sha256=$target.sha256;method='SendToRecycleBin'})
    }
    foreach ($active in $inventory.active_preserved) {
        if ((Get-FileHash -LiteralPath $active.path -Algorithm SHA256).Hash -ne $active.sha256) { throw "Active mod changed: $($active.path)" }
    }
} catch { $failure = $_.Exception.Message }
$report = [ordered]@{status=$(if ($failure) {'partial_failure'} else {'recycled'});moved=@($moved.ToArray());count=$moved.Count;failure=$failure;permanent_delete_used=$false;active_preserved=$inventory.active_preserved;launcher_not_modified=$true}
[System.IO.File]::WriteAllText((Join-Path $cleanupRoot 'recycle-report.json'), ($report | ConvertTo-Json -Depth 12), [System.Text.UTF8Encoding]::new($false))
if ($failure) { throw $failure }
Write-Output "Sent $($moved.Count) old installed mod files to Recycle Bin."
