$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$baseline = Get-Content -LiteralPath (Join-Path $root 'reports/dependency-fingerprints.json') -Raw | ConvertFrom-Json
foreach ($item in $baseline) {
    $actual = Get-FileHash -LiteralPath $item.path -Algorithm SHA256
    if ($actual.Hash -ne $item.sha256) { throw "Dependency changed: $($item.path). Re-run analysis before building." }
    Write-Output "SHA256 unchanged: $($item.path)"
}
